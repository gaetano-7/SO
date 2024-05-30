import math
import multiprocessing
from threading import Condition, Lock, Thread
import time
import random

'''
Punto 1
Come primo requisito, la classe ExtendedBarrier dovrà estendere il codice iniziale di Barrier con i metodi
finito e aspettaEbasta(self). Il primo metodo incrementa di uno i threadArrivati ed esce; il secondo metodo si
mette in attesa che i threadArrivati raggiungano la soglia prescritta per poi uscire quando questa condizione si verifica, ma
senza incrementare il numero di threadArrivati.

Punto 2
Sempre agendo sulla classe ExtendedBarrier, fattorizza il metodo wait, sfruttando i metodi finito e
aspettaEbasta che hai appena implementato.

Punto 3
Progetta e implementa la classe DoppiaBarriera. La classe deve consentire di incrementare e attendere due soglie in
contemporanea: la soglia S0 e la soglia S1. Il costruttore di DoppiaBarriera riceve due valori di soglia n0 e n1 che
saranno rispettivamente associati alla soglia S0 e alla soglia S1.
In altre parole questa classe deve fornire i metodi:
finito(self,numSoglia)
Incrementa i threadArrivati sulla soglia numSoglia, dove numSoglia può valere 0 oppure 1 a seconda che si voglia
scegliere la soglia S0 o la soglia S1.
aspettaEbasta(self,numSoglia)
Attende che i thread arrivati su numSoglia raggiungano la soglia impostata, dove numSoglia può valere 0 oppure 1,
per poi uscire.
wait(self,numSoglia)
Incrementa i threadArrivati associati alla soglia numSoglia, quindi attende che i thread arrivati su numSoglia
raggiungano la soglia prescritta per poi uscire.
waitAll(self)
Incrementa di uno i thread arrivati su entrambe le soglie e aspetta che entrambe le soglie siano raggiunte dal numero di
thread prescritti
'''

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

class ExtendedBarrier(Barrier):
    def __init__(self, n):
        super().__init__(n)

    def finito(self):
        self.threadArrivati += 1
        print("THREAD AGGIUNTO\n")
        if self.threadArrivati == self.soglia:
            self.condition.notify_all()
        return
    
    def aspettaEbasta(self):
        while self.threadArrivati < self.soglia:
            print(f"ASPETTO CHE SIA RAGGIUNTA LA SOGLIA\n")
            self.condition.wait()
        print("SOGLIA RAGGIUNTA\n")
        return
        
    def wait(self):
        with self.lock:
            self.finito()
            self.aspettaEbasta()

class DoppiaBarriera:
    def __init__(self):
        self.B0 = barriera
        self.B1 = barriera

    def finito(self, numSoglia):
        if numSoglia == 0:
            self.B0.finito()
        elif numSoglia == 1:
            self.B1.finito()
        return
    
    def aspettaEbasta(self, numSoglia):
        if numSoglia == 0:
            self.B0.aspettaEbasta()
        elif numSoglia == 1:
            self.B1.aspettaEbasta()
        return
    
    def wait(self, numSoglia):
        if numSoglia == 0:
            self.B0.wait()
        elif numSoglia == 1:
            self.B1.wait()
        return
    
    def waitAll(self):
        self.B0.wait()
        self.B1.wait()

class threadSingolo(Thread):
    def __init__(self, barriera):
        super().__init__()
        self.barriera = barriera

    def run(self):
        time.sleep(1)
        self.barriera.wait()

class threadDoppio(Thread):
    def __init__(self, doppia_barriera):
        super().__init__()
        self.doppia_barriera = doppia_barriera

    def run(self):
        #time.sleep(1)
        scelta = random.randint(1,2)
        if scelta == 1:
            numero = random.randint(0,1)
            self.doppia_barriera.wait(numero)
        else:
            self.doppia_barriera.waitAll()


barriera = ExtendedBarrier(5)
'''
lista = [threadSingolo(barriera) for i in range(10)]

for i in range(10):
    lista[i].start()
'''

doppia_barriera = DoppiaBarriera()

lista = [threadDoppio(doppia_barriera) for i in range(10)]

for i in range(10):
    lista[i].start()