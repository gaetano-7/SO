from threading import Thread,RLock,Condition, get_ident
from time import sleep
from random import random,randint

'''
Punto 1
Si deve modificare la classe PivotBlockingQueue in maniera tale da poter specificare quanti pivot ci sono in ciascun
momento. Per realizzare questo scopo, introduci il metodo setPivotNumber(self, n : int), che imposta il
numero di pivot al valore n (n deve essere almeno 1 e al massimo N-1, dove N è la dimensione della coda).
Il numero di pivot impostato in un certo momento influenza il numero di rimozioni di elementi prescritte. Dovrai fare in
modo che il cambio della quantità di pivot influenzi i metodi take() e put() per come spiegato di seguito. Facciamo un
esempio e supponiamo che il numero di pivot venga impostato a due, anziché uno come nel codice preesistente.
Se i pivot presenti vengono impostati a due, e non più a uno come nel codice esistente, dovrai fare in modo che take()
elimini due pivot prima di restituire l elemento richiesto, e cioè il primo massimo/minimo e il secondo massimo/minimo.
take() dovrà invece bloccarsi fintantochè in coda non ci siano almeno tre elementi (i due pivot da rimuovere più
l elemento da estrarre). L operazione di put resta invece invariata e rimuove un solo pivot nel caso in cui la coda sia piena.
E a tuo carico stabilire come gestire opportunamente il caso in cui ci sono due o più pivot di valore uguale e cioè due o più
massimi/minimi di pari valore.

Punto 2
Si estenda la classe PivotBlockingQueue con il metodo doubleTake(). Tale metodo preleva e restituisce una
coppia di elementi anziché uno solo, e si blocca se in coda non sono presenti almeno due elementi + i pivot. Decidi tu
quale sia la codifica migliore per restituire una coppia di interi anziché un solo valore intero. Nota che per risolvere questo
punto è necessario aver implementato il punto 1.

Punto 3
Introduci un metodo waitFor(self, n) che va in attesa bloccante finché la somma degli elementi presenti nella coda
non supera il valore n specificato, uscendo se la condizione è invece verificata.
'''

class PivotBlockingQueue:
    def __init__(self,dim):
        self.dim = dim
        self.buffer = []
        self.criterio = True
        self.lock = RLock()
        self.condNewElement = Condition(self.lock)
        self.N_Pivot = 1
        self.somma = sum(self.buffer)
        self.cond_somma = Condition(self.lock)

    def take(self) -> int:
        with self.lock:
            while len(self.buffer) < self.N_Pivot + 1:
                self.condNewElement.wait()

            for i in range(self.N_Pivot):   
                self.__removePivot__()
                print(f"ELEMENTO DI PIVOT {i} ELIMINATO\n")
            return self.buffer.pop(0)
        
    def doubleTake(self):
        with self.lock:
            while len(self.buffer) < self.N_Pivot + 2:
                self.condNewElement.wait()

            for i in range(self.N_Pivot):   
                self.__removePivot__()
                print(f"ELEMENTO DI PIVOT {i} ELIMINATO\n")

            elem1 = self.buffer.pop(0)
            elem2 = self.buffer.pop(0)

            return elem1, elem2
            

    def put(self,v : int):
        with self.lock:
            if len(self.buffer) == self.dim:
                self.__removePivot__()
            self.buffer.append(v)
            if len(self.buffer) == 2:
                self.condNewElement.notify()
                self.cond_somma.notify_all()

    def setCriterioPivot(self,minMax : bool):
        with self.lock:
            self.criterio = minMax

    def __migliore__(self,a :int, b: int) -> bool:
    
        return a < b if self.criterio else a > b

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
            self.N_Pivot = n
            print(f"NUMERO DI PIVOT CAMBIATO IN {n}\n")

    def waitFor(self, n):
        with self.lock:
            #self.somma = sum(self.buffer)
            while sum(self.buffer) < n:
                print(f"LA SOMMA TOTALE E' {sum(self.buffer)} ED E' MINORE DI {n}\n")
                self.cond_somma.wait()
            print(f"LA SOMMA TOTALE E' {sum(self.buffer)} E' MAGGIORE DI {n}\n")

  
class Operator(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
             sleep(random())
             for i in range(self.coda.N_Pivot + 1):
                coda.put(randint(-100,100))
                coda.put(randint(-100,100))
             sleep(random())
             elem1, elem2 = coda.doubleTake()
             #print (f"Il thread TID={get_ident()} ha estratto il valore {coda.take()}" )
             print (f"Il thread TID={get_ident()} ha estratto il valore {elem1} ed il valore {elem2}" )

class Switcher(Thread):
    def __init__(self, coda):
        super().__init__()
        self.coda = coda

    def run(self):
        while True:
            sleep(3)
            numero = randint(1,self.coda.dim-1)
            self.coda.setPivotNumber(numero)

class Attesa(Thread):
    def __init__(self, coda):
        super().__init__()
        self.coda = coda
    
    def run(self):
        while True:
            sleep(2)
            numero = randint(-100,100)
            self.coda.waitFor(numero)

if __name__ == '__main__':
            
    coda = PivotBlockingQueue(10)        
    operatori = [Operator(coda) for i in range(50)] 
    for o in operatori:
        o.start()
    switch = Switcher(coda)
    switch.start()

    attesa = Attesa(coda)
    attesa.start()
    