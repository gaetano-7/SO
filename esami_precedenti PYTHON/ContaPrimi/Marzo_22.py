import math
import multiprocessing
from threading import Condition, Lock, Thread
import time
import random

'''
Punto 1:
Si modifichi la logica di funzionamento del DistributoreNumeri in maniera tale da distribuire D numeri da verificare per
volta. La quantità D, che di default vale 10, deve essere modificabile dinamicamente (e cioè anche durante la fase di calcolo
dei Macinatori) attraverso il metodo thread safe DistributoreNumeri.setQuantita(d);
Invece, al posto del metodo DistributoreNumeri.getNextNumber() i Macinatori dovranno usare il metodo
DistributoreNumeri.getNextInterval() che restituisce un intervallo composto da D numeri da far calcolare
al Macinatore chiamante. L intervallo assegnato può essere più piccolo di D nel caso in cui i numeri restanti da testare
siano di meno.
Ad esempio, supponiamo che D=20 ed nthread=2.
Quando si invoca contaPrimiMultiThread(101,175), il distributore di numeri assegnerà ai due Macinatori, mano a
mano che questi ne fanno richiesta, gli intervalli (101,120), (121,140), (141,160), (161,175).
La modifica deve essere compatibile con eventuali Macinatori che continuino a usare getNextNumber (e cioè che
continuano a prelevare un numero per volta)

Punto 2:
Si noti che ciascun Macinatore lavora su un suo totale parziale che viene infine usato per calcolare il totale finale con lo
spezzone di codice:
totale = 0
for i in range(nthread):
totale += ciucci[i].getTotale()
return totale
Si modifichi il codice in maniera tale che ciascun Macinatore, nell arco del suo processo di calcolo, aggiorni direttamente
una variabile Totale condivisa. Il ciclo di cui sopra dovrebbe dunque poter essere sostituito con qualcosa di simile a:
return Totale.getTotale()
che restituisce il totale globale senza la necessità di sommare tutti i totali parziali.

'''

class DistributoreNumeri:

    def __init__(self,min,max):
        self.min = min
        self.max = max
        self.numCorrente = min
        self.lock = Lock()
        self.quantita = 10
        self.ultimo = False
    '''
        Utilizzato dai macinatori per avere un numero da calcolare
    '''
    def getNextNumber(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            num = self.numCorrente
            self.numCorrente += 1
            return num
        
    def setQuantita(self, d):
        with self.lock:
            self.quantita = d
            print(f"QUANTITA IMPOSTATA SU {self.quantita}\n")
        

    def getNextInterval(self):
        with self.lock:
            lista = []
            if self.numCorrente > self.max:
                return -1
            for i in range(self.numCorrente, self.numCorrente+self.quantita):
                lista.append(self.numCorrente)
                self.numCorrente += 1
                if self.numCorrente == self.max:
                    self.ultimo = True
                    return lista
            return lista

class Barrier:

    def __init__(self,n):

        self.soglia = n
        self.threadArrivati = 0
        self.lock = Lock()
        self.condition = Condition(self.lock)

    def wait(self):
        with self.lock:
            self.threadArrivati += 1

            if self.threadArrivati == self.soglia:
                self.condition.notifyAll()

            while self.threadArrivati < self.soglia:
                self.condition.wait()

'''
    Utilizzabile per testare se un singolo numero è primo
'''
def eprimo(n):
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    for i in range(3,int(math.sqrt(n)+1),2):
        if n % i == 0:
            return False
    return True

'''
    Utilizzabile per conteggiare un singolo intervallo di numeri primi
'''
def contaPrimiSequenziale(min,max):
    totale = 0
    for i in range(min,max+1):
        if eprimo(i):
            totale += 1
    return totale

class Macinatore(Thread):
    def __init__(self,d,b):
        super().__init__()
        self.min = min
        self.max = max
        self.totale = 0
        self.barrier = b
        self.distributore = d

    def getTotale(self):
        return self.totale
    
    def run(self):
        n = self.distributore.getNextNumber()
        quantiNeHoFatto = 0
        while(n != -1):
            
            if eprimo(n):
                self.totale += 1
            quantiNeHoFatto += 1
            n = self.distributore.getNextNumber()
        
        print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri\n")
        self.barrier.wait()

class MacinatoreDinamico(Thread):
    def __init__(self,d,b,t):
        super().__init__()
        self.min = min
        self.max = max
        self.barrier = b
        self.totale = t
        self.distributore = d
    
    def run(self):
        while True:
            if self.distributore.ultimo:
                self.barrier.wait()
                return False
            n = self.distributore.getNextInterval()
            quantiNeHoFatto = 0
            for i in range(len(n)):
                if eprimo(n[i]):
                    self.totale.aggiungi_Totale()
                quantiNeHoFatto += 1
            if self.distributore.ultimo:
                print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri: {n}")
                self.barrier.wait()
                return False
            print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri: {n}")

class Changer(Thread):
    def __init__(self, distributore):
        super().__init__()
        self.distributore = distributore

    def run(self):
        while True:
            if self.distributore.ultimo:
                return False
            
            time.sleep(3)

            numero = random.randint(1,100)
            self.distributore.setQuantita(numero)

def contaPrimiMultiThread(min,max):

    nthread = multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori" )
    ciucci = []
        
    b = Barrier(nthread+1)
    d = DistributoreNumeri(min,max)
    totale = Totale()

    '''
    for i in range(nthread):
        ciucci.append(Macinatore( d, b ))
        ciucci[i].start()
    '''

    for i in range(nthread):
        ciucci.append(MacinatoreDinamico(d,b, totale))
        ciucci[i].start()
    
    changer = Changer(d)
    changer.start()

    b.wait()

    return totale.getTotale()

class Totale:
    def __init__(self):
        self.totale = 0
    
    def aggiungi_Totale(self):
        self.totale += 1
    
    def getTotale(self):
        return self.totale



min = 100000
max = 1000000
start = time.time()
nprimi = contaPrimiMultiThread(min,max)
elapsed = time.time() - start
print (f"Primi tra {min} e {max}: {nprimi}")
print (f"Tempo trascorso: {elapsed} secondi")