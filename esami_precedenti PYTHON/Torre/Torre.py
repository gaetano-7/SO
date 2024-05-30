from threading import Thread,Condition,RLock
from time import sleep
from random import randint

debug = True
#
# Funzione di stampa sincronizzata di debug
#
plock = RLock()
def prints(s):
    plock.acquire()
    if debug:
        print(s)
    plock.release()


class TorreInCostruzione:
    
    def __init__(self,H : int):
        self.altFinale = H
        self.larghezzaFinale = 3
        self.stratoAttuale = 0
        self.tipiStrato = ['-','*']          # oscilleremo tra 0 e 1
        self.torre = ['']                    # il primo strato sarà  self.torre[0], inizialmente impostato a ''
        self.tipoStratoAttualmenteUsato = 0  # modalitÃ  iniziale = cemento, poichè self.tipiStrato[0] = '-'
        self.terminato = False               # imposteremo self.terminato = True quando la Torre sarà  completa
        self.lock = RLock()
        self.attendiTurno = Condition(self.lock)
        self.attendiFine = Condition(self.lock)
        self.urgente = False

    #def printTorre(self):
    #    prints(self.torre)

    def attendiTerminazione(self):
        with self.lock:
            while not self.terminato:
                self.attendiFine.wait()

    def addPezzo(self,c) -> bool:
        with self.lock:
            while self.tipiStrato[self.tipoStratoAttualmenteUsato] != c and not self.terminato or self.urgente:
                self.attendiTurno.wait()

            if self.stratoAttuale == self.altFinale - 1 and len(self.torre[self.stratoAttuale]) == self.larghezzaFinale:
                self.terminato = True
                self.attendiTurno.notify_all()
                self.attendiFine.notify_all()
                return False
            
            self.torre[self.stratoAttuale] = self.torre[self.stratoAttuale] + c

            if len(self.torre[self.stratoAttuale]) == self.larghezzaFinale and self.stratoAttuale < self.altFinale - 1:
                self.stratoAttuale += 1
                self.torre.append( '' ) # predispongo il prossimo strato 
                self.tipoStratoAttualmenteUsato = (self.tipoStratoAttualmenteUsato + 1) % 2
                self.attendiTurno.notify_all()

            #self.printTorre()

            return True

    def waitForStrato(self, S: int):
        with self.lock:
            if S > self.altFinale:
                S = self.altFinale
            
            print(f"{(self.stratoAttuale/self.altFinale)*100}% COMPLETATO")

            while self.stratoAttuale < S or (self.stratoAttuale == S and len(self.torre[self.stratoAttuale]) < self.larghezzaFinale):
                print("\nATTENDO LO STRATO")
                self.attendiTurno.wait()

    '''def aggiungiStratoUrgente(self, s: str):
        with self.lock:
            self.urgente = True

            self.torre[self.stratoAttuale] = self.torre[self.stratoAttuale] + s

            if len(self.torre[self.stratoAttuale]) == self.larghezzaFinale and self.stratoAttuale < self.altFinale - 1:
                self.stratoAttuale += 1
                self.altFinale += 1
                self.urgente = False
                self.torre.append( '' ) # predispongo il prossimo strato 
                self.tipoStratoAttualmenteUsato = (self.tipoStratoAttualmenteUsato + 1) % 2
                self.attendiTurno.notifyAll()'''

class Operaio(Thread):
    def __init__(self,t : TorreInCostruzione, tp : str, d:int):
        super().__init__()
        self.torre = t
        self.tipo = tp
        self.durata = d
    
    def run(self):
        while(self.torre.addPezzo(self.tipo)):
            #sleep(self.durata/1000)
            sleep(0.5)
        prints("Thread di tipo: '%s' finito" % self.tipo) 
           
class Cementatore(Operaio):
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'-',25)

class Mattonatore(Operaio):
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'*',50)

'''class Urgente(Thread):
    def __init__(self,t : TorreInCostruzione, tp : str, d:int):
        super().__init__()
        self.torre = t
        self.tipo = tp
        self.durata = d
    
    def run(self):
        while True:
            while(self.torre.aggiungiStratoUrgente(self.tipo)):
                sleep(self.durata/1000)
            prints("Thread di tipo: '%s' finito" % self.tipo)
            return'''

class Stampatore(Thread):
    def __init__(self,t : TorreInCostruzione):
        super().__init__()
        self.torre = t

    def run(self):
        while True:
            while not self.torre.terminato:
                sleep(1)
                self.torre.waitForStrato(self.torre.stratoAttuale-1)
            return

class Torre:
    
    def __init__(self):
        pass
            
    def makeTorre(self,H:int, M:int, C:int, U:int): 
        t = TorreInCostruzione(H)
        Mattonatori = [Mattonatore(t) for _ in range(M)]
        Cementatori = [Cementatore(t) for _ in range(C)]
        #Urgenti = [Urgente(t,"8==D",100) for _ in range(U)]
        for m in Mattonatori:
            m.start()
        for c in Cementatori:
            c.start()
        '''for u in Urgenti:
            u.start()'''
        
        S = Stampatore(t)
        S.start()

        t.waitForStrato(5)

        t.attendiTerminazione()
        return t.torre
        
if __name__ == '__main__':
    T = Torre()
    print (T.makeTorre(90,4,7,2))
    prints("TORRE FINITA")
    