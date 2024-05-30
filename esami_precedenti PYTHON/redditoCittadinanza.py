import threading

class Cittadino:
    def __init__(self):
        self.soldiPercepiti = 0
        self.offerteRicevute = []
        self.disoccupato = True
        self.lock = threading.Lock()
    
    def offriLavoro(self, nomeLavoro : str):
        #
        # Offre un lavoro a Self. Registra l'offerta nomeLavoro 
        # in self.offerteRicevute, ma solo se disoccupato = True
        #
        with self.lock:
            if self.disoccupato:
                self.offerteRicevute.append(nomeLavoro)

    def accettaLavoro(self,nomeLavoro : str):
        #
        # se nomeLavoro appartiene a self.offerteRicevute, pone self.disoccupato = False
        #
        with self.lock:
            if nomeLavoro in self.offerteRicevute:
                self.disoccupato = False
        
    def paga(self):
        #
        # Eroga 780 EUR a self, ma solo 
        # se quest'ultimo è disoccupato e il numero di offerte ricevute non supera 3
        # incrementa soldiPercepiti in accordo
        #
        with self.lock:
            if self.disoccupato and len(self.offerteRicevute) <= 3:
                self.soldiPercepiti += 780
        
    def getPercepito(self):
        #
        # Restituisce quanto percepito finora
        #
        with self.lock:
            return self.soldiPercepiti
        
class Popolo:        
    
    def __init__ (self):
        self.soldiErogati = 0
        self.soldiDisponibili = 1000000000
        self.cittadini = []
        self.lock = threading.Lock()
        
    def distribuisciReddito(self):
        #
        # Attribuisce a tutti i componenti di self.cittadini il reddito del mese corrente (780 EUR a testa), 
        # decrementando
        # soldiDisponibili e incrementando soldiErogati. Genera una eccezione e interrompe l'operazione 
        # se 
        # durante l'operazione i soldiDisponibili dovessero finire
        #
        with self.lock:
            for cittadino in self.cittadini:
                if self.soldiDisponibili < 0:
                    raise ValueError("Soldi disponibili insufficienti")
                cittadino.paga()
                self.soldiDisponibili -= 780
                self.soldiErogati += 780

    def aggiungiSoldi(self, valore : int):
        #
        # incrementa self.soldiDisponibili dell'ammontare di 'valore'
        #
        with self.lock:
            self.soldiDisponibili += valore

    def iContiTornano(self):
        #
        # Verifica che la somma di quanto percepito dai singoli elementi di self.cittadini corrisponda a self.soldiErogati
        # restituisce un valore booleano in accordo
        #
        with self.lock:
            totale_percepito = 0
            for cittadino in self.cittadini:
                totale_percepito += cittadino.getPercepito()
            if totale_percepito == self.soldiErogati:
                return True
            else:
                return False
            

def worker(popolo, cittadino):
    # Simula l'offerta di lavoro e l'accettazione del lavoro da parte del cittadino
    cittadino.offriLavoro("Lavoro1")
    cittadino.accettaLavoro("Lavoro1")

    # Simula la distribuzione del reddito
    try:
        popolo.distribuisciReddito()
        print(f"Cittadino {threading.current_thread().name}: Reddito distribuito con successo\n")
    except ValueError as e:
        print(f"Cittadino {threading.current_thread().name}: Errore nella distribuzione del reddito - {e}\n")

    # Verifica se i conti tornano
    if popolo.iContiTornano():
        print(f"Cittadino {threading.current_thread().name}: I conti tornano\n")
    else:
        print(f"Cittadino {threading.current_thread().name}: I conti non tornano\n")

def main():
    # Creazione di un oggetto Popolo
    popolo = Popolo()

    # Creazione di alcuni cittadini
    cittadino1 = Cittadino()
    cittadino2 = Cittadino()
    cittadino3 = Cittadino()

    # Aggiunta dei cittadini alla popolazione
    popolo.cittadini.extend([cittadino1, cittadino2, cittadino3])

    # Creazione di thread per simulare l'interazione dei cittadini con il sistema
    thread1 = threading.Thread(target=worker, args=(popolo, cittadino1), name="1")
    thread2 = threading.Thread(target=worker, args=(popolo, cittadino2), name="2")
    thread3 = threading.Thread(target=worker, args=(popolo, cittadino3), name="3")

    # Avvio dei thread
    thread1.start()
    thread2.start()
    thread3.start()

    # Attendi che tutti i thread abbiano completato l'esecuzione
    thread1.join()
    thread2.join()
    thread3.join()

    # Stampa lo stato finale
    print(f"\nStato finale:\nSoldi erogati: {popolo.soldiErogati}\nSoldi disponibili: {popolo.soldiDisponibili}\n")
    for idx, cittadino in enumerate(popolo.cittadini, 1):
        print(f"Cittadino {idx}: Soldi percepiti = {cittadino.getPercepito()}\n")

if __name__ == "__main__":
    main()
