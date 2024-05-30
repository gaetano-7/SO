from threading import Thread, Lock, current_thread, Condition
from time import sleep
from random import random, randrange

'''
Punto 1. Fattorizza il codice esistente introducendo una classe Sala che possiede al suo interno una matrice quadrata di
PostoSafe. Ricorda che “Fattorizzare” = “Riorganizzare”. Il numero di file iniziale deve essere passato via costruttore.
La classe Sala deve offrire il metodo pubblico
self.testaEoccupa(i,j). Dato il posto di coordinate (i,j), occupa il posto in tali coordinate se questo è libero.
Restituisce False in caso di fallimento, e True altrimenti.

Punto 2. Aggiungi alla classe sviluppata nel punto precedente il metodo self.trovaPosto(). Cerca di occupare un
posto qualsiasi tra quelli rimasti liberi. Restituisce la coppia (i,j) dove (i,j) sono le coordinate del posto trovato. Se
la sala è piena, restituisce la coppia (-1,-1). Da notare che “qualsiasi” non vuol dire necessariamente “casuale”. scegli tu
la strategia più adeguata per trovare un posto libero.

Punto 3. Sposta il codice che stampa il contenuto della sala all interno della classe Sala; rendi questo codice thread-safe;
fai in modo che il thread Display si attivi stampando il contenuto della Sala solo quando c è una effettiva modifica;

Punto 4. Fai in modo che il Thread Display termini quando tutti gli altri thread PartecipanteSafe hanno
terminato.
'''

class PostoSafe:
    def __init__(self):
        self.lock = Lock()
        self.occupato = False
        
    def testaEoccupa(self):
        with self.lock:
            if self.occupato:
                return False
            else:
                self.occupato = True
                return True
            
class Sala:
    def __init__(self,numero_file):
        self.lock = Lock()
        self.thread_arrivati = 0
        self.thread_attivi = 0
        self.tutti_i_thread_terminati = False
        self.conditionDisplay = Condition(self.lock)
        self.posti = [[PostoSafe() for j in range(numero_file)] for i in range(numero_file)]
    
    def testaEoccupa(self,i,j):
        return self.posti[i][j].testaEoccupa()
        
    def thread_terminati(self):
        with self.lock:
            self.thread_arrivati += 1
            self.thread_attivi -= 1
            if(self.thread_attivi == 0):
                self.tutti_i_thread_terminati = True
                self.conditionDisplay.notify_all()
        
    def trovaPosto(self):
        with self.lock:
            for i in range(len(self.posti)):
                for j in range(len(self.posti[0])):
                    if self.testaEoccupa(i,j):
                        self.conditionDisplay.notify()
                        return i, j
            return -1, -1
        
    def stampa(self):
        with self.lock:
            while not self.tutti_i_thread_terminati:
                self.conditionDisplay.wait()
                if self.tutti_i_thread_terminati:
                    break
                print(f"+{'-' * len(self.posti[0]) * 2}+")
                for i in range(len(self.posti)):
                    row = "|"
                    for j in range(len(self.posti[0])):
                        if self.posti[i][j].occupato:
                            row += "o "
                        else:
                            row += ". "
                    row += "|"
                    print(row)
                print(f"+{'-' * len(self.posti[0]) * 2}+")

class Display(Thread):

    def __init__(self, sala):
        super().__init__()
        self.sala = sala

    def run(self):
        self.sala.stampa()

class PartecipanteSafe(Thread):
    def __init__(self, sala):
        super().__init__()
        self.sala = sala

    def run(self):
        sleep(randrange(5))
        i, j = self.sala.trovaPosto()
        if i != -1 and j != -1:
            print(f"Sono il Thread {current_thread().name}. Occupo il posto ({self.sala.trovaPosto()}\n)")
            self.sala.thread_terminati()
        print(f"Sono il Thread {current_thread().name}. HO PERSO")
        self.sala.thread_terminati()

def main():
    numero_file = 10
    sala = Sala(numero_file)
    #posti = [[PostoSafe() for j in range(numero_file)] for i in range(LATOSALA)]

    lg = Display(sala)
    lg.start()

    for i in range(numero_file*numero_file+5):
        # t = PartecipanteUnsafe(posti)
        t = PartecipanteSafe(sala)
        t.name = f"Spettatore-{i}"
        t.start()
        sala.thread_attivi += 1

    lg.join()

if __name__ == '__main__':
    main()