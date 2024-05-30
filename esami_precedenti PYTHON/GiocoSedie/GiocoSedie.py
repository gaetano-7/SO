from threading import Thread, Lock, current_thread
from time import sleep
from random import random, randrange

'''
    Versione del gioco delle sedie con una matrice di posti. 
   
    Rispetto all'esempio che viene fatto tradizionalmente in ogni edizione del corso:
     - i partecipanti lavorano su una matrice di sedie anziche su una lista, al fine di simulare la prenotazione dei posti di una sala con un numero di posti disposti in griglia quadrata (LATOSALA = numero file).
     - la stampa tiene conto della presenza di una matrice quadrata;
     - il PartecipanteSafe sceglie un posto casuale;
     - Vi ho lasciato il codice della soluzione A e della soluzione B per come fatto a lezione, per ricordarvi le cose che NON SI DEVONO fare, ma la traccia di esame sarÃ  basata sulla soluzione C.

'''

class PostoSafe:
    def __init__(self):
        self.occupato = False
        self.lock = Lock()

    def libero(self):
        with self.lock:
            return not self.occupato

    def testaEoccupa(self):
        with self.lock:
            if not self.occupato:
                self.occupato = True
                return True
            return False
        
class Sala:
    def __init__(self, latosala):
        self.posti = [[PostoSafe() for _ in range(latosala)] for _ in range(latosala)]
        self.latosala = latosala
        self.display_lock = Lock()
        self.tentativi = set()  # Aggiungi questa linea
        self.tentativi_lock = Lock()  # Aggiungi questa linea

    def testaEoccupa(self, i, j):
        if 0 <= i < self.latosala and 0 <= j < self.latosala:
            return self.posti[i][j].testaEoccupa()
        return False

    def trovaPosto(self):
        for i in range(self.latosala):
            for j in range(self.latosala):
                if self.posti[i][j].libero() and self.testaEoccupa(i, j):
                    return i, j
        return -1, -1

    def stampaSala(self):
        with self.display_lock:
            print(f"+{'-' * (self.latosala * 2)}+")
            for i in range(self.latosala):
                row = "|"
                for j in range(self.latosala):
                    if self.posti[i][j].libero():
                        row += ". "
                    else:
                        row += "o "
                row += "|"
                print(row)
            print(f"+{'-' * (self.latosala * 2)}+")

class PartecipanteSafe(Thread):
    def __init__(self, sala):
        super().__init__()
        self.sala = sala

    def run(self):
        while True:
            sleep(randrange(1))
            i, j = self.sala.trovaPosto()
            if i != -1 and j != -1:
                print(f"Sono il Thread {current_thread().name}. Occupo il posto ({i},{j})\n")
                return
            with self.sala.tentativi_lock:
                tentativo = (i, j)
                if tentativo not in self.sala.tentativi:
                    self.sala.tentativi.add(tentativo)
                if len(self.sala.tentativi) == self.sala.latosala * self.sala.latosala:
                    print(f"Sono il Thread {current_thread().name}. Sala piena. HO PERSO\n")
                    return


class Display(Thread):
    def __init__(self, sala, partecipanti):
        super().__init__()
        self.sala = sala
        self.partecipanti = partecipanti

    def run(self):
        while any(t.is_alive() for t in self.partecipanti):
            sleep(1)
            self.sala.stampaSala()

# Funzione che crea e avvia i thread
def main():
    LATOSALA = 10
    sala = Sala(LATOSALA)

    partecipanti = []
    for i in range(LATOSALA * LATOSALA + 5):
        t = PartecipanteSafe(sala)
        t.setName(f"Spettatore-{i}")
        t.start()
        partecipanti.append(t)

    lg = Display(sala, partecipanti)
    lg.start()

    # Attendi che tutti i thread PartecipanteSafe terminino
    for t in partecipanti:
        t.join()

    # Attendi che il thread Display termini
    lg.join()

if __name__ == "__main__":
    main()