
from queue import Queue
from random import randint
from threading import Condition, RLock, Thread
import time

'''
Per questa prova di esame, dovrai progettare la classe Ristorante che combina una istanza di Pizzeria con una istanza di
classe Sala e con altri elementi che ora ti descriverò. Una Sala è composta da N tavoli da 10 posti ciascuno. Ciascun posto
può essere vuoto oppure essere occupato da una pizza. La Sala comunica con la pizzeria sostituendo ai Clienti, delle istanze
di thread Cameriere.

Il Cameriere è un nuovo tipo di thread che dovrai progettare appositamente. Così come avviene nel codice esistente di
Cliente, un Cameriere genera un ordine casualmente, lo affida ai pizzaioli usando il metodo putOrdine per poi prelevare
le pizze con il metodo getPizze.

Ci sono tuttavia delle differenze rispetto ai clienti:
-ogni ordine ora dovrà indicare un tavolo designato T, scelto tra quelli completamente sgombri, e appartenente alla Sala; T
rappresenta il tavolo dove il cameriere dovrà depositare le pizze appena sfornate;
-gli ordini non possono superare la quantità di dieci pizze totali;
-quando l ordine è pronto, il cameriere sistema le pizze sul tavolo T, ma poichè può trasportare al massimo due pizze per
volta, è costretto a fare più viaggi. Sarà tuo compito modificare il codice per fare in modo che si possano prelevare da uno
specifico ordine contenuto nel buffer delle pizze 2 elementi alla volta al massimo; inoltre, tra un viaggio e l altro dovrai
introdurre del tempo di attesa che simula il tempo che ci vuole ad andare dalla Pizzeria alla Sala e viceversa.

Una sala è inoltre dotata di una o più istanze di thread Sparecchiatore. Uno sparecchiatore toglie periodicamente le pizze
dai tavoli della Sala, ma dovrai assicurarti che una pizza appena depositata da un Cameriere non sia rimossa prima di 3
secondi dal momento in cui è stata poggiata sul tavolo.
Questo è tutto. Come sempre, è tuo specifico compito decidere cosa fare per tutti i dettagli che non sono stati
espressamente definiti
'''

pizze = { "margherita" : "(.)", 
          "capricciosa" : "(*)", 
          "diavola" : "(@)",
          "ananas" : "(,)"}



class Ordine:
    nextCodiceOrdine = 0
    def __init__(self,tipoPizza,quantita, tavolo):
        self.tipoPizza = tipoPizza
        self.quantita = quantita
        self.codiceOrdine = Ordine.nextCodiceOrdine
        self.pizzePronte = ""
        Ordine.nextCodiceOrdine += 1
        self.tavolo = tavolo

    def prepara(self):
        for i in range(self.quantita):
            self.pizzePronte += pizze[self.tipoPizza]

class BlockingSet(set):

    def __init__(self, size = 10):
        super().__init__()
        self.size = size
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def add(self,T):
        with self.lock:
            while len(self) == self.size:
                self.condition.wait()
            self.condition.notify_all()
            return super().add(T)

    def remove(self,T):
        with self.lock:
            while not T in self:
                self.condition.wait()
            super().remove(T)
            self.condition.notify_all()
            return True

class Pizzeria:
    
    def __init__(self):
        self.BO = Queue(10)
        self.BP = BlockingSet()

    def getOrdine(self):
        return self.BO.get()

    def putOrdine(self,codicePizza,quantita, tavolo):
        tavolo = tavolo
        ordine = Ordine(codicePizza,quantita, tavolo)
        self.BO.put(ordine)
        return ordine
        
    def getPizze(self,ordine):
        self.BP.remove(ordine)

    def putPizze(self,ordine):
        self.BP.add(ordine)

class Posto:
    def __init__(self):
        self.occupato = False
        self.tempo_passato = False

    def parti_timer(self):
        time.sleep(3)
        self.tempo_passato = True

class Tavolo:
    def __init__(self, n):
        self.numero = n
        self.occupato = False
        self.posti = [Posto() for i in range(10)]

class Sala:
    def __init__(self, N):
        self.N_tavoli = N
        self.tavoli = [Tavolo(i) for i in range(self.N_tavoli)]
        self.lock = RLock()
        self.cond = Condition(self.lock)

    def TrovaTavololibero(self):
        with self.lock:
            uno_libero = 0
            for i in range(self.N_tavoli):
                if self.tavoli[i].occupato == False:
                    uno_libero += 1
            while uno_libero == 0:
                self.cond.wait()
                uno_libero =0
                for i in range(self.N_tavoli):
                    if self.tavoli[i].occupato == False:
                        uno_libero += 1
            for i in range(self.N_tavoli):
                cnt = 0
                tavolo = self.tavoli[i]
                for j in range(10):
                    if tavolo.posti[j].occupato == False:
                        cnt += 1
                        if cnt == 10:
                            return tavolo
                    else:
                        continue
        
    def trasportaPizza(self,tavolo):
        with self.lock:
            cnt = 0
            for i in range(10):
                if tavolo.posti[i].occupato == False:
                    tavolo.posti[i].occupato = True
                    tavolo.posti[i].parti_timer()
                    cnt+=1
                    if cnt == 1:
                        tavolo.occupato = True
                if cnt == 2:
                    return
            return
        
    def SparecchiaTavoli(self):
        with self.lock:
            contatore = 0
            for i in range(self.N_tavoli):
                tavolo = self.tavoli[i]
                for j in range(10):
                    if tavolo.posti[j].tempo_passato:
                        tavolo.posti[j].occupato = False
                        tavolo.occupato = False
                        contatore += 1
                        self.cond.notify_all()
            return contatore

class Ristorante:
    def __init__(self):
        self.pizzeria = Pizzeria()

class Pizzaiolo(Thread):

    def __init__(self, name, pizzeria):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria

    def run(self):

        while True:
            ordine = self.pizzeria.getOrdine()
            tempoDiPreparazione = ordine.quantita
            time.sleep(tempoDiPreparazione)
            ordine.prepara()
            self.pizzeria.putPizze(ordine)
            #
            #  Sigaretta...
            #             
            time.sleep(randint(1,3))

class Cliente(Thread):
    def __init__(self, name, pizzeria):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria

    def run(self):
        while True:
                numeroPizze = 1 + randint(0,7)
                tipiPizza = list(pizze.keys())
                codicePizza = tipiPizza[randint(0,len(tipiPizza)-1)]

                print(f"Il cliente {self.name} entra in pizzeria e prova ad ordinare delle pizze")
                ordine = self.pizzeria.putOrdine(codicePizza, numeroPizze)
                print(f"Il cliente {self.name} aspetta le pizze con codice d'ordine numero {ordine.codiceOrdine}")

                time.sleep(randint(0, numeroPizze))

                self.pizzeria.getPizze(ordine)

                print(f"Il cliente {self.name} ha preso le pizze con codice d'ordine numero {ordine.codiceOrdine}")
                print(ordine.pizzePronte)
                #
                # Prima o poi mi tornerÃ  fame
                #
                time.sleep(randint(0, numeroPizze))

class Cameriere(Thread):
    def __init__(self,name, pizzeria,sala):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria
        self.sala = sala

    def run(self):
        while True:
            numeroPizze = 1 + randint(0,9)
            tipiPizza = list(pizze.keys())
            codicePizza = tipiPizza[randint(0,len(tipiPizza)-1)]

            tavolo = self.sala.TrovaTavololibero()

            print(f"Il Cameriere {self.name} prende un ordinazione")
            ordine = self.pizzeria.putOrdine(codicePizza, numeroPizze, tavolo)
            print(f"Il Cameriere {self.name} aspetta le pizze con codice d'ordine numero {ordine.codiceOrdine}")

            print(f"Il Cameriere {self.name} prende le pizze dalla cucina con codice d'ordine numero {ordine.codiceOrdine}")
            self.pizzeria.getPizze(ordine)

            viaggi =  1
            if numeroPizze %2 == 0:
                for i in range(numeroPizze//2):
                    self.sala.trasportaPizza(tavolo)
                    print(f"Il Cameriere {self.name} fa il viaggio numero {viaggi} dalla cucina con codice d'ordine numero {ordine.codiceOrdine}")
                    time.sleep(1)
                    viaggi += 1
            else:
                for i in range((numeroPizze//2)+1):
                    self.sala.trasportaPizza(tavolo)
                    print(f"Il Cameriere {self.name} fa il viaggio numero {viaggi} dalla cucina con codice d'ordine numero {ordine.codiceOrdine}")
                    time.sleep(1)
                    viaggi += 1

            print(f"Il Cameriere {self.name} ha portato tutte le pizze con codice d'ordine numero {ordine.codiceOrdine} al tavolo {ordine.tavolo.numero}")

class Sparecchiatore(Thread):
    def __init__(self, sala):
        super().__init__()
        self.sala = sala
        self.cont = 0

    def run(self):
        while True:
            time.sleep(20)
            self.cont = self.sala.SparecchiaTavoli()
            print(f"Lo sparecchiatore ha sparecchiato {self.cont} posti nei tavoli\n")

def main():
    NUMP = 3
    NUMC = 20
    NUMCAM = 3
    NUMS = 1
    p = []
    #c = []
    cam = []
    s = []
    pizzeria = Pizzeria()
    sala = Sala(10)

    for i in range(0, NUMP):
        pizzaiolo = Pizzaiolo("Totonno_" + str(i), pizzeria)
        p.append(pizzaiolo)
        pizzaiolo.start()

    #for i in range(0, NUMC):
    #    cliente = Cliente("Ciro_" + str(i), pizzeria)
    #    c.append(cliente)
    #    cliente.start()

    for i in range(0, NUMCAM):
        cameriere = Cameriere("Franco_" + str(i), pizzeria, sala)
        cam.append(cameriere)
        cameriere.start()

    for i in range(0, NUMS):
        sparecchiatore = Sparecchiatore(sala)
        s.append(sparecchiatore)
        sparecchiatore.start()

if __name__ == '__main__':
    main()
