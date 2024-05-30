from threading import RLock, Condition, Thread, current_thread
from time import sleep
from random import randint, random

#
# Funzione di stampa sincronizzata
#
plock = RLock()
def prints(s):
    plock.acquire()
    print(s)
    plock.release()

#
# Restituisce il Current THREAD ID (TID) di sistema formattato
#
def getThreadId():
    return f"{current_thread().ident:,d}"

#
# Errore WrongValue provocato se setDato imposta un valore negativo
#
class WrongValue(Exception):
    pass

class NoLockAcquired(Exception):
    pass

class ReadWriteLockEvoluto:

    def __init__(self):
        self.dato = 0
        self.ceUnoScrittore = False
        self.numLettori = 0
        self.lockAusiliario = RLock()
        self.conditionAusiliaria = Condition(self.lockAusiliario)
        self.max_readers = 10
        self.enable = True
        self.current_thread_lock = {}

    def setReaders(self, max_readers : int):
        with self.lockAusiliario:
            # Potrebbero esserci lettori in attesa che potrebbero sfruttare i nuovi posti.
            # Notifico questi eventuali lettori.
            if max_readers > self.max_readers:
                self.conditionAusiliaria.notify_all()
            self.max_readers = max_readers

    def enableWriters(self, enable : bool):
        with self.lockAusiliario:
            self.enable = enable
            #
            # Qualche scrittore che ha trovato il lock bloccato potrebbe 
            # beneficiare dello sblocco. Notifica in accordo a questo.
            #
            if enable:
                self.conditionAusiliaria.notify_all()

    def acquireReadLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_lock:
                return
            while self.ceUnoScrittore or self.numLettori >= self.max_readers:
                self.conditionAusiliaria.wait()
            self.numLettori += 1
            self.current_thread_lock[thread_id] = "read"

    def releaseReadLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_lock:
                del self.current_thread_lock[thread_id]
            self.numLettori -= 1
            if self.numLettori < self.max_readers:
                self.lockaqcuire = False
                self.conditionAusiliaria.notify_all()

    def acquireWriteLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_lock:
                return
            while self.ceUnoScrittore or self.numLettori > 0 or not self.enable:
                self.conditionAusiliaria.wait()
            self.ceUnoScrittore = True
            self.current_thread_lock[thread_id] = "write"

    def releaseWriteLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_lock:
                del self.current_thread_lock[thread_id]
            self.conditionAusiliaria.notify_all()
            self.ceUnoScrittore = False

    def getDato(self):
        with self.lockAusiliario:
            if not self.ceUnoScrittore and self.numLettori > 0:
                return self.dato
            else:
                raise NoLockAcquired
    
    def setDato(self, i):
        with self.lockAusiliario:
            if self.ceUnoScrittore:
                #
                # Dato puÃ² essere solo positivo
                #
                if i < 0:
                    raise WrongValue
                else:
                    self.dato = i
                self.dato = i
            else:
                raise NoLockAcquired


class Scrittore(Thread):
    
    maxIterations = 1000

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Lo scrittore %s chiede di scrivere." % getThreadId())
            self.dc.acquireWriteLock()
            prints("Lo scrittore %s comincia a scrivere." % getThreadId() )
            sleep(random())
            v = random() * 10
            self.dc.setDato(v)
            prints(f"Lo scrittore {getThreadId()} ha scritto il valore {v:.2f}.")
            self.dc.releaseWriteLock()
            prints("Lo scrittore %s termina di scrivere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1


class Lettore(Thread):
    maxIterations = 100

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Il lettore %s Chiede di leggere." % getThreadId())
            self.dc.acquireReadLock()
            prints("Il lettore %s Comincia a leggere." % getThreadId())
            #sleep(random())
            prints("Il lettore %s legge." % self.dc.getDato())
            self.dc.releaseReadLock()
            prints("Il lettore %s termina di leggere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1

#
# Codici ANSI per avere le scritte colorate su stampa console
#
redANSIcode = '\033[31m'
blueANSIcode = '\033[34m'
resetANSIcode = '\033[0m'
 
class TestaMetodi(Thread):

    maxIterations = 500

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = self.maxIterations

    def run(self):
        enable = True
        while self.iterations > 0:
            sleep(random() * 2)
            self.dc.enableWriters(enable)
            prints(f"{redANSIcode}SCRITTORI ABILITATI: {enable:d}{resetANSIcode}")
            #
            # Inverte il valore di enable, cosÃ¬ al prossimo giro imposta False se a questo
            # giro Ã¨ stato impostato True. E viceversa
            #
            enable = not enable
            sleep(random() * 2)
            #
            # Imposta i readers a un valore random. 
            # Si noti che max_readers = 0 => nessun lettore
            # puÃ² accedere.
            #
            v = randint (0,10)
            self.dc.setReaders(v)
            prints(f"{blueANSIcode}LETTORI ABILITATI: {v}{resetANSIcode}")

            self.iterations -= 1 

class Copiatore(Thread):
    def __init__(self,dc,dc2):
        super().__init__()
        self.dc = dc
        self.dc2 = dc2

    def run(self):
        while True:
            rand = randint(1,2)
            if rand == 1:
                dc2.dato = dc.dato
            else:
                dc.dato = dc2.dato


if __name__ == '__main__':
        dc = ReadWriteLockEvoluto()
        dc2 = ReadWriteLockEvoluto()

        NUMS = 5
        NUML = 10
        scrittori = [Scrittore(dc) for i in range(NUMS)]
        lettori = [Lettore(dc) for i in range(NUML)]
        for s in scrittori:
            s.start()
        for l in lettori:
            l.start()
        sleep(3)
        copiatore = Copiatore(dc,dc2)
        copiatore.start()
        #
        # Lancia una istanza di TestaMetodi anonima 
        #
        TestaMetodi(dc).start()