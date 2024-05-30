from threading import Thread,Condition,RLock
from time import sleep
import random

'''
Punto 1
Arricchisci la classe TorreInCostruzione con il metodo waitForStrato(S : int). Tale metodo pone in
attesa il thread chiamante fintantoché gli operai non completano lo strato S. Se S è maggiore dell altezza finale H della
torre, arrotonda S ad H.

Punto 2
Nota che il codice fornito stampa periodicamente l intero array che rappresenta la Torre. Rimuovi questa stampa e
introduci un Thread che, sfruttando il metodo waitForStrato, stampi periodicamente, a passi arrotondati al 10%,
quanta percentuale della Torre è stata correntemente realizzata. Decidi tu come gestire gli arrotondamenti tra il numero di
strati conclusi e la percentuale di completamento. L output prodotto da questo thread deve essere una sequenza di linee
che dicono “10% completato” - “20% completato” - “30% completato” … ecc.

Punto 3
Introduci il metodo aggiungiStratoUrgente(s : str). Tale metodo può essere invocato durante la
costruzione di una Torre, e istanzia due nuovi Operai capaci di aggiungere il carattere s (con un ritardo di 100ms tra una
posa e l altra) a una TorreInCostruzione. I due nuovi operai dovranno lavorare insieme per aggiungere, non appena sia
completo lo strato in corso, un nuovo strato fatto di s alla TorreInCostruzione, sospendendo la normale alternanza tra
Mattonatori e Cementatori. I due nuovi thread dovranno poi terminare al completamento dello strato aggiuntivo, mentre
la costruzione della torre deve riprendere normalmente. L altezza finale della Torre sarà aumentata da H ad H+1
'''

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
        self.torre = ['']                    # il primo strato sarÃ  self.torre[0], inizialmente impostato a ''
        self.tipoStratoAttualmenteUsato = 0  # modalitÃ  iniziale = cemento, poichÃ¨ self.tipiStrato[0] = '-'
        self.terminato = False               # imposteremo self.terminato = True quando la Torre sarÃ  completa
        self.lock = RLock()
        self.attendiTurno = Condition(self.lock)
        self.attendiFine = Condition(self.lock)
        self.straordinario = False
        self.cond_urgente = Condition(self.lock)
        self.stringa_straordinaria = ''
        self.strato_straordinario = self.altFinale+1 #valore giusto per inizializzare
        self.ultimo = 0
        

    def printTorre(self):
        prints(self.torre)

    def attendiTerminazione(self):
        with self.lock:
            while not self.terminato:
                self.attendiFine.wait()

    def addPezzo(self,c) -> bool:
        with self.lock:
            '''
                Se non Ã¨ il mio turno AND la torre Ã¨ da finire -> aspetto
                Se Ã¨ il mio turno OR la torre Ã¨ finita -> non aspetto
                Dopo avere atteso, controllo se per caso non ci sono pezzetti da aggiungere: in tal caso pongo Terminato = True, esco e restituisco False;
                Altrimenti aggiungo il mio pezzetto e restituisco True 
            '''

            while self.tipiStrato[self.tipoStratoAttualmenteUsato] != c and not self.terminato:
                self.attendiTurno.wait()
            
            while self.straordinario:
                self.attendiTurno.wait()

            if self.stratoAttuale == self.altFinale - 1 and len(self.torre[self.stratoAttuale]) == self.larghezzaFinale:
                self.terminato = True
                self.attendiTurno.notifyAll()
                self.attendiFine.notifyAll()
                return False
            
            self.torre[self.stratoAttuale] = self.torre[self.stratoAttuale] + c
            if len(self.torre[self.stratoAttuale]) == self.larghezzaFinale and self.stratoAttuale < self.altFinale - 1:
                self.stratoAttuale += 1
                self.torre.append( '' ) # predispongo il prossimo strato
                if self.stringa_straordinaria == '':
                    self.tipoStratoAttualmenteUsato = (self.tipoStratoAttualmenteUsato + 1) % 2
                    self.attendiTurno.notifyAll()
                else:
                    self.ultimo = self.tipoStratoAttualmenteUsato
                    self.straordinario = True
                    self.cond_urgente.notify_all()

            #self.printTorre()

            return True

    def waitForStrato(self, S : int):
        with self.lock:
            if S > self.altFinale:
                S = self.altFinale
            while self.stratoAttuale < S:
                print(f"L'OPERAIO ASPETTA CHE SI ARRIVI ALLO STRATO {S}\n")
                perc_att = (self.stratoAttuale/self.altFinale)*100
                perc_int = int(perc_att)
                print(f"{perc_int}% COMPLETATO")
                self.attendiTurno.wait()
            print(f"ARRIVATI ALLO STRATO {S}. L'OPERAIO PUO LAVORARE\n")

    def aggiungiStratoUrgente(self, s : str) -> bool:
        with self.lock:
            if self.stratoAttuale > self.strato_straordinario:
                return False
            
            if self.stringa_straordinaria == '':
                self.altFinale += 1
                self.stringa_straordinaria = s
                self.strato_straordinario = self.stratoAttuale+1

            while self.straordinario == False:
                self.cond_urgente.wait()

            self.torre[self.stratoAttuale] = self.torre[self.stratoAttuale] + s
            if len(self.torre[self.stratoAttuale]) == self.larghezzaFinale and self.stratoAttuale < self.altFinale - 1:
                self.stratoAttuale += 1
                self.torre.append( '' ) # predispongo il prossimo strato 
                self.tipoStratoAttualmenteUsato = (self.ultimo + 1) % 2
                self.straordinario = False
                self.stringa_straordinaria = ''
                self.attendiTurno.notifyAll()

            return True
            
            
            

class Operaio(Thread):
    def __init__(self,t : TorreInCostruzione, tp : str, d:int):
        super().__init__()
        self.torre = t
        self.tipo = tp
        self.durata = d
    
    def run(self):
        attesa = random.randint(1,5)
        if attesa == 5:
            numero = random.randint(1,100)
            self.torre.waitForStrato(numero)
        while(self.torre.addPezzo(self.tipo)):
            sleep(self.durata/1000)
        prints("Thread di tipo: '%s' finito" % self.tipo) 
           
class Cementatore(Operaio):
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'-',25)

class Mattonatore(Operaio):
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'*',50)
    
class Straordinario(Thread):
    def __init__(self,t : TorreInCostruzione, tp : str, d:int):
        super().__init__()
        self.torre = t
        self.tipo = tp
        self.durata = d
    
    def run(self):
        while(self.torre.aggiungiStratoUrgente(self.tipo)):
            sleep(self.durata/1000)
        prints("Thread di tipo: '%s' finito" % self.tipo)
        #return



class Torre:
    
    def __init__(self):
        pass
        
        
    def makeTorre(self,H:int, M:int, C:int, S : int): 
        t = TorreInCostruzione(H)
        Mattonatori = [Mattonatore(t) for _ in range(M)]
        Cementatori = [Cementatore(t) for _ in range(C)]
        Straordinari = [Straordinario(t, '&', 100) for _ in range (S)]
        for m in Mattonatori:
            m.start()
        for c in Cementatori:
            c.start()
        sleep(random.randint(0,1)) #serve solo per provare che funziona l'aggiunta di straordinari in ogni punto della torre
        for s in Straordinari:
            s.start()
        t.attendiTerminazione()
        return t.torre
        
if __name__ == '__main__':
    T = Torre()
    print (T.makeTorre(90,4,7,2)) 
    prints("TORRE FINITA")
    