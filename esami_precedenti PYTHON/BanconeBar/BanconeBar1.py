import threading
import random
import time
import string
#
#   BANCONE DEL BAR
#
#   Questo codice simula il workflow tipico dell'arrivo dei clienti in un bar
#   e la loro gestione da parte del barista.
#
#   Il bancone del bar è rappresentato da un vettore di liste, dove ogni lista
#   rappresenta una "colonna" del bancone e cioè un certo numero di clienti che si accodano sulla stessa fila
#   Ogni colonna può contenere al massimo 
#   un numero di elementi pari al numero di "righe" del bancone.
#
#   I clienti che arrivano al bar vengono inseriti in una delle colonne del bancone
#   tra quelle che hanno meno elementi. Se ci sono più colonne con lo stesso
#   numero minimo di elementi, viene scelta una di queste a caso. Se il bancone è pieno,
#   la procedura di inserimento viene messa in attesa.
#
#   Il barista, quando è libero, prende un cliente a caso che trova sulla fila 0
#   e lo serve.  Se non ci sono clienti, la procedura di estrazione viene posta in attesa.
#
#  Ad esempio, lo stato del bancone in un certo momento potrebbe essere:
#
#   OOOOO
#   OO-OO
#   OO--O    
#   -O--O
# 
#  dove O indica che c'è un cliente e - indica che la posizione corrispondente è vuota. Il barista
#  serve prima i clienti sulla prima riga, scegliendo a caso tra quelli che trova.
#  
#  I clienti in arrivo preferiscono accodarsi sulle colonne che hanno meno elementi.  
#    

class BanconeBar:
    def __init__(self, righe, colonne):
        self.righe = righe
        self.colonne = colonne
        self.bancone = [[] for _ in range(colonne)]
        self.lock = threading.Lock()
        self.cnt = 0
        self.check = ''
        self.ceElemento = threading.Condition(self.lock)
        self.cePostoLibero = threading.Condition(self.lock)
        self.condition_E = threading.Condition(self.lock)

    def __cisonoElementi(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) > 0:
                return True
        return False
    
    def __tuttoPieno(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) < self.righe:
                return False
        return True
    
    def __getIndiciFilaPiuCorta(self):
        minimo = len(self.bancone[0])
        for i in range(1, self.colonne):
            if len(self.bancone[i]) < minimo:
                #print(f"La lunghezza del bancone {i} è {len(self.bancone[i])}")
                minimo = len(self.bancone[i])
        return [i for i in range(self.colonne) if len(self.bancone[i]) == minimo]

    def get(self):
        with self.lock:
            while not self.__cisonoElementi():
                self.ceElemento.wait()
            indici_non_nulli = [i for i in range(self.colonne) if len(self.bancone[i]) > 0]
            indice_scelto = random.choice(indici_non_nulli)
            if self.bancone[indice_scelto][0] != 7:
                elemento = self.bancone[indice_scelto].pop(0)
                if elemento == self.check:
                    self.condition_E.notify()
                self.cePostoLibero.notify_all()
            else:
                print ("NCE U SETTI")
                cont = 0
                for i in range (self.colonne):
                    if self.bancone[i][0] == 7:
                        cont += 1
                if cont == self.colonne:
                    elemento = self.bancone[indice_scelto].pop(0)
                else:
                    elemento = ""
            return elemento

    def put(self, elemento):
        with self.lock:
            while self.__tuttoPieno():
                self.cePostoLibero.wait()
            self.cnt += 1
            if self.cnt == 10:
                elemento = 7
            if self.cnt == 11:
                self.cnt = 0
            self.bancone[random.choice(self.__getIndiciFilaPiuCorta())].append(elemento)
            self.ceElemento.notify_all()
        
    
    def print_bancone(self):
        with self.lock:
            for r in range(self.righe):
                for c in range(self.colonne):
                    toPrint = self.bancone[c][r] if len(self.bancone[c]) >= r+1 else '-'
                    print(toPrint, end = '') 
                print()

    def miglioraPosizione(self,r,c):
        with self.lock:
            print(f"C = {c}")
            if len(self.bancone[c]) <= r:
                print("NESSUN ELEMENTO PRESENTE")
                return
            else:
                if c == 0 and (len(self.bancone[c+1]) < len(self.bancone)):
                    self.bancone[c+1].append(self.bancone[c][r])
                    self.bancone[c].remove(self.bancone[c][r])
                    print("POSIZIONE CAMBIATA")
                    return
                if c == self.colonne-1 and (len(self.bancone[c-1]) < len(self.bancone)):
                    self.bancone[c-1].append(self.bancone[c][r])
                    self.bancone[c].remove(self.bancone[c][r])
                    print("POSIZIONE CAMBIATA")
                    return
                if (len(self.bancone[c-1]) < len(self.bancone[c])):
                    self.bancone[c-1].append(self.bancone[c][r])
                    self.bancone[c].remove(self.bancone[c][r])
                    print("POSIZIONE CAMBIATA")
                    return
                if (len(self.bancone[c+1]) < len(self.bancone[c])):
                    self.bancone[c+1].append(self.bancone[c][r])
                    self.bancone[c].remove(self.bancone[c][r])
                    print("POSIZIONE CAMBIATA")
                    return
        
    def attendiServizio(self, E):
        with self.lock:
            self.check = E
            print(f"ELEMENTO {E}")
            trovato = False
            for colonna in self.bancone:
                for elem in colonna:
                    if elem == E:
                        trovato = True
                        print ("E' IN ATTESA")
            if trovato == False:
                print ("NON C'è NESSUNO NEL LOCALE CON QUESTO NOME")
                return False
            while trovato:
                #self.condition_E.wait(self.lock)
                self.condition_E.wait(timeout=None)
                print ("SE N'E' ANDATO")
                return True

def migliora(bancone):
    while True:
        r = random.randint(0,bancone.righe-1)
        c = random.randint(0,bancone.colonne-1)
        bancone.miglioraPosizione(r,c)
        time.sleep(1)

def attendi(bancone):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone.attendiServizio(elemento)
        time.sleep(5)

def prendi_elementi(bancone):
    while True:
        elemento = bancone.get()
        print("Elemento prelevato:", elemento)
        time.sleep(1)  # Simula un tempo di elaborazione

def inserisci_elementi(bancone):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone.put(elemento)
        print("Elemento inserito:", elemento)
        time.sleep(0.5)  # Simula un tempo di elaborazione

def stampa_bancone(bancone):
    while True:
        bancone.print_bancone()
        time.sleep(1)

bancone = BanconeBar(7, 5)


#
# Un modo diverso per creare i thread senza dovere dichiarare una classe a parte,
# consiste nel passare come target una funzione che si vuole eseguire al posto del metodo run
#
thread_barista = threading.Thread(target=prendi_elementi, args=(bancone,))
thread_barista.start()


thread_creaClienti = threading.Thread(target=inserisci_elementi, args=(bancone,))
thread_creaClienti.start()


thread_stampab = threading.Thread(target=stampa_bancone, args=(bancone,))
thread_stampab.start()

thread_lilla = threading.Thread(target=migliora, args=(bancone,))
thread_lilla.start()

thread_attendi = threading.Thread(target=attendi, args=(bancone,))
thread_attendi.start()