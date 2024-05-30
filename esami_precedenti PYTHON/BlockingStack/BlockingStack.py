from threading import RLock,Condition, Thread
import random
import time

class BlockingStack:
    
    def __init__(self,size):
        self.size = size
        self.elementi = []
        self.lock = RLock()
        self.conditionTuttoPieno = Condition(self.lock)
        self.conditionTuttoVuoto = Condition(self.lock)
        self.FIFO = False
        
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
                
                if self.FIFO == False:
                    print(f"RIMOSSO ELEMENTO IN CIMA\n")
                    elemento = self.elementi.pop()
                    if len(self.elementi) == 0:
                        self.conditionTuttoPieno.notify_all()
                    return elemento
                else:
                    print(f"RIMOSSO ELEMENTO IN CODA\n")
                    elemento = self.elementi.pop(0)
                    if len(self.elementi) == 0:
                        self.conditionTuttoPieno.notify_all()
                    return elemento
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
        while len(self.elementi) == 0:
            self.conditionTuttoVuoto.wait()
        self.elementi.clear()
        self.conditionTuttoPieno.notify_all()
        self.lock.release()

    def putN(self, L : list):
        self.lock.acquire()
        while ((len(self.elementi) + len(L)) > self.size):
            self.conditionTuttoPieno.wait()
        for i in range(len(L)):
            self.elementi.append(L[i])
        print(f"{L} AGGIUNTA ALLA LISTA\n")
        self.conditionTuttoVuoto.notify_all()
        self.lock.release
        
    def setFIFO(self, onOff : bool):
        self.lock.acquire()
        self.FIFO = onOff
        print(f"CODA SETTATA A {self.FIFO}\n")
        print(f"ELEMENTI ATTUALMENTE IN LISTA: {self.elementi}\n")
        self.lock.release()
    
    

class Consumer(Thread): 
    
    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random()*2)
            print(f"Estratto elemento {self.queue.take()}\n")
            


class Producer(Thread):

    def __init__(self,buffer):
        self.queue = buffer
        self.lista = []
        Thread.__init__(self)

    def run(self): 
        while True:
            time.sleep(random.random() * 2)
            rand = random.randint(0,10)
            if rand > 4:
                self.queue.put(self.name)
            else:
                for i in range(5):
                    self.lista.append(random.randint(0,100))
                self.queue.putN(self.lista)

class settatore(Thread):
    def __init__(self, buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(5)
            casuale = random.randint(0,1)
            if casuale == 0:
                self.queue.setFIFO(False)
            else:
                self.queue.setFIFO(True)
            
#  Main
#
buffer = BlockingStack(10)

producers = [Producer(buffer) for x in range(5)]
consumers = [Consumer(buffer) for x in range(3)]

for p in producers:
    p.start()

for c in consumers:
    c.start()

sett = settatore(buffer)
sett.start()