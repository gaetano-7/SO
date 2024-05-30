import math
import multiprocessing
from threading import Condition, Lock, Thread
import time

class Totale:

    def __init__(self):
        self.tot = 0

    def getTotale(self):
        return self.tot
    
    def setTotale(self,agg):
        self.tot += agg

class DistributoreNumeri:

    def __init__(self,min,max):
        self.D = 10
        self.min = min
        self.max = max
        self.numCorrente = min
        self.lock = Lock()

    def setQuantita(self,D):
        with self.lock:
            self.D = D
    
    '''
        Utilizzato dai macinatori per avere un intervallo di numeri da calcolare
    '''
    def getNextInterval(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            self.numCorrente += self.D
            primo = self.numCorrente - self.D
            secondo = self.numCorrente-1
            if secondo > self.max:
                return primo, self.max
            return self.numCorrente - self.D, self.numCorrente-1

    '''
        Utilizzato dai macinatori per avere un numero da calcolare
    '''
    def getNextNumber(self):
        with self.lock:
            # se il numero corrente è maggiore del massimo
            if self.numCorrente > self.max:
                # restituisci -1 poichè tutti i numeri sono stati testati
                return -1
            # altrimenti, il numero da testare è il corrente
            num = self.numCorrente
            # incrementa il numero per la prossima chiamata
            self.numCorrente += 1
            # restituisce il numero da testare
            return num
    


class Barrier:

    def __init__(self,n):

        self.soglia = n # numero totale di thread che devono raggiungere la barriera
        self.threadArrivati = 0 # numero thread che hanno raggiunto la barriera
        self.lock = Lock()
        self.condition = Condition(self.lock)

    # viene chimato dai thread quando raggiungono la barriera
    def wait(self):
        with self.lock:
            # quando arriva il thread viene incrementato di 1
            self.threadArrivati += 1

            # se tutti i thread hanno raggiunto la barriera
            if self.threadArrivati == self.soglia:
                # notifica tutti i thread che possono procedere
                self.condition.notify_all()

            # finchè non arrivano tutti i thread
            while self.threadArrivati < self.soglia:
                # il thread viene messo in attesa
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
    def __init__(self,d,b, ist_tot):
        super().__init__()
        # self.min = min
        # self.max = max
        self.totale = 0 # totale di numeri primi trovati
        self.barrier = b
        self.distributore = d
        self.ist_tot = ist_tot
    
    def run(self):
        # chiama il metodo del ditributore che restituisce il numero da testare
        n = self.distributore.getNextNumber()
        # conta quanti numeri sono stati testati
        quantiNeHoFatto = 0

        # finchè riceve un numero diverso da -1
        while(n != -1):
            # se il numero è primo
            if eprimo(n):
                # incrementa il totale di numeri primi trovati
                self.ist_tot.setTotale(1)
            # incrementa i numeri testati
            quantiNeHoFatto += 1
            # chiama il metodo del ditributore che restituisce il numero da testare
            n = self.distributore.getNextNumber()
        
        print(f"Il thread {self.name} ha finito e ha testato {quantiNeHoFatto} numeri\n")
        # quando il thread ha finito il test dei numeri utilizza
        # la barriera per mettersi in attesa che tutti finiscano
        self.barrier.wait()

class Macinatore2(Thread):
    def __init__(self,d,b, ist_tot):
        super().__init__()
        # self.min = min
        # self.max = max
        self.totale = 0 # totale di numeri primi trovati
        self.barrier = b
        self.distributore = d
        self.ist_tot = ist_tot
    
    def run(self):
        n = self.distributore.getNextInterval()
        quantiNeHoFatto = 0

        while (n != -1):
            primo, secondo = n
            self.ist_tot.setTotale(contaPrimiSequenziale(primo,secondo))
            quantiNeHoFatto += secondo - primo
            n = self.distributore.getNextInterval()

        print(f"Il thread {self.name} ha finito e ha testato {quantiNeHoFatto} numeri\n")
        self.barrier.wait()



def contaPrimiMultiThread(min,max):
    # numero processori disponibili nel sistema
    nthread = 2
    #multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori\n" )

    # lista per contenere istanze di Macinatore
    ciucci = []
    
    # bariera per sincronizzare i thread
    b = Barrier(nthread+1)
    # distribuisce i numeri con l'intervallo specificato
    d = DistributoreNumeri(min,max)

    d.setQuantita(5)

    t = Totale()

    # per ogni processo viene istanziato un Macinatore
    # con il distributore di numeri e la barriera
    # e viene aggiunto alla lista di istanze
    for i in range(nthread):
        ciucci.append(Macinatore2(d, b, t))
        ciucci[i].start() # avvia il thread

    # aspetta che tutti i thread abbiano raggiunto il numero 
    # di numeri primi trovati
    b.wait() 

    return t.getTotale()



min = 1000
max = 1000000
start = time.time()
nprimi = contaPrimiMultiThread(min,max)
elapsed = time.time() - start
print (f"Primi tra {min} e {max}: {nprimi}\n")
print (f"Tempo trascorso: {elapsed} secondi\n")
