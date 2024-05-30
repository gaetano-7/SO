from threading import RLock,Condition, Thread
import random
import time

'''
Punto 1
Aggiungi alla struttura dati BlockingStack il metodo flush(self). Tale metodo elimina tutti gli elementi
attualmente presenti nel BlockingStack.
Punto 2
Aggiungi alla struttura dati BlockingStack il metodo putN(self,L : List). Tale metodo inserisce tutti gli
elementi della lista L all interno di self. Se self non dispone di almeno len(L) posti liberi, ci si pone in attesa
bloccante finché tali posti non si rendano disponibili, effettuando a seguire l inserimento degli elementi di L.
Punto 3
Dal momento che un BlockingStack è basato su una politica di inserimento ed estrazione di tipo LIFO, è evidente che
esso soffre di problemi di starvation. Introduci dunque il metodo setFIFO(self,onOff : bool). Quando onOff
= True, il BlockingStack corrente deve cominciare a funzionare come una BlockingQueue, e cioè con politica di
inserimento ed estrazione FIFO. Se invece onOff = False, il BlockingStack deve tornare a funzionare come uno stack
LIFO. L invocazione di setFIFO deve avere effetto anche sull ordine di estrazione degli elementi ormai già inseriti.
'''

class BlockingStack:
    
    def __init__(self,size):
        self.size = size
        self.elementi = []
        self.lock = RLock()
        self.conditionTuttoPieno = Condition(self.lock)
        self.conditionTuttoVuoto = Condition(self.lock)
        self.FIFO_attiva = False
        
    def __find(self,t):
        try:
            if self.elementi.index(t) >= 0:
                return True
        except(ValueError):
            return False
    
    def put(self,t):
        self.lock.acquire()
        while len(self.elementi) == self.size:
            self.conditionTuttoPieno.wait()
        self.conditionTuttoVuoto.notify_all()
        self.elementi.append(t)
        self.lock.release()
    
    
    def take(self,t=None):
        self.lock.acquire()
        try:
            if t == None:
                while len(self.elementi) == 0:
                    self.conditionTuttoVuoto.wait()
                
                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()
                if self.FIFO_attiva == False:
                    return self.elementi.pop()
                else:
                    return self.elementi.pop(0)
            else:
                while not self.__find(t):
                    self.conditionTuttoVuoto.wait()
                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()
                self.elementi.remove(t)    
                return t    
        finally:
            self.lock.release()

    def flush(self):
        self.lock.acquire()
        self.elementi.clear()
        self.conditionTuttoPieno.notify_all()
        self.lock.release()

    def putN(self, L: list):
        self.lock.acquire()
        while (len(self.elementi) + len(L)) < self.size:
            self.conditionTuttoPieno.wait()
        self.elementi += L
        self.conditionTuttoVuoto.notify_all()
        self.lock.release()

    def setFIFO(self, onOff : bool):
        with self.lock:
            if onOff == False:
                print("CODA LIFO ATTIVA\n")
                return
            self.FIFO_attiva = True
            print("CODA FIFO ATTIVA\n")
            return

    
    

class Consumer(Thread): 
    
    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random()*2)
            print(f"Estratto elemento {self.queue.take()}")
            


class Producer(Thread):

    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self): 
        while True:
            time.sleep(random.random() * 2)
            self.queue.put(self.name)

class Fifo(Thread):
    def __init__(self, buffer):
        Thread.__init__(self)
        self.buffer = buffer

    def run(self):
        while True:
            time.sleep(5)
            scelta = random.randint(0,1)
            if scelta == 0:
                self.buffer.setFIFO(False)
            else:
                self.buffer.setFIFO(True)
            
#  Main
#
buffer = BlockingStack(10)

producers = [Producer(buffer) for x in range(5)]
consumers = [Consumer(buffer) for x in range(3)]

for p in producers:
    p.start()

for c in consumers:
    c.start()

fifo = Fifo(buffer)
fifo.start()
    