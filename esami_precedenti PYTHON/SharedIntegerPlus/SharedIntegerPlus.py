#!/usr/bin/env python
from threading import Thread,Condition,RLock,get_ident
from typing import Type

class IllegalMonitorStateException(Exception):
    pass

'''
#
# Note sull'implementazione
#
#
# Lo shared integer presenta come unica difficoltà di implementazione il fatto che alcuni metodi (inc e setInTheFuture) modificano o leggono DUE sharedInteger
# CONTEMPORANEAMENTE.
#
# Per evitare deadlock e race condition insieme, si usano due classi molto utili:
#
# FriendlyLock: consente di fare acquire in contemporanea con un altro FriendlyLock 'amico', stando automaticamente attento a non creare deadlock
# usando il trucco dell'ordine lessicografico
#
# FriendlyCondition: una normale condition consente di andare in wait rilasciando solo il lock di appartenenza, ma non altri eventuali lock che si possiede;
# le FriendlyCondition consentono di fare wait() liberando tutti insieme un insieme di FriendlyLock. All'uscita della wait, tutti i friendlylock "amici" vengono riacquisiti.
#
# Grazie a FriendlyLock l'implementazione di inc diventa molto semplice, mentre invece FriendlyCondition ci aiuta a realizzare setInTheFuture in cui è necessario 
# attendere che cambi un certo intero per poi modificarne un secondo
#
'''
#
# Lock interno usato da tutti i friendlyLock e da tutte le friendlyCondition
# 
globalInternalLock = RLock()

#
# Per gestire al meglio i punti 3, 4 e 5, estendiamo il FriendlyLock con la possibilità  di avere 
# tanti lock amici (non più uno solo)
#
class FriendlyLock:
#(Lock): non è stato possibile ereditare da Lock poichè non si possono ereditare le classi builtin

    #
    # Contatore statico che vale per tutte le istanze di classe. Usato per disciplinare l'ordine di acquire contemporanee
    #
    internalSerialCounter = 0

    def __init__(self):
        super(FriendlyLock, self).__init__()
        self.taken = False
        self.internalLock = globalInternalLock
        self.internalCondition = Condition(self.internalLock)
        #
        # Assegna un numero progressivo diverso a ogni FriendlyLock
        #
        FriendlyLock.internalSerialCounter += 1
        self.serial = FriendlyLock.internalSerialCounter
        #
        # ID del thread che attualmente possiede il lock
        #
        self.currentHolder = None
        #
        # Numero di volte che il possessore del lock ha fatto acquire(). Per ogni acquire() deve esserci una corrispondente release()
        #
        self.holds = 0

    #
    #  SOLUZIONE: usato per ordinare i lock
    #
    def __lt__(self, other):
        return self.serial < other.serial


    def acquire(self, l  = None):
        # 
        # 	Se l != None, consente di prendere due FriendlyLock insieme nell'ordine anti-deadlock
        #
        if type(l) == FriendlyLock:
            if self.serial < l.serial:
                self.acquire()
                l.acquire()
            else:
                l.acquire()
                self.acquire()
        elif type(l) == list:
            #
            # Aggiungo il lock corrente a tutti gli altri, perchè deve anche esso rispettare l'ordine
            # 
            l.append(self)
            for lk in sorted(l):
                lk.acquire()
        #
        # Non c'è l oppure l è del tipo sbagliato, simula il comportamento di una normale acquire
        #
        else:
            self.internalLock.acquire()
            while self.currentHolder != None and self.currentHolder != get_ident():
                    self.internalCondition.wait()
            self.currentHolder = get_ident()
            # 
            #  Conta eventuali lock multipli per garantire la rientranza
            # 
            self.holds += 1
            self.internalLock.release()

    # 
    #  se il parametro l è presente, rilascia due lock insieme. Notare che qui l'ordine di rilascio non è importante
    #             
    def release(self, l  = None):
        if type(l) == FriendlyLock:
            self.release()
            l.release()
        elif type(l) == list:
            self.release()
            #
            # L'ordine di release non necessita sorting
            #
            for lk in l:
                lk.release()
        else:
            self.internalLock.acquire()
            try:
                if self.currentHolder == get_ident():
                    self.holds -= 1
                    if self.holds == 0:
                        self.currentHolder = None
                        self.internalCondition.notify()
                else:
                    # 
                    #  Non puoi rilasciare un lock che non appartiene al thread corrente (get_ident())
                    # 
                    raise IllegalMonitorStateException()
            finally:
                self.internalLock.release()

#
# Una friendlyCondition può avere più di un lock collegato, i quali vengono liberati tutti in caso di wait, e ripresi alla fine dell'attesa
#
class FriendlyCondition:
#(Condition): non è stato possibile ereditare da Condition poichè non si possono ereditare le classi builtin

    def __init__(self, l):
        super(FriendlyCondition, self).__init__()
        #
        # Insieme dei lock collegati
        #
        self.joinedLocks = list()
        #
        # Bisogna dichiarare almeno un lock collegati che viene subito messo tra i joinedLock
        #
        self.joinedLocks.append(l)
        #
        # Lock interno usato per disciplinare l'accesso alle variabili interne
        #
        self.internalLock = globalInternalLock
        #
        # Useremo delle condition interne per simulare wait e notify. Ogni thread in wait avrà  una sua condition separata. Ne terremo traccia qui dentro
        #
        self.internalConditions = list()

#
# Aggiunge un lock all'insieme dei collegati
#
    def join(self, l):
        self.internalLock.acquire()
        self.joinedLocks.append(l)
        self.internalLock.release()

#
# Scollega un certo lock che prima era collegato
#
    def unjoin(self, l : FriendlyLock):
        self.internalLock.acquire()
        self.joinedLocks.remove(l)
        self.internalLock.release()

    #
    # Per implementare wait e notify, creo ogni volta una condition usa e getta che verrà  usata per fare wait() e buttata alla prima notify().
    # 
    # Tutti i lock amici di questa Friendly condition vengo rilasciati temporaneamente e riacquisiti dopo la wait
    #
    def wait(self):
        self.internalLock.acquire()
        for i in self.joinedLocks:
            i.release()
        myCondition = Condition(self.internalLock)
        self.internalConditions.append(myCondition)
        # 
        #   Qui non uso un while di controllo. Come per le Condition native
        # 	Anche la FriendlyCondition sarà  soggetta agli spurious wake-up.
        #   Gli spurious wake-up andranno gestiti dal programmatore
        #   che usa le FriendlyCondition
        # 
        myCondition.wait()
        #
        # Riprendo tutti i lock collegati che avevo lasciato
        #
        for i in self.joinedLocks:
            i.acquire()
        self.internalLock.release()

    def notify(self):
        self.internalLock.acquire()
        toDelete = None
        for cond in self.internalConditions:
            # 
            #  Prendo solo la prima condition da notificare (questa non è notifyAll), faccio signal e poi faccio break;
            # 
            cond.notify()
            toDelete = cond
            break
        self.internalConditions.remove(toDelete)
        self.internalLock.release()

#
# In notifyAll devo considerare tutti i thread che potrebbero avere usato wait e sono in attesa. Per ciascuno ci sarà  una condition dentro internalCondition.
# Faccio notify su tutte e pulisco il set di internalConditions perchè non mi servono più.
#
    def notifyAll(self):
        self.internalLock.acquire()
        for cond in self.internalConditions:
            cond.notify()
        self.internalConditions = list()
        self.internalLock.release()

    def notify(self):
        self.internalLock.acquire()
        toDelete = None
        for cond in self.internalConditions:
            # 
            #  Prendo solo la prima condition da notificare (questa non è notifyAll), faccio notify, cancello la condition e poi faccio break;
            # 
            cond.notify()
            toDelete = cond
            break
        self.internalConditions.remove(toDelete)
        self.internalLock.release()


#
# La classe Attesa mi serve per implementare gli SharedInteger e in particolare gestire tutti i thread che attendono il superamento di specifiche soglie.
# Ogni attesa corrisponde a una soglia fissata, e corrisponde a una Condition che è quella su cui fare notify per svegliare il thread corrispondente.
#
class Attesa:
    serialCounter = 0

    def __init__(self, i, c):
        #
        # Condition da notificare in futuro a superamento della soglia
        #
        self.c = c
        self.soglia = i
        Attesa.serialCounter += 1
        self.serial = Attesa.serialCounter

    # 
    #  Le attese sono ordinate dal valore piu' basso al più alto. 
    #  A parita' di valore vince l'elemento col seriale più basso. 
    #  sorted e sort usano __lt__ per comparare gli elementi
    # 
    def __lt__(self, other):
        return self.soglia < other.soglia if self.soglia != other.soglia else self.serial < other.serial


class SharedInteger(object):

    def __init__(self):
        self.value = 0
        #
        # Non avendo a disposizione un SortedSet di serie in Python, invocheremo self.attese.sort() alla bisogna.
        # Così facendo self.attese sarà  sempre ordinato.
        #
        #self.attese = list()
        #
        # Punti 2 e 4: siccome adesso è necessario attendere anche quando uno SharedInteger SCENDE sotto un certo valore
        # Introduciamo due tipi di attesa, quelle "in salita" e quelle "in discesa"
        self.atteseInSalita = list()    # rimpiazza il vecchio self.attese. Viene mantenuto ordinato per valori crescenti
        self.atteseInDiscesa = list()   # nuovo. Viene mantenuto ordinato per valori decrescenti

        # Qui sfrutteremo il FriendlyLock implementato sopra
        #
        self.lock = FriendlyLock()

    #
    # Fa notify su tutti gli eventuali thread in attesa di superamento soglia
    #
    #
    # Modificato con i nuovi due tipi di attesa
    #
    def signalWaiters(self):
        for a in self.atteseInSalita:
            if self.value > a.soglia:
                a.c.notifyAll()
            else:
                # 
                #  Siccome le atteseInSalita (ex self.attese) sono ordinate dalla soglia più bassa alla più alta, mi fermo alla prima non superata da value. 
                #  Le soglie successive non saranno sicuramente superate.
                # 
                break
        for a in self.atteseInDiscesa:
            if self.value < a.soglia:
                a.c.notifyAll()
            else:
                # 
                #  Siccome le atteseInDiscesa sono ordinate dalla soglia più alta alla più bassa, mi fermo alla prima non superata da value. 
                #  Le soglie successive non saranno sicuramente superate.
                # 
                break

#
# NOTATE CHE il FriendlyLock somiglia a un Lock nativo come interfaccia ma NON implementa il costrutto "with:"
# 
    def get(self):
        self.lock.acquire()
        try:
            return self.value
        finally:
            self.lock.release()
#
# set, inc, oppure inc_int potrebbero far andare un intero sopra o sotto delle soglie su cui qualcuno aspetta
#
    def set(self, i):
        self.lock.acquire()
        self.value = i
        self.signalWaiters()
        self.lock.release()

    def inc(self, I):
        self.lock.acquire(I.lock)
        self.value += I.value
        self.signalWaiters()
        self.lock.release(I.lock)

    def inc_int(self, i : int):
        self.lock.acquire()
        self.value += i
        self.signalWaiters()
        self.lock.release()

    def waitForAtLeast(self, soglia):
        self.lock.acquire()
        try:
            cond = FriendlyCondition(self.lock)
            att = Attesa(soglia, cond)
            #
            # Modificato con nuovo nome
            #
            self.atteseInSalita.append(att)
            self.atteseInSalita = sorted(self.atteseInSalita)
            while self.value < soglia:
                cond.wait()
            self.atteseInSalita.remove(att)
            return self.value
        finally:
            self.lock.release()

    def setInTheFuture(self, I, soglia, valore):
        self.lock.acquire(I.lock)
        cond = FriendlyCondition(self.lock)
        cond.join(I.lock)
        att = Attesa(soglia, cond)
        # 
        #  Non dimentichiamo che sto aspettando il cambiamendo del valore di I, non di self
        #  Tuttavia non POSSO usare I.waitForAtLeast(soglia) poichè non potrei in contemporanea bloccare il lock su self.
        #
        #  Lo spezzone di codice
        #       I.waitForAtLeast(soglia)
        #       self.set(valore)
        #
        # Contiene una RACE CONDITION che non mi da la garanzia che I sia maggiore di soglia all'atto della self.set(valore)
        # 
        # Il problema si risolve usando un FriendlyLock insieme a una FriendlyCondition
        # 
        I.atteseInSalita.append(att)
        self.atteseInSalita = sorted(self.atteseInSalita)
        while I.value < soglia:
            cond.wait()
        I.atteseInSalita.remove(att)
        self.value = valore
        self.signalWaiters()
        self.lock.release(I.lock)

    #
    # Punto 1 soluzione
    #
    def sposta_int(self,I2, n : int):
        self.lock.acquire(I2.lock)
        self.value-=n
        I2.value+=n
        self.signalWaiters()
        I2.signalWaiters()
        self.lock.release(I2.lock)
    #
    # Punto 2 soluzione
    #
    def waitAndBalance_int(self,I2,n:int):
        self.lock.acquire(I2.lock)
        cond=FriendlyCondition(self.lock)
        cond.join(I2.lock)
        att = Attesa(n, cond)
        self.atteseInDiscesa.append(att)
        self.atteseInDiscesa = sorted(self.atteseInDiscesa,reverse=True)
        while self.value >= n:
            cond.wait()
        self.atteseInDiscesa.remove(att)
        self.value = I2.value= (self.value+I2.value)//2
        self.signalWaiters()
        I2.signalWaiters()
        self.lock.release(I2.lock)

    #
    # Punto 3 soluzione. Sfrutteremo il FriendlyLock esteso
    #
    def sposta(self,I2,I3):
        self.lock.acquire([I2.lock,I3.lock])
        self.sposta_int(I2,I3.get())
        self.lock.release([I2.lock,I3.lock])

    #
    # Punto 4. Anche qui il FriendlyLock esteso è utilissimo
    #
    def waitAndBalance(self,I2,I3):
        self.lock.acquire([I2.lock,I3.lock])
        #
        #  Si userà  il valore di I3 letto *prima dell'attesa*
        #
        self.waitAndBalance_int(I2,I3.get())
        self.lock.release([I2.lock,I3.lock])

    #
    # Punto 5. 
    #
    def somma(self,A : list):
        L = [I.lock for I in A]
        self.lock.acquire(L)
        sum = 0
        for I in A:
            sum += I.get()
        self.lock.release(L)


print("STARTING MAIN\n")
a = SharedInteger()
b = SharedInteger()
a.set(500)
b.set(1000)

class Thread1(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print(f"A ora vale: {a.get()}\n")
        print(f"sono il thread {self.name} e imposterà B a 5001 quando A supererà  999\n")
        b.setInTheFuture(a, 999, 5001)
        print(f"A è ora: {a.get()}\n")
        print(f"B è ora: {b.get()}\n")

class Thread2(Thread):

		
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        conta = 0
        for i in range(0,500):
            a.inc_int(1)
            print("+", end='')
            conta += 1
            if conta > 50:
                print()
                conta = 0
                print(f"\nA vale ora: {a.get()}\n")
        print("\n")
        print(f"Sono il Thread {self.name} e ora aspetterà che B sia 5000. In questo momento B è: {b.get()}\n")
        b.waitForAtLeast(5000)
        print(f"Aspettato B, che adesso vale: {b.get()}\n")


class Thread3_1(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.name = "Thread3_1"
    def run(self):
        print(f"{self.name}: Thread 3_1\n")
        
        print(f"{self.name}: wait b >= 1020\n")
        b.waitForAtLeast(1020)
        a.sposta_int(b,300)
        a.sposta(b,c)
        
        print(f"{self.name}: Exit A:{a.get()}, B:{b.get()}\n")

class Thread4(Thread):

		
    def __init__(self):
        Thread.__init__(self)
        self.name = "Thread4"

    def run(self):
        print(f"{self.name}: Thread 4\n")

        conta=0
        for i in range(0,100):
            if conta>=20:
                print(f"{self.name}: A:{a.get()}, B:{b.get()}\n")
            
            b.inc_int(1)
            if conta>=20:
                print(f"{self.name}: A:{a.get()}, B:{b.get()}\n")
                conta=0
            conta+=1
        a.waitAndBalance_int(b,201)
        print(f"{self.name}: A:{a.get()}, B:{b.get()}\n")
        c.set(801)
        a.waitAndBalance(b,c)
        print(f"{self.name}: A:{a.get()}, B:{b.get()}\n")
        

print("STARTING MAIN\n")
a = SharedInteger()
b = SharedInteger()
c = SharedInteger()
a.set(500)
b.set(1000)
c.set(100)


print("STARTING THREADS\n")
print(f"lock a: {a.lock.serial}\n")
print(f"lock b: {b.lock.serial}\n")
#Thread3().start()
Thread3_1().start()
Thread4().start()
print("MAIN STARTED\n")

