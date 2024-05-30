import random, time, os
from threading import Thread,Condition,RLock, get_ident
from queue import Queue

'''
Punto 1:
Si noti che il metodo waitForTicket(self,ticket) può rimanere in attesa all infinito qualora venisse invocato troppo
in ritardo da un thread utente. In particolare questa anomalia si può verificare se waitForTicket viene invocata se
ticket è stato ormai chiamato ed è infine sparito dalla lista degli ultimi cinque ticket chiamati. Si modifichi il codice di
Utente in maniera tale da verificare che l errore sia effettivamente possibile; si programmi quindi una nuova versione di
waitForTicket, chiamata waitForTicketSafe che abbia lo stesso identico comportamento (e cioè si va in attesa
bloccante finchè il ticket in input non viene chiamato), salvo che si restituisce True se il ticket è stato effettivamente
chiamato oppure si trova nella lista degli ultimi ticket. Se invece ticket è stato chiamato da molto tempo, e dunque non
risulta più negli ultimi cinque ticket chiamati, bisogna, anziché finire in attesa indefinita, restituire False.
Si programmi infine un UtenteSafe che usi il nuovo metodo waitForTicketSafe anziché il precedente
waitForTicket e se ne verifichi il funzionamento corretto.

Punto 2:
Si noti che è possibile prendere ticket da più di un ufficio contemporaneamente, ad esempio lo spezzone di codice:
ticket1 = self.sede.prendiTicket("B"))
ticket2 = self.sede.prendiTicket("F"))
ticket3 = self.sede.prendiTicket("D"))
Consente di prelevare tre ticket da tre differenti uffici in sequenza. Si introduca il metodo
waitForTickets(self, L : List)
Questo metodo prende in input una lista L di ticket, e si mette in attesa contemporanea di tutti i ticket presenti in L. Il
metodo esce restituendo True quando uno qualsiasi dei ticket presenti in L risulta presente in self.ultimiTicket.
Analogamente al metodo waitForTicketSafe, bisogna restituire False se nessun ticket presente in L risulta ormai
chiamabile (poiché chiamato in passato e ormai non presente in self.ultimiTicket).
Si programmi un thread UtenteFurbetto pensato per testare il nuovo metodo.

Punto 3:
Si introduca il metodo incDecSizeUltimi(self,n : int).
Tale metodo incrementa (o diminuisce, a seconda del segno di n) la dimensione di self.ultimiTicket .
Se n < 0 and -n >= len(self.ultimiTicket) l operazione deve essere ignorata. Si verifichi che tutto il
codice pre-esistente tenga conto del fatto che la taglia di self.ultimiTicket possa variare, facendo le eventuali
modifiche. Si programmi un thread di test del nuovo metodo introdotto
'''

#
# Una sede sarÃ  formata da tanti Uffici
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
            # self.ticketDaRilasciare e self.ticketDaServire stanno per diventare diversi e cioÃ¨ ci sono utenti da smaltire
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
        self.size_ultimiTicket = 5
        self.chiamati = []
        self.update = False
        self.setPrintAttese = False

    #
    # Preleva ticket da rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio
    #
    def prendiTicket(self,uff):
        return self.uffici[uff].prendiProssimoTicket()

    #
    # Chiama ticket del rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio e poi si aggiorna l'elenco degli ultimi ticket con il lock di SEDE
    #
    def chiamaTicket(self,uff):
        ticket = self.uffici[uff].chiamaProssimoTicket()
        with self.lock:
            self.condition.notifyAll()
            #
            # Questo aggiornamento serve a far capire al display che ci sono novitÃ  da stampare a video
            #
            self.update = True
            if len(self.ultimiTicket) > 0:
                if(len(self.ultimiTicket) >=self.size_ultimiTicket):
                    if self.size_ultimiTicket != 0:
                        while len(self.ultimiTicket) >= self.size_ultimiTicket:
                            self.ultimiTicket.pop()
                    else:
                        while len(self.ultimiTicket) > self.size_ultimiTicket:
                            self.ultimiTicket.pop()
            self.ultimiTicket.insert(0,ticket)
            self.chiamati.append(ticket)
            

    def waitForTicket(self,ticket):
        with self.lock:
            while(ticket not in self.ultimiTicket):
                self.condition.wait()

    def waitForTicketSafe(self, ticket):
        with self.lock:
            while(ticket not in self.chiamati):
                #print(f" IL TICKET: {ticket} NON E' STATO ANCORA CHIAMATO\n")
                self.condition.wait()
            if ticket not in self.ultimiTicket:
                print(f"TICKET {ticket} CHIAMATO TROPPO IN RITARDO")
                return False
            else:
                print(f"TICKET {ticket} CHIAMATO")
                return True
            
    def waitForTickets(self, L : list):
        with self.lock:
            set1 = set(self.chiamati)
            set2 = set(self.ultimiTicket)
            set3 = set(L)
            while not set3 & set1:
                print(f" NESSUN TICKET E' STATO ANCORA CHIAMATO\n")
                self.condition.wait()
            if not set3 & set2:
                print(f"TICKET CHIAMATI TROPPO IN RITARDO\n")
            else:
                print(f"TICKET TRAMITE LISTA CHIAMATO\n")
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
            if self.size_ultimiTicket > 0:
                for t in self.ultimiTicket:
                    print(t)
                print ("="*10)

    def incDecSizeUltimi(self, n : int):
        with self.lock:
            if n < 0 and -n >= len(self.ultimiTicket):
                print(f"{n} NON RIENTRA NEL RANGE\n")
            else:
                print(f"SIZE CAMBIATA IN {n}\n")
                self.size_ultimiTicket = n
            



class Utente(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        while True:
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
            time.sleep(random.randint(1,3))
            print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}") 
            self.sede.waitForTicket(str(ticket))

class UtenteSafe(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
        print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
        time.sleep(random.randint(1,3))
        print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}") 
        self.sede.waitForTicketSafe(str(ticket))
    
class UtenteFurbetto(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.lista = []
        self.n = 3
        self.n = len(sede.uffici)

    def run(self):
        for i in range(self.n):
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            #print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
            time.sleep(random.randint(1,3))
            #print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}") 
            #self.sede.waitForTicketSafe(str(ticket))
            self.lista.append(ticket)
        for i in range(self.n):
            print(f"POSSIEDO TICKET: {self.lista[i]}", end=" ")
        self.sede.waitForTickets(self.lista)

class ChangeSize(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede

    def run(self):
        while True:
            time.sleep(3)
            numero = random.randint(0,10)
            self.sede.incDecSizeUltimi(numero)



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
            

sede = Sede(6)

display = Display(sede)
display.start()


#utenti = [Utente(sede) for p in range(10)]
utenti_safe = [UtenteSafe(sede) for p in range(100)]
#utenti_furbetti = [UtenteFurbetto(sede) for p in range (10)]

impiegato = [Impiegato(sede, i) for i in "ABCDEF"]


#for p in utenti:
#    p.start()

for p in utenti_safe:
    p.start()

#for p in utenti_furbetti:
#    p.start()

for i in impiegato:
    i.start()

changer = ChangeSize(sede)
changer.start()