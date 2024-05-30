import threading
import time
import random

'''
Punto 1.
Come primo punto, modifica ogni VasettoDiMiele in maniera da ottimizzare l uso delle condition e non risvegliare
inutilmente più thread del necessario. In particolare, rimuovi la condition esistente e introduci una
condition_aumento, da usare quando si aspetta che il vasetto aumenti il suo contenuto e una
condition_diminuzione, da usare quando si aspetta che il vasetto diminuisca il suo contenuto. Puoi anche
ottimizzare il codice a tua scelta introducendo più di due condition, se lo ritieni opportuno.

Punto 2
Avrai notato che è molto difficile che le mamme orse riescano a rabboccare un vasetto di miele, poiché è necessario che un
vasetto di miele sia completamente vuoto. Per risolvere il problema, fai in modo che quando almeno una mamma orsa è
bloccata all interno del metodo riempi, nessun papà orso possa aggiungere del miele. Inoltre, quando una mamma orsa
invoca il metodo riempi, ma il vaso è già pieno fino all orlo, bisogna uscire immediatamente anziché aspettare.

Punto 3
Implementa una funzione totaleMiele() che stampa a video la quantità di miele attualmente presente in tutti i
vasetti, e la quantità che è stata finora mangiata da qualcuno. Bonus: osserva che potrebbero esserci delle quantità di
miele temporaneamente fuori dai vasetti, poiché nelle mani di un papà orso nell intervallo di tempo tra prendi() e
aggiungi(). Puoi fare in modo che totaleMiele() tenga conto anche di queste quantità?

'''

class VasettoDiMiele:
    def __init__(self, indice, capacita):
        self.capacita = capacita
        self.miele = capacita
        self.indice = indice
        self.mangiata = 0
        self.nelle_mani = 0
        self.lock = threading.RLock()
        self.condition_aumento = threading.Condition(self.lock)
        self.condition_diminuizione = threading.Condition(self.lock)
        self.condition_papa = threading.Condition(self.lock)
        self.mamma_dentro = False

    #
    # Si sblocca solo quando il vasetto Ã¨ totalmente vuoto
    #
    def riempi(self):
        with self.lock:
            while self.miele > 0:
                if self.miele == self.capacita:
                    return
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aspetto che si svuoti completamente\n")
                self.condition_aumento.wait()
            self.mamma_dentro = True
            print(f"MAMMA STA RIEMPIENDO\n")
            self.miele = self.capacita
            print(f"MAMMA HA FINITO\n")
            self.mamma_dentro = False
            self.condition_papa.notify_all()
            self.condition_diminuizione.notify_all()
            print(f"{threading.current_thread().name} ha rabboccato il vasetto {self.indice}")

    #
    # Preleva del miele dal vasetto
    #
    def prendi(self, quantita):
        with self.lock:
            while self.miele < quantita:
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, non Ã¨ possibile prendere {quantita}. Aspetto che il vasetto venga riempito\n")
                self.condition_diminuizione.wait()
            self.miele -= quantita
            if "Winnie" in threading.current_thread().name:
                self.mangiata += quantita
            else:
                self.nelle_mani += quantita
            print(f"Orsetto {threading.current_thread().name} ha preso {quantita} unitÃ  di miele dal vasetto {self.indice}\n")
            self.condition_aumento.notify_all()

    def aggiungi(self, quantita):
        with self.lock:
            while self.mamma_dentro:
                print(f"PAPA' ASPETTA MAMMA\n")
                self.condition_papa.wait()
            while self.miele + quantita > self.capacita:
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aggiungerne {quantita} supererebbe la capacitÃ  massima di {self.capacita}\n")
                self.condition_aumento.wait()
            self.miele += quantita
            self.nelle_mani -= quantita
            print(f"Orso {threading.current_thread().name} ha aggiunto {quantita} unitÃ  di miele al vasetto {self.indice}\n")
            self.condition_diminuizione.notify_all()

    def totaleMiele(self):
        with self.lock:
            print(f"IL VASETTO {self.indice} HA ATTUALMENTE {self.miele} QUANTITA'", end=" ")
            print(f", E' STATA MANGIATO {self.mangiata} MIELE",end=" ")
            print(f", E NELLE MANI DEI PAPA' C'E' ATTUALMENTE {self.nelle_mani} MIELE\n")


class OrsettoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            quantita = random.randint(1,self.vasettiMiele[vasetto_indice].capacita)
            self.vasettiMiele[vasetto_indice].prendi(quantita)

class PapaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice1 = random.randint(0, len(self.vasettiMiele)-1)
            vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)
            while vasetto_indice1 == vasetto_indice2:
                vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)
            quantita = random.randint(1, self.vasettiMiele[vasetto_indice1].capacita)
            self.vasettiMiele[vasetto_indice1].prendi(quantita)
            self.vasettiMiele[vasetto_indice2].aggiungi(quantita)
            print(f"Papa orso {self.name} ha spostato {quantita} grammi dal vasetto {vasetto_indice1} al vasetto {vasetto_indice2}\n")

class MammaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            self.vasettiMiele[vasetto_indice].riempi()
            print(f"Mamma orso {self.name} ha riempito il vasetto {vasetto_indice}\n")

class Stampatore_miele(threading.Thread):
    def __init__(self,vasetti):
        threading.Thread.__init__(self)
        self.vasetti = vasetti

    def run(self):
        while True:
            for i in range(num_vasetti):
                vasetti[i].totaleMiele()
            time.sleep(2)

if __name__ == '__main__':
    num_vasetti = 5

    vasetti = [VasettoDiMiele(i,50+50*i) for i in range(num_vasetti)]

    orsetti = [OrsettoThread(f"Winnie-{i}", vasetti) for i in range(5)]
    mamme_orse = [MammaOrsoThread(f"Mamma-{i}",vasetti) for i in range(2)]
    papa_orso = [PapaOrsoThread(f"Babbo-{i}", vasetti) for i in range(3)]

    for orsa in mamme_orse:
        orsa.start()

    for orsetto in orsetti:
        orsetto.start()

    for orso in papa_orso:
        orso.start()
    
    stampatore = Stampatore_miele(vasetti)
    stampatore.start()