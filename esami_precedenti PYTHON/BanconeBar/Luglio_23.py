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
#   Il bancone del bar Ã¨ rappresentato da un vettore di liste, dove ogni lista
#   rappresenta una "colonna" del bancone e cioÃ¨ un certo numero di clienti che si accodano sulla stessa fila
#   Ogni colonna puÃ² contenere al massimo 
#   un numero di elementi pari al numero di "righe" del bancone.
#
#   I clienti che arrivano al bar vengono inseriti in una delle colonne del bancone
#   tra quelle che hanno meno elementi. Se ci sono piÃ¹ colonne con lo stesso
#   numero minimo di elementi, viene scelta una di queste a caso. Se il bancone Ã¨ pieno,
#   la procedura di inserimento viene messa in attesa.
#
#   Il barista, quando Ã¨ libero, prende un cliente a caso che trova sulla fila 0
#   e lo serve.  Se non ci sono clienti, la procedura di estrazione viene posta in attesa.
#
#  Ad esempio, lo stato del bancone in un certo momento potrebbe essere:
#
#   OOOOO
#   OO-OO
#   OO--O    
#   -O--O
# 
#  dove O indica che c'Ã¨ un cliente e - indica che la posizione corrispondente Ã¨ vuota. Il barista
#  serve prima i clienti sulla prima riga, scegliendo a caso tra quelli che trova.
#  
#  I clienti in arrivo preferiscono accodarsi sulle colonne che hanno meno elementi.  
#    

#
# Classe di supporto per la gestione di un elemento del bancone. 
#

'''
Punto 1. Implementa il metodo imposta_colonna_prioritaria(i). Questo metodo specifica una colonna i.
Dal momento in cui tale metodo viene invocato, l ordine di estrazione dal bancone bar presente nell implementazione di
get deve privilegiare la colonna i nell ordine di estrazione degli elementi. Quando i è completamente vuota va
applicata la strategia di estrazione pre-esistente. Se il valore di i è fuori dall intervallo dei valori ammissibili, la strategia di
estrazione deve tornare a essere quella pre-esistente.

Punto 2. Implementa la funzione attendi_invisibile(self). Il thread che invoca questo metodo va in attesa
bloccante fintantochè non viene estratto un elemento invisibile.

Punto 3. Progetta la classe bancone_combinato. Tale classe incapsula due istanze di banconebar B1 e B2 e un thread
S. Il costruttore della classe inizializza B1, B2 e crea ed avvia S. I metodi pubblici di tale classe devono essere gli stessi di
bancone bar, ma così ridefiniti:
-get: estrae un elemento da B1;
-put: inserisce un elemento in B2;
-attendiElemento: attende che un elemento sia complessivamente estratto dal bancone_combinato;
Il thread S deve prelevare periodicamente elementi da B2 depositarli in B1.
Non è necessario implementare printBancone e miglioraPosizione.

Punto 4. Scrivi del codice multi-threaded che testi tutti i metodi di cui sopra. Assicurati che il tuo codice non si inceppi per
via di errori di sintassi o altri problemi tecnici.
'''

class DatiElemento:
    def __init__(self, invisibile, elemento, condition):
        self.invisibile = invisibile
        self.elemento = elemento
        self.condition = condition 
        self.monitorato = False 
        self.estratto = False
 

class BanconeBar:
    def __init__(self, righe, colonne):
        self.righe = righe
        self.colonne = colonne
        self.bancone = [[] for _ in range(colonne)]
        self.lock = threading.Lock()
        self.ceElemento = threading.Condition(self.lock)
        self.cePostoLibero = threading.Condition(self.lock)
        self.bool_prioritaria = False
        self.colonna_prioritaria = 0
        self.cond_estratto = threading.Condition(self.lock)

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
                minimo = len(self.bancone[i])
        return [i for i in range(self.colonne) if len(self.bancone[i]) == minimo]
    
    def imposta_colonna_prioritaria(self, i):
        with self.lock:
            if i < 0 or i > self.colonne:
                print(f"COLONNA PRIORITARIA EVITATA: {i}\n")
                return
            self.colonna_prioritaria = i
            self.bool_prioritaria = True
            print(f"COLONNA PRIORITARIA: {i}\n")

    def attendi_invisibile(self):
        with self.lock:
            self.cond_estratto.wait()
            print("INVISIBILE ESTRATTO POSSO ANDARE")
            

    def put(self, elemento):
        with self.lock:
            while self.__tuttoPieno():
                self.cePostoLibero.wait()
            #
            # Per gestire l'invisibilitÃ  casuale e i meccanismi di attesa legati al Punto 3, incapsulo l'elemento in un oggetto DatiElemento
            # In questa maniera tutti questi aspetti saranno del tutto trasparenti al codice che usa la classe BanconeBar
            #
            d = DatiElemento(True if random.random() >= 0.9 else False, elemento, threading.Condition(self.lock))    
            self.bancone[random.choice(self.__getIndiciFilaPiuCorta())].append(d)
            self.ceElemento.notify_all()
        
    def get(self):
        with self.lock:
            while not self.__cisonoElementi():
                self.ceElemento.wait()
            
            if self.bool_prioritaria == False or (self.colonna_prioritaria and len(self.bancone[self.colonna_prioritaria]) == 0):
                #
                # Esploro la situazione in prima fila, raccogliendo prima la posizione dei visibili ed eventualmente quella degli invisibili
                #
                indiciDaCuiScegliere = [i for i in range(self.colonne) if len(self.bancone[i]) > 0 and not self.bancone[i][0].invisibile]
                #
                # Se non ci sono elementi visibili, prendo quelli invisibili
                #
                if len(indiciDaCuiScegliere) == 0:
                    indiciDaCuiScegliere = [i for i in range(self.colonne) if len(self.bancone[i]) > 0 and self.bancone[i][0].invisibile]
                
                
                indice_scelto = random.choice(indiciDaCuiScegliere)
                datiElemento = self.bancone[indice_scelto].pop(0)
                self.cePostoLibero.notify_all()
                datiElemento.estratto = True
                if datiElemento.monitorato:
                    datiElemento.condition.notify_all()
            else:
                datiElemento = self.bancone[self.colonna_prioritaria].pop(0)
                self.cePostoLibero.notify_all()
                datiElemento.estratto = True
                if datiElemento.monitorato:
                    datiElemento.condition.notify_all()
            if datiElemento.invisibile:
                print(f"ELEMENTO INVISIBILE = {datiElemento.elemento}")
                self.cond_estratto.notify_all()
            return datiElemento.elemento
    
    def print_bancone(self):
        with self.lock:
            for r in range(self.righe):
                for c in range(self.colonne):
                    if len(self.bancone[c]) >= r+1:
                        toPrint = self.bancone[c][r].elemento
                        #
                        # Se l'elemento Ã¨ invisibile, lo stampo in minuscolo
                        #
                        if self.bancone[c][r].invisibile:
                            toPrint = toPrint.lower()
                    else:
                        toPrint = '-'
                    print(toPrint, end = '') 
                print()

    def miglioraPosizione(self,r,c):
        with self.lock:
            #
            # Controllo che la posizione r,c sia valida
            #
            if 0 <= r < len(self.bancone[c]) and 0 <= c <= self.colonne:
                colonnaMigliore = c
                #
                # Verifico se conviene spostarmi a sinistra. 
                # La colonna adiacente deve avere almeno due elementi in meno perchÃ¨ possa convenire lo spostamento
                # Esempio: se sono quarto nella mia colonna, e ci sono tre elementi nella colonna adiacente, non conviene spostarsi, resterei sempre quarto
                #
                if c > 0 and len(self.bancone[c-1]) + 1 < len(self.bancone[colonnaMigliore]):
                    colonnaMigliore = c-1
                #
                # Verifico se conviene spostarmi a destra rispetto alla posizione corrente ma anche rispetto a un eventuale spostamento a sinistra
                #
                if c < self.colonne-1 and len(self.bancone[c+1]) + 1 < len(self.bancone[c]) and len(self.bancone[c+1]) < len(self.bancone[colonnaMigliore]):
                    colonnaMigliore = c+1
                #
                # Se tra le adiacenti ho trovato una colonna migliore, sposto l'elemento
                #
                if colonnaMigliore != c:
                    elemento = self.bancone[c].pop(r)
                    self.bancone[colonnaMigliore].append(elemento)

    def attendiServizio(self,E):
        with self.lock:
            #
            # Cerco la posizione dell'elemento che voglio monitorare
            #
            trovato = False
            for c in range(self.colonne):
                for r in range(len(self.bancone[c])):
                    #
                    # Preferisco usare 'is' a '==' perchÃ¨ mi interessa che sia proprio lo stesso oggetto a essere presente. 
                    # Ad esempio, voglio poter distinguere due istanze diverse di 'A'.
                    #
                    if self.bancone[c][r].elemento is E:
                        self.bancone[c][r].monitorato = True
                        elementoDaAttendere = self.bancone[c][r]
                        trovato = True
                        break
            if not trovato:
                return False
            while not elementoDaAttendere.estratto:
                elementoDaAttendere.condition.wait()
            return True
        
class Bancone_combinato:
    def __init__(self):
        self.B1 = bancone
        self.B2 = bancone
        #self.lock = threading.Lock()
        #self.cond_elemento = threading.Condition(self.lock)
        self.S = threading.Thread(target=self.funzionamento)
        self.S.start()

    def get(self):
        return self.B1.get()
    
    def put(self, elemento):
        return self.B2.put(elemento)
    
    def attendiElemento(self, elemento):
        return self.B1.attendiServizio(elemento)

    def funzionamento(self):
        while True:
            time.sleep(random.randint(2,5))
            elemento = self.B1.get()
            self.B2.put(elemento)



def prendi_elementi(bancone):
    while True:
        elemento = bancone.get()
        print("Elemento prelevato:", elemento)
        time.sleep(1)  # Simula un tempo di elaborazione

def inserisci_elementi(bancone):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone.put(elemento)
        print(f"Elemento inserito: {elemento}")
        if random.random() >= 0.95:
            r = random.randint(0, bancone.righe-1)
            c = random.randint(0, bancone.colonne-1)
            print(f"Provo a migliorare posizione ({r},{c})")
            bancone.miglioraPosizione(r,c)
        if random.random() >= 0.95:
            print(f"Attendo che venga servito elemento {elemento}")
            if bancone.attendiServizio(elemento):
                out = ""
            else: 
                out = "giÃ  "
            print(f"Fine attesa elemento {out}servito:", elemento)
        time.sleep(0.5)  # Simula un tempo di elaborazione

def stampa_bancone(bancone):
    while True:
        bancone.print_bancone()
        time.sleep(1)

def imposta_prioritaria(bancone):
    while True:
        time.sleep(5)
        numero = random.randint(0,10)
        bancone.imposta_colonna_prioritaria(numero)

def aspetta_invisibile(bancone):
    while True:
        bancone.attendi_invisibile()
        time.sleep(5)


def prendi_elementi2(bancone_comb):
    while True:
        elemento = bancone_comb.get()
        print("Elemento prelevato:", elemento)
        time.sleep(1)  # Simula un tempo di elaborazione

def inserisci_elementi2(bancone_comb):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone_comb.put(elemento)
        print(f"Elemento inserito: {elemento}")
        if random.random() >= 0.95:
            print(f"Attendo che venga servito elemento {elemento}")
            if bancone_comb.attendiElemento(elemento):
                out = ""
            else: 
                out = "giÃ  "
            print(f"Fine attesa elemento {out}servito:", elemento)
        time.sleep(0.5)  # Simula un tempo di elaborazione


bancone = BanconeBar(7, 5)
bancone_comb = Bancone_combinato()


#
# Un modo diverso per creare i thread senza dovere dichiarare una classe a parte,
# consiste nel passare come target una funzione che si vuole eseguire al posto del metodo run
#
'''thread_barista = threading.Thread(target=prendi_elementi, args=(bancone,))
thread_barista.start()

thread_creaClienti = threading.Thread(target=inserisci_elementi, args=(bancone,))
thread_creaClienti.start()


thread_stampab = threading.Thread(target=stampa_bancone, args=(bancone,))
thread_stampab.start()

thread_impostap = threading.Thread(target=imposta_prioritaria, args=(bancone,))
thread_impostap.start()

thread_aspettainv = threading.Thread(target=aspetta_invisibile, args=(bancone,))
thread_aspettainv.start()'''

thread_prendi2 = threading.Thread(target=prendi_elementi2, args=(bancone_comb,))
thread_prendi2.start()

thread_inserisci2 = threading.Thread(target=inserisci_elementi2, args=(bancone_comb,))
thread_inserisci2.start()