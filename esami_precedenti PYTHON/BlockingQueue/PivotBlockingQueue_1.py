from threading import Thread,RLock,Condition, get_ident
from time import sleep
from random import random,randint

'''
Il codice fornito implementa una struttura dati detta PivotBlockingQueue, simile alla Blocking Queue. 
La differenza principale sta nel fatto che l'operazione take() opera su due elementi. 
Quando si fa un prelievo, un certo elemento da individuare, detto PIVOT, viene eliminato dalla coda, 
mentre un altro elemento viene individuato secondo l'usuale politica FIFO, quindi estratto dalla coda e restituito. 
Proprio come le code bloccanti standard, una PivotBlockingQueue può contenere al massimo N elementi, 
dove N è specificato in fase di creazione della struttura dati. Le regole per determinare l'elemento PIVOT
vengono scelte secondo un particolare criterio che è possibile impostare con un metodo apposito.
'''
class PivotBlockingQueue:
    def __init__(self,dim):
        self.dim = dim
        self.buffer = []
        self.criterio = True
        self.lock = RLock()
        self.condNewElement = Condition(self.lock)
        self.nPivot = 1
        self.somma = 0
        self.condWaitFor = Condition(self.lock)

    def take(self) -> int:
        with self.lock:
            while len(self.buffer) < self.nPivot + 1:
                self.condNewElement.wait()
            
            for i in range(self.nPivot):
                self.__removePivot__()
            return self.buffer.pop(0)
        
    def put(self,v : int):
        with self.lock:
            if len(self.buffer) == self.dim:
                self.__removePivot__()
            for i in range(self.nPivot): #ciclo fatto per far si che ci siano sempre elementi nella queue
                self.buffer.append(v)
                self.somma += v
                self.condWaitFor.notify_all()
            if len(self.buffer) == 2:
                self.condNewElement.notify()

    '''
    setCriterioPivot(minMax : boolean)
    Definisce il criterio di scelta dell'elemento PIVOT. Il criterio di scelta dell'elemento PIVOT
    serve a definire come la coda individua l'elemento PIVOT. Si può impostare la coda per prendere 
    il massimo oppure il minimo tra gli elementi attualmente presenti nella coda.
    Se minMax = True, al termine della chiamata il criterio di scelta dell'elemento PIVOT diventerà
    quello del minimo elemento tra quelli presenti nella coda. Se minMax = False, al termine della 
    chiamata il criterio di scelta dell'elemento PIVOT diventerà  quello del massimo elemento tra quelli presenti. 
    Se ci sono più di un valore massimo (o più di un valore minimo), viene selezionato l'elemento inserito più recentemente. 
    Inizialmente il criterio di scelta dell'elemento PIVOT viene impostato su quello del minimo elemento.
    '''

    def setCriterioPivot(self,minMax : bool):
        with self.lock:
            self.criterio = minMax #True = minore, #False = massimo
    
    '''
        Funzione usata per definire il criterio di scelta del pivot (max o min)
    '''
    def __migliore__(self,a :int, b: int) -> bool:
    
        return a < b if self.criterio else a > b
    
    '''
        Funzione privata che trova e rimuove il pivot secondo le regole stabilite.
        Si noti che non ci si aspetta che questa funzione venga chiamata direttamente essendo privata.
    '''
    def __removePivot__(self):
        pivot = self.buffer[0]
        pivotMultipli = False
        for i in range(1,len(self.buffer)):
            if self.__migliore__(self.buffer[i],pivot):
                pivot = self.buffer[i]
                pivotMultipli = False
            elif self.buffer[i] == pivot:
                pivotMultipli = True

        if not pivotMultipli:
            self.buffer.remove(pivot)
            self.somma -= pivot
        else:
            self.somma -= self.buffer.pop()

    def setPivotNumber(self, n:int):
        with self.lock:
            if n < 1 or n > self.dim:
                return
            self.nPivot = n
            print(f"NUMERO DI PIVOT IMPOSTATO SU {self.nPivot}\n")
        
    def doubleTake(self):
        with self.lock:
            while len(self.buffer) < self.nPivot + 2:
                self.condNewElement.wait()

            for i in range(self.nPivot):
                self.__removePivot__()
            
            valore1 = self.buffer.pop(0)
            valore2 = self.buffer.pop(0)

            print(f"I VALORI ESTRATTI SONO: {valore1} E {valore2}\n")

            return valore1, valore2
        
    def waitFor(self,n):
        with self.lock:
            while self.somma <= n:
                print(f"{self.somma} < {n}\n")
                self.condWaitFor.wait()
            print(f"{self.somma} > {n}\n")
            return

class Operator(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
            sleep(random())
            coda.put(randint(-100,100))
            coda.put(randint(-100,100))
            sleep(random())
            print (f"Il thread TID={get_ident()} ha estratto il valore {coda.take()}\n" )
            #coda.doubleTake()


class Switch(Thread):
    def __init__(self,c):
        super().__init__()
        self.coda = c

    def run(self):
        while True:
            sleep(2)
            casuale = randint(1,4)
            self.coda.setPivotNumber(casuale)

class WaitSomma(Thread):
    def __init__(self,c):
        super().__init__()
        self.coda = c

    def run(self):
        while True:
            sleep(2)
            casuale = randint(0,10000)
            self.coda.waitFor(casuale)

if __name__ == '__main__':
            
    coda = PivotBlockingQueue(10)        
    operatori = [Operator(coda) for i in range(50)] 
    for o in operatori:
        o.start()

    #s = Switch(coda)
    #s.start()

    w = WaitSomma(coda)
    w.start()
    
    