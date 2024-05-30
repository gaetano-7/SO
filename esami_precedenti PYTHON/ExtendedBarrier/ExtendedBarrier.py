import math
import multiprocessing
from threading import Condition, Lock, Thread
import time


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
                self.condition.notify_all()

            while self.threadArrivati < self.soglia:
                self.condition.wait()

class ExtendedBarrier(Barrier):
    
    def __init__(self, n):
        super().__init__(n)

    def finito(self):
        with self.lock:
            self.threadArrivati += 1
            if self.threadArrivati == self.soglia:
                self.condition.notify_all()
    
    def aspettaEbasta(self):
        with self.lock:
            while self.threadArrivati < self.soglia:
                self.condition.wait()

    def wait(self):
        with self.lock:
            self.finito()
            self.aspettaEbasta()

class DoppiaBarriera:

    def __init__(self, n0, n1):
        self.S0 = n0
        self.S1 = n1
        self.threadArrivati0 = 0
        self.threadArrivati1 = 0
        self.lock = Lock()
        self.condition0 = Condition(self.lock)
        self.condition1 = Condition(self.lock)

    def finito(self, numSoglia):
        with self.lock:
            if numSoglia == 0:
                self.threadArrivati0 += 1
                if self.threadArrivati0 == self.S0:
                    self.condition0.notify_all()
            if numSoglia == 1:
                self.threadArrivati1 += 1
                if self.threadArrivati1 == self.S1:
                    self.condition1.notify_all()


    def aspettaEbasta(self, numSoglia):
        with self.lock:
            if numSoglia == 0:
                while self.threadArrivati0 < self.S0:
                    self.condition0.wait()
            if numSoglia == 1:
                while self.threadArrivati1 < self.S1:
                    self.condition1.wait()

    def wait(self, numSoglia):
        with self.lock:
            self.finito(numSoglia)
            self.aspettaEbasta(numSoglia)

    def waitAll(self):
        with self.lock:
            self.finito(self.S0)
            self.finito(self.S1)
            self.aspettaEbasta(self.S0)
            self.aspettaEbasta(self.S1)