import random, time, os
from threading import Thread,Condition,RLock, get_ident
from queue import Queue

#
# Una sede sarà formata da tanti Uffici
#
class Ufficio:
    def __init__(self,l):
        Thread.__init__(self)
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.lettera = l
        self.ticketDaRilasciare = 0
        self.ticketDaServire = 0

    #
    # Fornisce un ticket formattato abbinando correttamente lettera e numero
    #
    def formatTicket(self,lettera,numero):
        return "%s%03d" % (lettera, numero)
    
    #
    # Restituisce quanti ticket in attesa ci sono in questo ufficio
    #
    def getTicketInAttesa(self):
        with self.lock:
            return self.ticketDaRilasciare - self.ticketDaServire

    #
    # Invocato da un utente  quando deve prendere un numerino
    #
    def prendiProssimoTicket(self):
        with self.lock:
            #
            # self.ticketDaRilasciare e self.ticketDaServire stanno per diventare diversi e cioè ci sono utenti da smaltire
            #
            if (self.ticketDaRilasciare <= self.ticketDaServire):
                self.condition.notify_all()
            self.ticketDaRilasciare+=1
            
            return self.formatTicket(self.lettera, self.ticketDaRilasciare)

    #
    # Invocato da un impiegato quando deve chiamare la prossima persona
    #
    def chiamaProssimoTicket(self):
        with self.lock:
            #
            # Non ci sono ticket in attesa da elaborare. Attendo
            #
            while(self.ticketDaRilasciare <= self.ticketDaServire):
                self.condition.wait()

            self.ticketDaServire+=1
            
            return self.formatTicket(self.lettera, self.ticketDaServire)
                
 
class Sede:

    def __init__(self,n):
        self.n = n
        #
        # Gestiremo gli n uffici con un dizionario. Esempio: per selezionare l'ufficio "C" si usa self.uffici["C"]
        #
        self.uffici = {} 
        for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:n]:
            self.uffici[l] = Ufficio(l) 
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.ultimiTicket = []
        self.ultimiSize = 5
        self.update = False
        self.setPrintAttese = False

    #
    # Preleva ticket da rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio
    #
    def prendiTicket(self,uff):
        return self.uffici[uff].prendiProssimoTicket()
    
    def incDecSizeUltimi(self, n):
        with self.lock:
            if n < 0 and -n >= len(self.ultimiTicket):
                return
            self.ultimiSize += n

    #
    # Chiama ticket del rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio e poi si aggiorna l'elenco degli ultimi ticket con il lock di SEDE
    #
    def chiamaTicket(self,uff):
        ticket = self.uffici[uff].chiamaProssimoTicket()
        with self.lock:
            self.condition.notify_all()
            #
            # Questo aggiornamento serve a far capire al display che ci sono novità  da stampare a video
            #
            self.update = True
            if(len(self.ultimiTicket) >= self.ultimiSize):
                self.ultimiTicket.pop()
            self.ultimiTicket.insert(0,ticket)
            

    def waitForTicketSafe(self,ticket):
        with self.lock:
            if ticket in self.ultimiTicket:
                return True
            else:
                while ticket not in self.ultimiTicket:
                    self.condition.wait()
                return True
            
    def waitForTickets(self, L):
        with self.lock:
            while not any(ticket in self.ultimiTicket for ticket in L):
                self.condition.wait()
            return True

    #
    # Serve a segnalare al display di stampare il riepilogo
    #
    def printAttese(self):
        with self.lock:
            self.setPrintAttese = True
        
    #
    #  Stampa gli ultimi numeri chiamati
    #
    def printUltimi(self):
        with self.lock:
            while not self.update:
                self.condition.wait()
            self.update = False
            #os.system('clear')
            #
            # Se qualcuno lo ha chiesto, stampo l'elenco degli utenti in coda per ogni ufficio
            #
            if (self.setPrintAttese):
                for u in self.uffici:
                    print("%s : %d" % (self.uffici[u].lettera, self.uffici[u].getTicketInAttesa()))
                self.setPrintAttese = False
            for t in self.ultimiTicket:
                print(t)
            print ("="*10)
            

class Utente(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        while True:
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}\n")
            time.sleep(random.randint(1,3))
            print(f"Sono l'utente {get_ident()}, ho preso un caffè e adesso aspetto il mio ticket: {ticket}\n") 
            
            if not self.sede.waitForTicketSafe(str(ticket)):
                print(f"Sono l'Utente {get_ident()}, il mio ticket {ticket} è stato chiamato troppo tempo fa o è scaduto.\n")

class UtenteFurbetto(Thread):
    def __init__(self, sede, uffici):
        Thread.__init__(self)
        self.sede = sede
        self.uffici = uffici

    def run(self):
        while True:
            tickets = [self.sede.prendiTicket(ufficio) for ufficio in self.uffici]
            print(f"Sono L'Utente furbetto {get_ident()}, ho preso i ticket {tickets}\n")

            if not self.sede.waitForTickets(map(str, tickets)):
                print(f"Sono l'Utente furbetto {get_ident()}, nessuno dei miei {tickets} è più chiamabile.\n")
                break
            
            time.sleep(random.randint(1, 3))



class Impiegato(Thread):
    def __init__(self, sede, lettera):
        Thread.__init__(self)
        self.sede = sede
        self.ufficio = lettera
 
    def run(self):
        while True:
            self.sede.chiamaTicket(self.ufficio)
            #
            # Simula un certo tempo in cui l'impiegato serve l'utente appena chiamato
            #
            time.sleep(random.randint(1,4))
            #
            # Notifica di voler stampare il riepilogo attese 
            #
            if random.randint(0,5) >= 4:
                self.sede.printAttese()


class Display(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        

    def run(self):
        while True:
            self.sede.printUltimi()
            
class TestThread(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede

    def run(self):
        for i in range(5):
            # Incrementa la dimensione di ultimiTicket di 2
            self.sede.incDecSizeUltimi(2)
            print(f"Nuova dimensione di ultimiTicket: {self.sede.ultimiSize}\n")
            time.sleep(1)

            # Decrementa la dimensione di ultimiTicket di 1
            self.sede.incDecSizeUltimi(-1)
            print(f"Nuova dimensione di ultimiTicket: {self.sede.ultimiSize}\n")
            time.sleep(1)

sede = Sede(6)

display = Display(sede)
display.start()


utenti = [Utente(sede) for p in range(10)]
impiegato = [Impiegato(sede, i) for i in "ABCDEF"]
utente_furbetto = UtenteFurbetto(sede, ["B", "F", "D"])
test_thread = TestThread(sede)


for p in utenti + impiegato + [utente_furbetto]:
    p.start()

test_thread.start()