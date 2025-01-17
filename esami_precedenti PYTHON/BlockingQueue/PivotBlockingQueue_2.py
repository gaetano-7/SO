from threading import Thread,RLock,Condition, get_ident
from time import sleep
from random import random,randint
from typing import List

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
        self.nPivot = 1
        self.lock = RLock()
        self.condNewElement = Condition(self.lock)

    '''
    take(self) -> int: 

    individua l'elemento PIVOT e lo elimina dalla coda; quindi estrae e restituisce un elemento 
    secondo il consueto ordine FIFO. Il metodo si pone in attesa bloccante se non sono presenti nella coda almeno due elementi.
    '''

    def take(self) -> int:
        with self.lock:
            while len(self.buffer) < self.nPivot+1:
                print(self.nPivot)
                print(self.buffer)
                self.condNewElement.wait()
            
            for i in range(self.nPivot):
                self.__removePivot__()
            return self.buffer.pop(0)
        
    def doubleTake(self) -> int:
        with self.lock:
            while len(self.buffer) < 2+self.nPivot+1:
                self.condNewElement.wait()

            for i in range(self.nPivot):
                self.__removePivot__()
            
            item1 = self.buffer.pop(0)
            item2 = self.buffer.pop(0)
            return item1, item2

    '''
    put(self,T : int)
    inserisce l'elemento T nella Blocking Queue. Se la coda contiene già  N elementi, 
    individua ed elimina l'elemento PIVOT, quindi inserisce subito l'elemento T. 
    Questo metodo dunque non è mai bloccante, poichè quando non si trova posto per T, 
    questo viene creato eliminando l'elemento PIVOT.
    '''          

    def put(self,v : int):
        with self.lock:
            if len(self.buffer) == self.dim:
                self.__removePivot__()
            self.buffer.append(v)
            if len(self.buffer) == self.nPivot+1:
                self.condNewElement.notify()

    '''def putIntegers(self,L : List):
        with self.lock:
            while len(self.buffer) + len(L) > self.dim:
                self.__removePivot__()

            self.buffer.extend(L)
            if len(self.buffer) >= self.nPivot + 1:
                self.condNewElement.notify()'''

    def putIntegers(self,L : List):
        with self.lock:
            while len(self.buffer) + len(L) > self.dim + self.nPivot:
                self.condNewElement.wait()

            for _ in range(self.nPivot):
                self.__removePivot__()

            self.buffer.extend(L)
            if len(self.buffer) >= self.nPivot + 1:
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
            self.criterio = minMax
    
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

        self.buffer.remove(pivot) if not pivotMultipli else self.buffer.pop()

    def setPivotNumber(self, n : int):
        with self.lock:
            self.nPivot = n
    
    def waitFor(self, n):
        with self.lock:
            while len(self.buffer) < n:
                self.condNewElement.wait()
            self.condNewElement.notify_all()

'''
    Thread di test
'''       
class Operator(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        self.lista = []
        
    def run(self):
        for i in range(1000):
            rand = randint(1,10)
            if rand == 5:
                casuale = randint(1,3)
                print(f"CAMBIO NUMERO DI PIVOT IN {casuale}\n")
                self.coda.setPivotNumber(casuale)
            sleep(random())
            for i in range(coda.nPivot+1):
                coda.put(randint(-100,100))
            r = randint(1,5)
            if r < 1:
                for i in range(randint(1,4)):
                    self.lista.append(randint(-100,100))
                coda.putIntegers(self.lista)
            sleep(random())
            coda.waitFor(7)
            rand2 = randint(0,5)
            if rand2 <= 1:
                coda.put(randint(-100,100))
                print (f"Il thread TID={get_ident()} ha estratto i valori {self.coda.doubleTake()}\n" )
            else:
                print (f"Il thread TID={get_ident()} ha estratto il valore {self.coda.take()}\n" )


if __name__ == '__main__':
            
    coda = PivotBlockingQueue(10)        
    operatori = [Operator(coda) for i in range(50)] 
    for o in operatori:
        o.start()