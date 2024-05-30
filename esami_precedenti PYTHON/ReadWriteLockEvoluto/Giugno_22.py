from threading import RLock, Condition, Thread, current_thread
from time import sleep
from random import randint, random

'''
Punto 1
Si modifichi il codice di prova introducendo un secondo valore condiviso, chiamato dc2, di tipo
ReadWriteLockEvoluto. Si lancino più istanze di thread di tipo Copiatore. Un thread Copiatore
periodicamente sceglie a caso un valore tra dc e dc2 e lo copia sull altro elemento non sorteggiato. Ad esempio, se viene
scelto dc, allora bisogna effettuare l operazione dc2.dato=dc.dato. Altrimenti bisognerà fare l operazione dc.dato
= dc2.dato.

Punto 2
Modificare getDato e setDato in maniera tale da provocare l eccezione NoLockAcquired allorquando questi
metodi vengono invocati senza che si possieda il lock corretto. Si noti che il possesso del write lock deve consentire di
invocare sia getDato che setDato, mentre il possesso del read lock deve consentire di invocare solamente getDato.

Punto 3
Si noti che se lo stesso thread T invoca per due volte consecutive acquireWriteLock, T si blocca in attesa di sè stesso. Lo
stesso problema si verifica se uno stesso thread invoca tante volte acquireReadLock, fino a saturare il numero di lettori
disponibili, oppure quando uno scrittore, già in possesso del lock in scrittura, prova ad acquisire il lock in lettura.
Si modifichi il readwritelockevoluto in maniera tale da ignorare eventuali invocazioni consecutive di
acquireReadLock o acquireWriteLock, così rendendo il readwritelockevoluto rientrante.
Esempio:
1.dc.acquireWriteLock()
2.dc.acquireWriteLock()
3.prints(“Che voglia di stampare che ho”)
Con il sorgente fornito, un thread si bloccherebbe per sempre sul rigo 2. Questo non deve succedere, la seconda chiamata
ad acquireWriteLock deve terminare immediatamente senza attese, poiché il thread corrente già possiede lo stesso lock,
che è stato acquisito sul rigo 1
'''

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
        self.current_thread_read_lock = {}
        self.current_thread_write_lock = {}

    def setReaders(self, max_readers : int):
        with self.lockAusiliario:
            #
            # Potrebbero esserci lettori in attesa che potrebbero sfruttare i nuovi posti.
            # Notifico questi eventuali lettori.
            #
            if max_readers > self.max_readers:
                self.conditionAusiliaria.notifyAll()
            self.max_readers = max_readers

    def enableWriters(self, enable : bool):
        with self.lockAusiliario:
            self.enable = enable
            #
            # Qualche scrittore che ha trovato il lock bloccato potrebbe 
            # beneficiare dello sblocco. Notifica in accordo a questo.
            #
            if enable:
                self.conditionAusiliaria.notifyAll()

    def acquireReadLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_read_lock:
                return
            while self.ceUnoScrittore or self.numLettori >= self.max_readers:
                self.conditionAusiliaria.wait()
            self.numLettori += 1
            self.current_thread_read_lock[thread_id] = "read"

    def releaseReadLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_read_lock:
                del self.current_thread_read_lock[thread_id]
            self.numLettori -= 1
            if self.numLettori < self.max_readers:
                self.conditionAusiliaria.notifyAll()

    def acquireWriteLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_write_lock:
                return
            while self.ceUnoScrittore or self.numLettori > 0 or not self.enable:
                self.conditionAusiliaria.wait()
            self.ceUnoScrittore = True
            self.current_thread_write_lock[thread_id] = "write"

    def releaseWriteLock(self):
        with self.lockAusiliario:
            thread_id = getThreadId()
            if thread_id in self.current_thread_write_lock:
                del self.current_thread_write_lock[thread_id]
            self.conditionAusiliaria.notifyAll()
            self.ceUnoScrittore = False

    def getDato(self):
        thread_id = getThreadId()
        if thread_id in self.current_thread_write_lock or thread_id in self.current_thread_read_lock:
            return self.dato
        else:
            raise NoLockAcquired
    
    def setDato(self, i):
        #
        # Dato puÃ² essere solo positivo
        #
        thread_id = getThreadId()
        if thread_id in self.current_thread_write_lock:
            if i < 0:
                raise WrongValue
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
            sleep(random())
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
    def __init__(self, dc, dc2):
        super().__init__()
        self.dc = dc
        self.dc2 = dc2

    def run(self):
        while True:
            sleep(randint(2,4))
            numero = randint(0,1)
            if numero == 0:
                vecchio = self.dc2.dato
                self.dc2.dato = self.dc.dato
                print(f"DC2 {vecchio} DIVENTA {self.dc.dato}\n")
            else:
                vecchio = self.dc.dato
                self.dc.dato = self.dc2.dato
                print(f"DC {vecchio} DIVENTA {self.dc2.dato}\n")



if __name__ == '__main__':
        dc = ReadWriteLockEvoluto()
        dc2 = ReadWriteLockEvoluto()

        NUMS = 5
        NUML = 10
        NUMC = 3
        scrittori = [Scrittore(dc) for i in range(NUMS)]
        lettori = [Lettore(dc) for i in range(NUML)]

        #scrittori2 = [Scrittore(dc2) for i in range(NUMS)]
        #lettori2 = [Lettore(dc2) for i in range(NUML)]

        copiatori = [Copiatore(dc, dc2) for i in range(NUMC)]
        for s in scrittori:
            s.start()
        for l in lettori:
            l.start()

        '''
        for s2 in scrittori2:
            s2.start()
        for l2 in lettori2:
            l2.start()
        '''

        for c in copiatori:
            c.start()
        #
        # Lancia una istanza di TestaMetodi anonima 
        #
        TestaMetodi(dc).start()