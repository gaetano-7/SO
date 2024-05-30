from threading import Thread,Condition,RLock,get_ident
import random
import time

class IllegalMonitorStateException(Exception):
    pass

'''
#
# Note sull'implementazione
#
#
# Lo shared integer presenta come unica difficoltÃ  di implementazione il fatto che alcuni metodi (inc e setInTheFuture) modificano o leggono DUE sharedInteger
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
# Grazie a FriendlyLock l'implementazione di inc diventa molto semplice, mentre invece FriendlyCondition ci aiuta a realizzare setInTheFuture in cui Ã¨ necessario 
# attendere che cambi un certo intero per poi modificarne un secondo
#
'''
#
# Lock interno usato da tutti i friendlyLock e da tutte le friendlyCondition
# 

'''
Punto 1:
Si estenda la classe SharedInteger con il metodo sposta_int(I2 : SharedInteger, n : int).
Tale metodo effettua in maniera thread-safe le due operazioni self.value -= n, I2.value +=n
Si aggiunga inoltre del codice di testing del metodo introdotto.

Punto 2:
Si estenda la classe SharedInteger con il metodo waitAndBalance_int(I2 : SharedInteger,n :
int)
Tale metodo si mette in attesa bloccante se self.value >= n. Qualora il valore di self dovesse scendere sotto n,
pone, in maniera thread-safe, self.value = I2.value = (self.value+I2.value)/2
Si aggiunga inoltre del codice di testing del metodo introdotto.

Punto 3:
Si estenda la classe SharedInteger con il metodo sposta(I2 : SharedInteger, I3 :
SharedInteger).
Tale metodo effettua in maniera thread-safe le due operazioni self.value -= I3.value, I2.value +=
I3.value
Si aggiunga inoltre del codice di testing del metodo introdotto.

Punto 4:
Si implementi il metodo waitAndBalance(I2 : SharedInteger, I3 : SharedInteger)
Il metodo si comporta come il metodo al punto 2, ma il valore di n è sostituito da I3.value .

Punto 5:
Si implementi la funzione somma(A : list[SharedInteger]) -> int
Tale funzione restituisce in maniera thread safe la somma di tutti gli SharedInteger presenti nell array A
'''

globalInternalLock = RLock()

class FriendlyLock:
#(Lock): non Ã¨ stato possibile ereditare da Lock poichÃ¨ non si possono ereditare le classi builtin

    #
    # Contatore statico che vale per tutte le istanze di classe. Usato per disciplinare l'ordine di acquire contemporanee
    #
    internalSerialCounter = 0

    def __init__(self):
        super(FriendlyLock, self).__init__()
        # self.taken = False
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
        #
        # Non c'Ã¨ l oppure l Ã¨ del tipo sbagliato, simula il comportamento di una normale acquire
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
    #  se il parametro l Ã¨ presente, rilascia due lock insieme. Notare che qui l'ordine di rilascio non Ã¨ importante
    #             
    def release(self, l  = None):
        if type(l) == FriendlyLock:
            self.release()
            l.release()
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
# Una friendlyCondition puÃ² avere piÃ¹ di un lock collegato, i quali vengono liberati tutti in caso di wait, e ripresi alla fine dell'attesa
#
class FriendlyCondition:
#(Condition): non Ã¨ stato possibile ereditare da Condition poichÃ¨ non si possono ereditare le classi builtin

    def __init__(self, l):
        super(FriendlyCondition, self).__init__()
        #
        # Insieme dei lock collegati
        #
        self.joinedLocks = list()
        #
        # Bisogna dichiarare almeno un lock collegato che viene subito messo tra i joinedLock
        #
        self.joinedLocks.append(l)
        #
        # Lock interno usato per disciplinare l'accesso alle variabili interne
        #
        self.internalLock = globalInternalLock
        #
        # Useremo delle condition interne per simulare wait e notify. Ogni thread in wait avrÃ  una sua condition separata. Ne terremo traccia qui dentro
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
    # Per implementare wait e notify, creo ogni volta una condition usa e getta che verrÃ  usata per fare wait() e buttata alla prima notify().
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
        # 	AnchÃ¨ la FriendlyCondition sarÃ  soggetta agli spurious wake-up.
        #   Gli spurious wake-up andranno gestiti dal programmatore
        #   che usa le FriendlyCondition
        # 
        myCondition.wait()
        #
        # Riprendo tutti i lock collegati che avevo lasciato
        #
        # Hint: ordinare i lock prima di acquisirli.
        for i in self.joinedLocks:
            i.acquire()
        self.internalLock.release()

    def notify(self):
        self.internalLock.acquire()
        toDelete = None
        for cond in self.internalConditions:
            # 
            #  Prendo solo la prima condition da notificare (questa non Ã¨ notifyAll), faccio signal e poi faccio break;
            # 
            cond.notify()
            toDelete = cond
            break
        if toDelete != None:
            self.internalConditions.remove(toDelete)
        self.internalLock.release()

#
# In notifyAll devo considerare tutti i thread che potrebbero avere usato wait e sono in attesa. Per ciascuno ci sarÃ  una condition dentro internalCondition.
# Faccio notify su tutte e pulisco il set di internalConditions perchÃ¨ non mi servono piÃ¹.
#
    def notifyAll(self):
        self.internalLock.acquire()
        for cond in self.internalConditions:
            cond.notify()
        self.internalConditions = list()
        self.internalLock.release()

#
# La classe Attesa mi serve per implementare gli SharedInteger e in particolare gestire tutti i thread che attendono il superamento di specifiche soglie.
# Ogni attesa corrisponde a una soglia fissata, e corrisponde a una Condition che Ã¨ quella su cui fare notify per svegliare il thread corrispondente.
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
    #  Le attese sono ordinate dal valore piu' basso al piÃ¹ alto. 
    #  A parita' di valore vince l'elemento col seriale piÃ¹ basso.
    # 
    def __lt__(self, other):
        return self.soglia < other.soglia if self.soglia != other.soglia else self.serial < other.serial



class SharedInteger(object):

    def __init__(self):
        self.value = 0
        #
        # Non avendo a disposizione un SortedSet di serie in Python, invocheremo self.attese.sort() alla bisogna.
        # CosÃ¬ facendo self.attese sarÃ  sempre ordinato.
        #
        self.attese = list()
        #
        # Qui sfrutteremo il FriendlyLock implementato sopra
        #
        self.lock = FriendlyLock()
        self.cond = FriendlyCondition(self.lock)

    #
    # Fa notify su tutti gli eventuali thread in attesa di superamento soglia
    #

    def signalWaiters(self):
        for a in self.attese:
            if self.value >= a.soglia:
                a.c.notifyAll()
            else:
                # 
                #  Siccome le attese sono ordinate dalla soglia piÃ¹ bassa alla piÃ¹ alta, mi fermo alla prima non superata da value. 
                #  Le soglie successive non saranno sicuramente superate.
                # 
                break

    def sposta_int(self, I2 : 'SharedInteger', n : int):
        self.lock.acquire()
        try:
            self.value -= n
            I2.value += n
            self.cond.notifyAll()
            print("OPERAZIONI EFFETTUATE\n")
        finally:
            self.lock.release()

    def waitAndBalance(self, I2 : 'SharedInteger', n : int):
        self.lock.acquire()
        #cond = FriendlyCondition(self.lock)
        try:
            while self.value >= n: 
                print(f"SONO IN WAIT: value = {self.value} / n = {n}\n")
                self.cond.wait()
            self.value = I2.value = (self.value + I2.value)/2
            print("MODIFICATO E USCITO DAL WAIT\n")
        finally:
            self.lock.release()

    def sposta(self, I2 : 'SharedInteger', I3 : 'SharedInteger'):
        self.lock.acquire()
        try:
            self.value -= I3.value
            I2.value += I3.value
            self.cond.notifyAll()
            I2.cond.notifyAll()
            I3.cond.notifyAll()
            print("TUTTO ALLA GRANDE\n")
        finally:
            self.lock.release()

    def waitAndBalance2(self, I2 : 'SharedInteger', I3 : 'SharedInteger'):
        self.lock.acquire()
        #cond = FriendlyCondition(self.lock)
        try:
            while self.value >= I3.value: 
                print(f"SONO IN WAIT: value = {self.value} / I3.value = {I3.value}\n")
                self.cond.wait()
            self.value = I2.value = (self.value + I2.value)/2
            print("MODIFICATO E USCITO DAL WAIT2\n")
        finally:
            self.lock.release()

    def somma(self, A : list['SharedInteger']) -> int:
        self.lock.acquire()
        try:
            somma = 0
            for i in range(len(A)):
                somma += A[i].value
            return somma
        finally:
            self.lock.release()

                


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
# set, inc, oppure inc_int potrebbero far superare delle soglie su cui qualcuno aspetta
#
    def set(self, i):
        self.lock.acquire()
        self.value = i
        #print(f"SETTO A {self.value}")
        self.cond.notifyAll()
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
            self.attese.append(att)
            self.attese = sorted(self.attese)
            while self.value < soglia:
                cond.wait()
            self.attese.remove(att)
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
        #  Tuttavia non POSSO usare I.waitForAtLeast(soglia) poichÃ¨ non potrei in contemporanea bloccare il lock su self.
        #
        #  Lo spezzone di codice
        #       I.waitForAtLeast(soglia)
        #       self.set(valore)
        #
        # Contiene una RACE CONDITION che non mi da la garanzia che I sia maggiore di soglia all'atto della self.set(valore)
        # 
        # Il problema si risolve usando un FriendlyLock insieme a una FriendlyCondition
        # 
        I.attese.append(att)
        I.attese = sorted(I.attese)
        while I.value < soglia:
            cond.wait()
        I.attese.remove(att)
        self.value = valore
        self.signalWaiters()
        self.lock.release(I.lock)

print("STARTING MAIN")
a = SharedInteger()
b = SharedInteger()
c = SharedInteger()
a.set(500)
b.set(1000)
c.set(800)

class Thread1(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print(f"A ora vale: {a.get()}")
        print(f"sono il thread {get_ident()} e imposterÃ² B a 5001 quando A supererÃ  999")
        b.setInTheFuture(a, 999, 5001)
        print(f"A Ã¨ ora: {a.get()}")
        print(f"B Ã¨ ora: {b.get()}")

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
                print(f"\nA vale ora: {a.get()}")

        print(f"Sono il Thread {get_ident()} e ora aspetterÃ² che B sia 5000. In questo momento B Ã¨: {b.get()}")
        b.waitForAtLeast(5000)
        print(f"Aspettato B, che adesso vale: {b.get()}")

class TestSpostaInt(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(1)
        numero = random.randint(1,100)
        a.sposta_int(b, numero)

class TestWaitAndBalance(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(1)
        numero = random.randint(1,100)
        a.waitAndBalance(b, numero)

class TestSposta(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(2)
        a.sposta(b, c)

class TestWaitAndBalance2(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(1)
        numero = random.randint(1,100)
        a.waitAndBalance2(b, c)

class TestSomma(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lista = []

    def run(self):
        self.lista = [b, c]
        somma = a.somma(self.lista)
        print(f"LA SOMMA E' {somma}\n")

class Test(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(2)
        a.set(1)
        c.set(1)    


print("STARTING THREADS")
Thread1().start()
Thread2().start()
Thread2().start()
TestSpostaInt().start()
TestSposta().start()
TestWaitAndBalance().start()
TestWaitAndBalance2().start()
TestSomma().start()
Test().start()


print("MAIN STARTED")