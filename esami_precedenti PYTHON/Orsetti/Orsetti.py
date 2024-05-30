import threading
import random
import time

class VasettoDiMiele:
    def __init__(self, indice, capacita):
        self.capacita = capacita
        self.miele = capacita
        self.indice = indice
        self.in_mano = 0
        self.mangiato = 0
        self.mamma_block = False
        self.lock = threading.RLock()
        self.condition_aumento = threading.Condition(self.lock)
        self.condition_diminuzione = threading.Condition(self.lock)

    #
    # Si sblocca solo quando il vasetto è completamente vuoto
    #
    def riempi(self):
        with self.lock:
            # se il vasetto di miele è già pieno esci
            if self.miele == self.capacita:
                return
            # se il vasetto non è vuoto
            while self.miele > 0:
                self.mamma_block = True
                print(f"Il vasetto {self.indice} ha {self.miele} unità  di miele, aspetto che si svuoti completamente\n")
                # aspetta fin quando non è vuoto
                self.condition_diminuzione.wait()
            # se è vuoto, viene riempito
            self.miele = self.capacita
            self.mamma_block = False
            # e tutti i thread in attesa vengono avvisati
            self.condition_aumento.notify_all()
            print(f"{threading.current_thread().name} ha rabboccato il vasetto {self.indice}\n")

    #
    # Preleva del miele dal vasetto
    #
    def prendi(self, quantita):
        with self.lock:
            # se il vasetto non ha la quantità di miele richiesta
            while self.miele < quantita:
                print(f"Il vasetto {self.indice} ha {self.miele} unità  di miele, non è possibile prendere {quantita}. Aspetto che il vasetto venga riempito\n")
                # aspetta fin quando non ha la quantità necessaria di miele
                self.condition_aumento.wait()
            if isinstance(threading.current_thread(), PapaOrsoThread):
                # Se il chiamante è un papa orso, incrementa il contatore miele_in_mano
                self.in_mano += quantita
            if isinstance(threading.current_thread(), OrsettoThread):
                self.mangiato += quantita
            # se ha la quantità richiesta, viene preso il miele
            self.miele -= quantita
            print(f"Orsetto {threading.current_thread().name} ha preso {quantita} unità  di miele dal vasetto {self.indice}\n")
            # vengono avvisati tutti i thread in attesa che è stato preso del miele
            self.condition_diminuzione.notify_all()

    #
    # Aggiunge del miele dal vasetto
    #
    def aggiungi(self, quantita):
        with self.lock:
            if self.mamma_block == True:
                return
            # se il miele da aggiungere supera la capacità del vasetto
            while self.miele + quantita > self.capacita:
                print(f"Il vasetto {self.indice} ha {self.miele} unità  di miele, aggiungerne {quantita} supererebbe la capacità  massima di {self.capacita}\n")
                # aspetta fin quando la quantità desiderata può essere aggiunta
                self.condition_diminuzione.wait()
            if isinstance(threading.current_thread(), PapaOrsoThread):
                # Se il chiamante è un papa orso, incrementa il contatore miele_in_mano
                self.in_mano -= quantita
            # la quantità di miele può essere aggiunta al vasetto
            self.miele += quantita
            print(f"Orso {threading.current_thread().name} ha aggiunto {quantita} unità  di miele al vasetto {self.indice}\n")
            # vengono avvisati i thread in attessa che è stato aggiunto del miele
            self.condition_aumento.notify_all()

# orsetto normale
class OrsettoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            # vasetto casuale
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            # quantità di miele da prendere
            quantita = random.randint(1,self.vasettiMiele[vasetto_indice].capacita)
            # prendono il miele dal vasetto
            self.vasettiMiele[vasetto_indice].prendi(quantita)

# papà orso
class PapaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def vasetto_in_mano(self):
        # Restituisci la quantità di miele temporaneamente in mano al papa orso
        return sum(vasetto.in_mano for vasetto in self.vasettiMiele)

    def run(self):
        while True:
            # vasetto da cui prendere il miele
            vasetto_indice1 = random.randint(0, len(self.vasettiMiele)-1)
            # vasetto a cui aggiungere miele
            vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)

            # in modo che i vasetti non siano uguali
            while vasetto_indice1 == vasetto_indice2:
                vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)
            
            # se i vasetti sono diversi, genera una quantità di miele
            quantita = random.randint(1, self.vasettiMiele[vasetto_indice1].capacita)
            # chiama il metodo prendi sul vasetto1
            self.vasettiMiele[vasetto_indice1].prendi(quantita)
            # chiama il metodo aggiungi sul vasetto2
            self.vasettiMiele[vasetto_indice2].aggiungi(quantita)
            print(f"Papa orso {self.name} ha spostato {quantita} grammi dal vasetto {vasetto_indice1} al vasetto {vasetto_indice2}\n")

# mamma orso
class MammaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            # vasetto casuale
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            # riempiono il vasetto
            self.vasettiMiele[vasetto_indice].riempi()
            print(f"Mamma orso {self.name} ha riempito il vasetto {vasetto_indice}\n")

def totaleMiele(vasetti, papa_orso):
    with threading.Lock():
        miele_totale = sum(vasetto.miele for vasetto in vasetti)
        mangiato_totale = sum(vasetto.mangiato for vasetto in vasetti)
        in_mano_totale = sum(papa.vasettiMiele[0].in_mano for papa in papa_orso)

        print(f"Quantità totale di miele nei vasetti: {miele_totale} unità")
        print(f"Quantità totale di miele mangiato: {mangiato_totale} unità")
        print(f"Quantità totale di miele in mano ai papa orsi: {in_mano_totale} unità")

if __name__ == '__main__':
    num_vasetti = 5
    vasetti = [VasettoDiMiele(i,50+50*i) for i in range(num_vasetti)]

    orsetti = [OrsettoThread(f"Winnie-{i}", vasetti) for i in range(5)]
    mamme_orse = [MammaOrsoThread(f"Mamma-{i}",vasetti) for i in range(2)]
    papa_orso = [PapaOrsoThread(f"Babbo-{i}", vasetti) for i in range(3)]

 
    for orsetto in orsetti:
        orsetto.start()
 
    for orsa in mamme_orse:
        orsa.start()

    for orso in papa_orso:
        orso.start()

    time.sleep(10)

    totaleMiele(vasetti, papa_orso)