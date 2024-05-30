from threading import RLock, Thread, Condition
from random import randint
from time import sleep

'''

Il codice fornito implementa il gioco di â€œUn, due, tre, Stella!â€, nella versione resa famosa dalla serie The Squid Game. 
457 diversi Player devono riuscire a compiere un certo numero di passi N entro lo scadere di un certo tempo limite T (gameDuration nel codice). 
Un semaforo che si alterna a intervalli temporali casuali tra i valori RED e GREEN stabilisce i momenti in cui i Player possono muoversi. 
Se un Player si muove in un momento in cui il  semaforo Ã¨ RED, il Player in questione viene immediatamente eliminato. 
Un Player puÃ² invece compiere liberamente dei passi nei momenti in cui il semaforo Ã¨ GREEN. 
Quando un Player compie piÃ¹ degli N (winningLine nel codice) passi richiesti esso si puÃ² considerare salvo. 
Allo scadere del tempo T, tutti i Player che non hanno ancora compiuto i passi richiesti per salvarsi vengono eliminati e infine il gioco termina definitivamente.

'''

'''
Punto 1:
Si osservi che nel codice fornito, per via di problemi di context switch da individuare, l ordine delle stampe non sempre
corrisponde alla sequenza di gioco che ci si aspetterebbe. Ad esempio, può verificarsi che a video appaia la sequenza
RED LIGHT!!!!
GREEN LIGHT!!!!
KILLING PLAYER 016 AAHAHAHAHAHA!!!!
PLEASE PLEASE NO NO NO NO DON'T KILL MEEEE AAAAAAHHHH. [RIP PLAYER 016]!!!!
KILLING PLAYER 198 AAHAHAHAHAHA!!!!
Che lascia apparentemente pensare che è stato eliminato un Player quando la luce del semaforo è GREEN. Si corregga
opportunamente il codice per ottenere una sequenza delle stampe corretta. Si salvi la versione corretta al punto 1 col
nome SquidGame-Punto1.py.

Punto 2:
Partendo dal codice originale contenuto in SquidGame.py, si modifichi il codice in maniera tale da affidare le
eliminazioni dei Player a un Thread Killer. Solo il Thread killer può invocare il metodo
UnDueTreStella.kill(num). Quando un altra tipologia di Thread deve effettuare una o più eliminazioni, si deve
commissionare l eliminazione stessa usando il nuovo metodo UnDueTreStella.ordinaEliminazione(num).
Tale metodo commissiona una richiesta di eliminazione al Thread killer ed esce immediatamente. Il Thread killer attende
invece l arrivo di richieste di eliminazione. Queste ultime vengono smaltite in ordine di arrivo FIFO dal thread killer stesso, il
quale invoca il metodo UnDueTreStella.kill(num) in accordo alla corrispondente richiesta di eliminazione. Il
Thread killer ha la facoltà di eliminare i Player in qualsiasi momento del gioco (sia con luce RED che con luce GREEN che a
tempo scaduto).

Punto 3:
Si fornisca una variante del gioco in cui il timer si avvia, anziché subito, dal momento in cui il primo giocatore si salva. Dal
momento in cui si salva il primo giocatore, il gioco deve terminare se:
1. Si sono salvati 50 Player, oppure
2. E scaduto il tempo del timer
Al termine del gioco, tutti i restanti Player devono essere eliminati utilizzando il killer implementato al punto 2.
Deve essere possibile avviare il gioco a scelta in una delle due modalità, dunque la classe UnDueTreStella dovrà possedere
un costruttore nella forma:
def __init__(self,specialMode = False)
Allorquando specialMode = True, il gioco dovrà svolgersi nella modalità speciale di cui al Punto 3.
Si salvino le modifiche apportate al Punto 2 e al Punto 3 (anche se si è svolto solo un punto o parte di entrambi i punti),
nel file SquidGame-Punto2-Punto3.py
'''

GREEN = 0
RED = 1
NUMPLAYERS = 20

#
# Suggerimento per le prove a casa: ridurre il numero di giocatori e variare la durata del gioco e la winningLine.
#


#
# Funzione di stampa di debug
#
debugOn = True
def debug(text : str):
    if debugOn:
        print(text)

#
# Scheda di ciascun giocatore
#
class PlayerData:

    def __init__(self,p, n : str):
        self.player = p
        self.num = n
        self.position = 0
#
# Classe che tiene traccia dello stato del gioco
#
class UnDueTreStella:

    def __init__(self, specialMode = False):
        self.winningLine = 80
        self.gameDuration = 20
        self.playerData = {}
        self.currentMode = GREEN
        self.running = True
        self.lock = RLock()
        self.da_eliminare = []
        self.cond_eliminazione = Condition(self.lock)
        self.cond_50_salvi = Condition(self.lock)
        self.salvati = 0
        self.specialMode = specialMode

        for i in range(1,NUMPLAYERS+1):
            num = "%03d" % i   # num = f"{i:03}"
            pd = PlayerData(Player(self,num),num)
            self.playerData[num] = pd   
            pd.player.start()

        self.timer = Timer(self)
        if self.specialMode == False:
            self.timer.start()

        self.stellaMaster = StellaMaster(self)
        self.stellaMaster.start()

        self.killer = Killer(self)
        self.killer.start()
 
        Display(self).start()

 
    def shout(self,text : str):
        print(text.upper()+"!!!!")

    def step(self, num : str) -> int:
        sleep(randint(0,5)/10)
        with self.lock:
            if self.currentMode == GREEN:
                self.playerData[num].position += 1
                if self.playerData[num].position > self.winningLine:
                    #
                    # SAFE! Sono salvo e oltre la linea finale
                    #
                    self.shout("I'm aliveeeeeeeee. [Player %s survives beyond the line]" % num)
                    if self.specialMode:
                        self.salvati += 1
                        if self.salvati == 1:
                            self.timer.start()
                        if self.salvati == 50:
                            self.gameOver()
                    return 0 
                else:
                    #
                    # Sono riuscito a fare un passo in piÃ¹
                    #
                    return 1
            else: 
                # se si arriva in questo ramo, il semaforo Ã¨ RED. il Player viene UCCISO
                self.shout("Please please no no no no don't kill meeee aaaaaahhhh. [RIP Player %s]" % num)
                self.ordinaEliminazione(num)
                return -1


    def getLight(self) -> int:
        with self.lock:
            return self.currentMode

    def setLight(self, v : int):
        with self.lock:
            self.currentMode = v

    def stop(self):
        with self.lock:
            self.running = False

    def gameOver(self) -> bool:
        with self.lock:
            return not self.running or len(self.playerData) == 0

    def kill(self):
        with self.lock:
            if self.gameOver():
                return
            while (len(self.da_eliminare) == 0):
                self.cond_eliminazione.wait()
            if len(self.da_eliminare) == 0:
                return
            num = self.da_eliminare[0]
            del self.playerData[num]
            self.shout("killing player %s aahahahahaha" % num)   # self.shout(f"killing player {num} aahahahahaha")
            self.da_eliminare.pop(0)

    def killPeople(self):
        with self.lock:
            #
            # Non si possono cancellare elementi da un dizionario mentre vi si sta iterando sopra. 
            # dunque Ã¨ necessario prima ricopiare tutte le chiavi in una nuova lista separata.
            #
            for num in list(self.playerData.keys()):
                #
                #  Giocatore che si Ã¨ salvato.
                #
                if self.playerData[num].position > self.winningLine:
                    print("Sparing player %s" % num)     # print(f"Sparing player {num}")
                    #self.kill(num)
                    #self.cond_finale.notify_all()

            lunghezza = len(self.da_eliminare)
            for i in range(lunghezza):
                num = self.da_eliminare[0]
                del self.playerData[num]
                self.shout("killing player %s aahahahahaha" % num)   # self.shout(f"killing player {num} aahahahahaha")
                self.da_eliminare.pop(0)
            self.cond_eliminazione.notify_all()

                    

    def printPlayers(self):
        with self.lock:
            txt = ""
            for pd in self.playerData.values():
                txt += f"%s:%03d " % (pd.num,pd.position)   #  txt += f"{pd.num}:{pd.position:03} "
            print(txt)    

    def ordinaEliminazione(self, num):
        with self.lock:
            self.da_eliminare.append(num)
            self.cond_eliminazione.notify_all()
            '''
            print("LISTA ATTUALE: ", end = " ")
            for i in range(len(self.da_eliminare)):
                print(self.da_eliminare[i], end = " ")
            print("\n")
            '''
        return

class Timer(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        debug("Timer started\n")
        sleep(self.game.gameDuration)
        self.game.stop()
        self.game.shout("TIME IS OVER!")

class Player(Thread):

    def __init__(self,game : UnDueTreStella, numero : str):
        Thread.__init__(self)
        self.game = game
        self.numero = numero

    def run(self):
        debug("Player %s started" % self.numero)  #  debug(f"Player {self.numero} started")
        aliveAndKicking = 1
        while aliveAndKicking > 0:
            if self.game.getLight() == GREEN:
                aliveAndKicking = self.game.step(self.numero)    
            

class StellaMaster(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        debug("StellaMaster Started")
        while not self.game.gameOver():
            self.game.shout("green light")
            self.game.setLight(GREEN)
            sleep(randint(1,10)/5)
            self.game.shout("red light")
            self.game.setLight(RED)
        #print(f"The timer ended with {len(self.game.playerData)} survivors. Proceeding to kill survivors still before the winning line.")
        print("The timer ended with %d survivors. Proceeding to kill survivors still before the winning line." % len(self.game.playerData))
        self.game.killPeople()
        #print(f"The game ended with {len(self.game.playerData)} survivors. Proceeding to next game.")
        sleep(2)
        print(f"The game ended with %d survivors. Proceeding to next game." % len(self.game.playerData))

class Display(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        while(not self.game.gameOver()):
            sleep(1)
            self.game.printPlayers()

class Killer(Thread):
    def __init__(self, game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        while True:
            with self.game.lock:
                self.game.cond_eliminazione.wait()
            self.game.kill()
            if self.game.gameOver():
                return False

theSquidGame = UnDueTreStella(True)
print ("GAME STARTED. GOOD LUCK")