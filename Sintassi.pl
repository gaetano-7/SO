/*per avviarlo da terminale:*/
#1) chmod u+x nomefile.pl
#2) perl nomefile.pl

/*per specificare l'interprete*/
#!/usr/bin/perl 

/*ti aiutano, mostrano errori*/
#use strict; use warnings; 

/* VARIABILI */
/* '$' USATA PER INDICARE STRINGHE E VALORI NUMERICI */
$var; #variabile scalare "$" ovvero numeri,stringe e booleane
$intero = 2314; #intero
$str = 'ciao $var'; #stringa che non permette di utilizzare variabili, ovvero stampa tutto
$str = "ciao $var"; #stringa che permette di inserire variabili
%str = 'ciao'.$var; #il punto '.' e l'operatore di concatenazione (somma tra due stringhe)

#passaggio da stringa a intero
my $stringa = "123";
my $intero = int($stringa);

#passaggio da stringa a float
my $stringa = "40.0";
my $float = $stringa + 0;

#passaggio da intero a stringa
my $intero = 123;
my $stringa = "$intero";

#controllare che una parola o una frase è presente in una stringa;
my $frase = "ciao come stai ?";
if ($frase =~ /ciao/) {
    print "La parola 'ciao' è presente nella frase.\n";
} else {
    print "La parola 'ciao' non è presente nella frase.\n";
}

#codice che itera un ciclo fino alla lunghezza della stringa e seleziona ogni elemento della stringa
'''CORRISPETTIVO CODICE PYTHON:
frase = "lillanutella";
for i in range (len(frase)):
    print(frase[i])'''
    
$frase = "lillanutella";
for $i (0..length($frase)-1){
    $carattere = substr($frase, $i, 1);
    print "$carattere\n";
}


/* VARIABILI SPECIALI */
@ARGV # E' una variabile speciale in Perl che rappresenta gli argomenti passati allo script Perl dalla riga di comando

Ad esempio: "perl script.pl arg1 arg2 arg3"
In questo caso gli argomenti 'arg1', 'arg2' e 'arg3' vengono passati allo script Perl.
Gli argomenti vengono memorizzati nell'array' 'ARGV'

Ogni elemento dell array corrisponde a un singolo argomento.
L elemento 0 ($ARGV[0]) contiene il primo argomento, l elemento 1 ($ARGV[1]) contiene il secondo argomento e così via.
L indice $#ARGV rappresenta l indice dell ultimo elemento nell array @ARGV.

shift @ARGV: La funzione shift viene spesso utilizzata per estrarre il primo elemento dall array @ARGV.
La sintassi shift @ARGV rimuove il primo elemento dall array @ARGV e restituisce quel valore.
Puoi assegnare il valore restituito a una variabile, ad esempio $file = shift @ARGV, per utilizzarlo nel tuo script.

$#ARGV: È un modo di ottenere l indice dell ultimo elemento nell array @ARGV.
Ad esempio, se $#ARGV restituisce 2, significa che ci sono 3 argomenti passati allo script Perl.

scalar @ARGV: La funzione scalar viene utilizzata per ottenere la lunghezza dell array @ARGV,
cioè il numero di argomenti passati allo script Perl.

Iterazione su @ARGV: È possibile utilizzare un loop for o un loop foreach per iterare sugli elementi dell array @ARGV
e lavorare con ciascun argomento separatamente. Ad esempio:

perl

    foreach my $arg (@ARGV) {
        print "Argomento: $arg\n";
    }

In sintesi, ARGV è una variabile speciale in Perl che contiene gli argomenti passati allo script Perl dalla riga di comando.
Puoi accedere agli argomenti utilizzando l array @ARGV e lavorare con essi in base alle tue esigenze nello script.

if($#ARGV == -1){ #per vedere se sono stati passati argomenti alla chiamata del programma
    #non sono stati passati argomenti
}
else{
    #sono stati passati argomenti
}

#vedere il numero di argomenti passati ad ARGV
my $num_elementi = scalar @ARGV;
print "Numero di elementi passati: $num_elementi\n";




/* ARRAY */
/* '@' USATA PER INDICARE GLI ARRAY */
push @array, 1,2,3,4,5; # aggiungere elementi alla fine di un array
push @array, $variabile; # aggiungere variabile alla fine di unarray

my $elemento_array = $array[5]; # accedere a un elemento di array -> $
my $pezzo_array = @array[0,4]; # accedere a pezzi di array -> @

my $ultimo_elemento = pop @array; # elimina e restituisce ultimo elemento di un array

unshift @array, $variabile; # aggiungere elementi all'inizio di un array
unshift @array, @array2; # aggiunge tutti gli elementi di array2 all'inizio di array

my $primo_elemento = shift @array; # elimina e restituisce il primo elemento di un array

print join("\n",@array)."\n"; # stampa tutto array

my $str = join('.',@array); # stringa con gli elementi dell'array separati da '.'
my @arr = split('\.',$str); # @arr contiene gli elementi di $str separati da '.'
# $str = ci.bi.li -----  @arr = ('ci','bi','li')

my $lix ="lilla\n";
my $res = chomp $lix; #rimuove lo "\n" a fine stringa ---- $res = "lilla"

my $lunghezza_array = @arr; # restituisce la lunghezza dell'array

@array = ('ciccio') x 10; # @array conterrà 10 elementi il cui valore è 'ciccio'
$str = 'ciccio' x 10; # $str conterra 'cicciocicciocicciocicciocicciocicciocicciocicciocicciociccio'

for my $numero (1..10) {
    print "Numero: $numero\n";
    
    if ($numero == 7) {  # Esce dal ciclo quando il numero è 7
        last; # come break, esce immediatamente dal ciclo
        #next; # come continue, salta al prossimo valore di $numero, esclude il 7
    }
}

@array; #array "@"
@array = (1) x 10 #in questo modo si ottengono dieci 1 = '1 1 1 1 1 1 1 1 1 1'
@array1 = 1 x 10; #in questo modo invece crea un unico intero composto da dieci 1 = '1111111111'
#riempimento manuale array
@giorni_settimana = ("Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica");

print @array; #in questo modo stampa il tutto senza spazi

print join "\n", @array; #in questo modo stampa gli elementi separati, simile al classico ciclo for
print "$_\n" foreach @last; #come il precedente, altro modo per stampare a capo ogni elemento.

#METODO PER STAMPARE GLI ULTIMI ELEMENTI DI UNA LISTA
$valore = 4;
for $i (-$valore..-1){
    $val = @array[$i];
    print "$val\n";
} #stampa gli ultimi 4 valori della lista

$#array; #in questo modo prende l'indice dell'ultimo elemento
print $#array+1 #quindi cosi stampi la lunghezza dell'array
$lunghezza = scalar @array; #Ottenere la lunghezza dell'array

#ciclo for fino a len(lista)
my @lista = (1, 2, 3, 4);
for my $i (0 .. $#lista) {
    print $lista[$i] . "\n";
}

for($i = 0; %i <= $#array; $i++){
    print "$array[$i] ";
} #stampa for classica

push @array, 45; #'push' aggiunge 45 in coda all'array
unshift @array, 66 #'unshift' aggiunge 66 in testa all'array
undef @array; / @array = (); / splice @array; #svuota l'array
shift @array; #elimina il primo elemento dell'array
pop @array; #elimina l'ultimo elemento dell'array
splice @array, indice, n; #Rimuovere n elementi dall'array a partire dall'indice

$elemento = $array[indice]; #Accedere a un elemento in base all'indice
@array[indice] = "nuovo_valore"; #Modificare un elemento esistente

@nuovo_array = (@array1, @array2); #Unire due array

if (grep {$_ eq $elemento} @array) { #Verificare se un elemento è presente nell'array
    # L'elemento è presente nell'array
} else {
    # L'elemento non è presente nell'array
}

if (not grep {$_ eq $elemento} @array) { #Verificare se un elemento non  è presente nell'array
    # L'elemento non è presente nell'array
} else {
    # L'elemento è presente nell'array
}

@array2 = @array[1,2] #crea un nuovo array2 con gli elementi in indice 1,2 dell'array
@array2 = @array[1..10] #crea un nuovo array2 con gli elementi in indice 1 all'indice 10 dell'array
$array2 = @array[1..10] #se al posto di '@' cre uno scalare '$' in questo caso passa la size perchè deve passare un intero

#FUNZIONI DI ORDINAMENTO DI ARRAY TRAMITE SORT
@array = sort @array; #ordinare gli elementi dell'array

@array = reverse @array; #Invertire l'ordine degli elementi dell'array

sort {$a cmp $b} --> ordinamento lessografico

sort {$b cmp $a} --> ordinamento lessografico inverso

sort {$a <==> $b} --> ordinamento numerico ascendente

sort {$b <==> $a} --> ordinamento numerico discendente

#ESEMPIO:
@lista = sort {$b cmp $a} @lista;

@array1 = [1,65,7]

@copia {$a <==> $b} @array1; #in copia si avrà l'array1 ordinato ==> @copia = [1,7,65] 

for(sort({length $a <=> length $b || $a cmp $b} @comments)){ #ordinamento dalla stringa più lunga a quella più corta, se hanno uguale lunghezza stampa la prima in oridne alfabetico
    print $_."\n";
} 

#ORDINAMENTO PER ELEMENTI SECONDARI. es: IN QUESTO CASO LA LISTA 'ALIMENTI' VIENE
#ORDINATA PER PREZZO CRESCENTE (USO DELLE ESPRESSIONI REGOLARI)
my @elementi = (
    "pasta : 0.99",
    "pesto : 3.49",
    "tonno : 3.49"
);

my @ordinata = sort {
    my ($prezzo_a) = $a =~ /:\s*([\d.]+)/;
    my ($prezzo_b) = $b =~ /:\s*([\d.]+)/;
    $prezzo_a <=> $prezzo_b;
} @elementi;

foreach my $elem (@ordinata) {
    print "$elem\n";
}


$_ @_ #variabili globali
@s = split('_',"c_i_a_o"); #in questo modo split mette uno spazio ogni volta che trova un '_'. Quindi crea un array con ['c' 'i', 'a' 'o']

/* PRENDERE VALORI DA INPUT */
$valore = <STDIN>;
chomp $controllo; #rimuove il carattere di nuova linea dalla fine di una stringa

/* METODI PER I CICLI */
next = passa alla iterazione successiva
last = termina completamente il ciclo

/* FAR TERMINARE BRUSCAMENTE UN PROGRAMMA */
die "Errore";

/* i valori numerici si confrontano con i classici operatori numerici */
my $ugu = $a == $b; # True se sono uguali, False altrimenti
my $div = $a != $b; # True se sono diversi, False altrimenti
my $mag = $a > $b; # True se $a è maggiore di $b, False altrimenti
my $min = $a < $b; # True se $a è minore di $b, False altrimenti
my $mag_ugu = $a >= $b; # True se $a è maggiore-uguale di $b, False altrimenti
my $min_ugu = $a <= $b; # True se $a è minore-uguale di $b, False altrimenti
my $confronto = $a <=> $b; # -1 se $a minore di $b, 0 se sono uguali, 1 se $a è maggiore di $b

#operatori di confronto per le stringhe
$ugu = $a eq $b; # True se sono uguali, False altrimenti
$div = $a ne $b; # True se sono diversi, False altrimenti
$mag = $a gt $b; # True se nell'ordinamento lessicografico $a viene dopo di $b
$min = $a lt $b; # True se nell'ordinamento lessicografico $a viene prima di $b
$mag_ugu = $a ge $b; # True se nell'ordinamento lessicografico $a viene dopo o uguale di $b
$min_ugu = $a le $b; # True se nell'ordinamento lessicografico $a viene prima o uguale di $b
$confronto = $a cmp $b; # -1 se $a viene prima di $b, 0 se sono uguali, 1 se $a viene dopo $b

$str1 =~ /ia/; #true se 'ia' si trova in 'ciao'

%hash; #hasmap

/* operatori booleani */
&&, || --> valutano il valore a destra solo se quello a sinistra è vero per && e falso per ||
and, or --> valutano SEMPRE sia il valore a sinistra che quello a destra
my $and = $cond1 && $cond2; # True se entrambe le condizioni sono vere, False altrimenti
my $or = $cond1 || $cond2; # True se aleno una delle condizioni sono vere, False altrimenti

/* RENDERE LE STRINGHE MINUSCOLE O MAIUSCOLE */
$stringa_maiuscola = uc($stringa); #maiuscola
$stringa_minuscola = lc($stringa); #minuscola

/* ESPRESSIONI REGOLARI */
#servono a: - controllare pattern all'interno di stringhe
#           - recuperare pezzi di stringhe
#           - sostiituire pezzi di stringhe

#si rappresentano racchiuse tra / ..... /

/* ESPRESSIONI REGOLARI: METACARATTERI */
\ --> 1- può essere utilizzato per "escapare" caratteri speciali all interno di un 
        espressione regolare. Ad esempio, se vuoi cercare il punto "." 
        letterale invece di farlo corrispondere a qualsiasi carattere, puoi utilizzare il
        carattere di escape come segue: "\."
      2- può essere utilizzato per rappresentare caratteri di controllo come il ritorno
        a capo (\n), la tabulazione (\t), il carattere di ritorno a capo (\r), ecc.
      3- Se hai bisogno di utilizzare caratteri speciali come le virgolette all interno 
        di una stringa, puoi utilizzare il carattere di escape per indicare che il 
        carattere successivo deve essere trattato come carattere letterale. 
        Ad esempio, se vuoi includere una virgoletta all interno di una stringa racchiusa
        tra virgolette, puoi utilizzare ' \" ' per rappresentare il carattere di 
        virgoletta senza terminare la stringa.

^ --> Identifica l'inizio di una riga; inoltre all'inizio di un gruppo nega il gruppo stesso
. --> Qualsiasi carattere ad eccezione di quelli che identificano una riga nuova
$ --> Identifica la fine di una riga
| --> indica una condizione OR
() --> indicano un gruppo di caratteri
[] --> indicano intervalli e classi di caratteri

/* ESPRESSIONI REGOLARI: METACARATTERI (CONT.)*/
\d --> Ricerca un numero
\D --> Opposto di \d, ricerca qualsiasi cosa che non sia un numero
\w --> Ricerca un carattere "parola" (w sta per word) ovvero lettere, numeri e "_" -> [a-z A-Z 0-9 _]
\s --> Ricerca uno spazio, comprese tabulazioni e caratteri di fine riga
\S --> Opposto di \s. Ricerca qualsiasi cosa che non sia uno spazio, una tabulazione o dei caratteri di fine riga
\N --> Ricerca un carattere che non sia newline
\b --> Quando "\b" viene utilizzato all inizio di un pattern, corrisponde a un punto di ancoraggio
       all inizio di una parola. Ad esempio, il pattern "/\btest/" corrisponde a "test" solo
       quando appare all inizio di una parola. Quindi, "test" corrisponderà a "test" ma non
       a "atest" o "testo".
       Allo stesso modo, quando "\b" viene utilizzato alla fine di un pattern, rappresenta
       un punto di ancoraggio alla fine di una parola. Ad esempio, il pattern "/test\b/"
       corrisponde a "test" solo quando appare alla fine di una parola. Quindi, "test"
       corrisponderà a "test" ma non a "testa" o "testo".

/* ESPRESSIONI REGOLARI: QUANTIFICATORI */
* --> indica 0 o più occorrenze
+ --> indica 1 o più occorrenze
? --> indica al massimo 1 occorrenza
{n} --> Ricerca esattamente n occorrenze
{n,} --> Ricerca minimo n occorrenze
{n,p} --> Ricerca minimo n e massimo p occorrenze*/

/*  ESPRESSIONI REGOLARI CHE POTREBBERO TORNARE UTILI */
$str = "ciao Ciccio";

if ($str =~ /ci/) { # verifica se la stringa contiene la parola 'ci'
    print "La stringa contiene la parola 'ci'.\n";
} else {
    print "La stringa non contiene la parola 'ci'.\n";
}

my $cont = 0;
while ($str =~ /ci/g) { # g verifica tutti i match
    $cont += 1;
} 
print "La stringa contiene la parola 'ci' ".$cont." volte\n";
$cont = 0;
while ($str =~ /ci/gi) { # l'aggiunta di i verifica tutti i match anche in case-insensitive
    $cont += 1;
} 
print "La stringa contiene la parola 'ci' ".$cont." volte\n";

$nome_file =~ s/\.txt$//; # rimuove l'estensione ".txt" dal nome di un file

$frase =~ s/\*\/$//; # rimuove "*/" se è alla fine da una stringa

$frase =~ s/^\/\* //; # rimuove "/*" se è all'inizio da una stringa

$frase =~ s/\///g; # rimuove "/" se è nel mezzo di una stringa

#rimuove tutte le parentesi tonde all'interno della stringa
my $stringa = "(ciao) (come) (stai)";
$stringa =~ s/[()]//g; # Rimuove tutte le parentesi tonde
print $stringa; # Stampa: ciao come stai


if ($frase =~ /(\w+)\s*:/) { #prende tutto quelle che c'è prima di ":" (parola\spazi:)
    $parola = $1;
}

my $frase = "Esempio: questa è una frase.";
my $prima_dp;

if ($frase =~ /^(.*?) /) {
    $prima_dp = $1;
    print "Tutto ciò che precede ':' $prima_dp\n";
} else {
    print "Nessuna corrispondenza trovata.\n";
}

if ($frase =~ /:(.*)/) {
    $dopo_dp = $1;
    print "Tutto ciò che segue ':' $dopo_dp\n";
} else {
    print "Nessuna corrispondenza trovata.\n";
}

#controlla che la stringa termini con ".h"
my $stringa = "esempio.h";
if ($stringa =~ /\.h$/) {
    print "La stringa termina con '.h'\n";
} else {
    print "La stringa non termina con '.h'\n";
}

#RIMUOVE TUTTO QUELLO CHE C'E' DOPO "|"
my $stringa = "nike|69.99";  # La tua stringa
if ($stringa =~ /^(.*?)\|/) {
    my $estratto = $1;
    print "$estratto\n";
} else {
    print "Nessuna corrispondenza trovata\n";
}

#RIMUOVE TUTTO QUELLO CHE C'E' PRIMA DI "|"
my $stringa = "nike|69.99";  # La tua stringa
if ($stringa =~ /\|(.+)/) {
    print "$stringa\n";  # Stampa la stringa modificata
} else {
    print "Nessuna corrispondenza trovata\n";
}

#controlla che la stringa inizi con "/*"
if ($stringa =~ /^\/\*/) {
    print "La stringa inizia con '/*'\n";
}

#controlla che la striga inizi con /* e termini con */
if ($elem =~ /^\/\*.*\*\/$/) {
    print ("inizia con /* e termina con */")
}
'''In questa espressione regolare:

    ^ indica l inizio della stringa.
    \/\* corrisponde a "/*" all inizio della stringa. Poiché "/" è un carattere speciale nelle espressioni regolari, deve essere scappato con un "".
    .* corrisponde a zero o più caratteri qualsiasi.
    \*\/ corrisponde a "*/" alla fine della stringa. Anche qui, "/" deve essere scappato con un "".'''



#controlla che la stringa inizi con degli spazi,seguiti da "-", seguiti da una lettera
#minuscola o maiuscola, seguiti da una virgola. Per es: "  -f,....."
if($elem =~ /^\s*-([a-zA-Z]),/){
    print "$elem\n";
}

#controlla che la stringa inizi xcon "-" e che la seconda lettera non sia "-". es: "-v" OKAY, "--v" NO.
if ($val =~ /^-(?!-)/){
    print "$val\n";
}

#elimina tutti gli spazi da una stringa (utile quando il chomp non funziona)
my $stringa = "Questo è un esempio di stringa con spazi";
$stringa =~ s/\s+//g; # Rimuove tutti gli spazi
print $stringa; # Stampa: "Questoèunesempiodistringaconspazi"


#controlla che la stringa sia completamente vuota
my $line = "   ";
if ($line =~ /^\s*$/) {
    print "La riga è completamente vuota\n";
}

#cambiare elementi in una stringa
trasformare la stringa "gpasta|0.99" in "gpasta:0.99"

my $frase = "gpasta|0.99";
$frase =~ s/\|/:/g;

#controllare che una stringa presa da un comando è proprio quella
frase =     PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND  
if ($elem =~ /PID\s+USER\s+PR\s+NI\s+VIRT\s+RES\s+SHR\s+S\s+%CPU\s+%MEM\s+TIME\+\s+COMMAND/) {
        print "$elem";
} #se fai copia e incolla della frase al posto delle esp.reg non la prende per colpa della formattazione


#FILE TEST OPERATORS
-e $path: Restituisce 1 se il percorso $path esiste, indipendentemente dal fatto che sia un file, una directory o altro. Restituisce 0 se il percorso non esiste.

-f $path: Restituisce 1 se il percorso $path corrisponde a un file regolare. Restituisce 0 altrimenti.

-d $path: Restituisce 1 se il percorso $path corrisponde a una directory. Restituisce 0 altrimenti.

-r $path: Restituisce 1 se il percorso $path è leggibile. Restituisce 0 altrimenti.

-w $path: Restituisce 1 se il percorso $path è scrivibile. Restituisce 0 altrimenti.

-x $path: Restituisce 1 se il percorso $path è eseguibile. Restituisce 0 altrimenti.

-s $path: Restituisce la dimensione del file corrispondente al percorso $path, in byte. Restituisce 0 se il file è vuoto o non esiste.

esempio:
my $path = "/path/to/your/file_or_directory";

# Verifica se il percorso esiste
if (-e $path) {
    print "$path esiste.\n";
} else {
    print "$path non esiste.\n";
}

Se non si ha il path invece può tornare utile:
my @cartella = qx{ls -l /usr};

for my $elem (@cartella){
    if($elem =~ /^d/){
        print "$elem";
    }
}


#FUNZIONE STAT
/* La funzione stat restituisce un array contenente diverse informazioni sul file specificato.
Di seguito sono elencati gli indici dell'array @stat e i relativi valori restituiti dalla funzione stat:*/

0 Device ID del file
1 Numero dei nodi del file (numero inode)
2 Modalità di protezione del file (permessi)
3 Numero di collegamenti al file
4 ID del proprietario del file
5 ID del gruppo del file
6 Device ID del dispositivo speciale (se applicabile)
7 Dimensione del file in byte
8 Numero di blocchi allocati al file
9 Timestamp dell ultima modifica del file
10 Timestamp dell ultima accesso al file
11 Timestamp dell ultima modifica dei metadati del file

#esempio:
$path = "$directory/$controllo";
@stat = stat($path);
if(-f $path){
    $last_modified_timestamp = $stat[9];  # Indice 9 corrisponde all'ultima data di modifica
    $last_modified_date = strftime("%Y-%m-%d", localtime($last_modified_timestamp)); #si usa la funzione strftime (use POSIX qw(strftime);) per ottenere una stampa più leggibile
    print "Ultima modifica: $last_modified_date\n";
}

#ARRAY ASSOCIATVI
%nomi_completi = () #per gli array associativi si usa '%' e le '()'

%nomicompleti = (                                  # nomicompleti={"Camus":"Albert", "Smith":"Renee"...}
  "Camus"      => "Albert",
  "Einstein"   => "Albert",
  "Smith"      => "Renee",
  "Baudelaire" => "Charles",
  "Pierre"     => "Robes",
  "Smith"      => "Larry",        
  "Sartre"     => "Jean-Paul"
);

undef %array_associativo; #per svuotarlo

$array_associativo{chiave3} = "valore3"; # Aggiungi una nuova coppia di elementi

my $valore = $nome_array{chiave}; #Accedere a un valore in base alla chiave

#Verificare se una chiave esiste nell'array associativo
my $valore = 2;
if (exists $elementi{$valore}) {
    print "La chiave con valore $valore esiste in \%elementi\n";
} else {
    print "La chiave con valore $valore non esiste in \%elementi\n";
}

$hash{chiave} = "nuovo_valore"; #Modificare un valore esistente

delete $hash{chiave}; #Rimuovere un elemento dall'array associativo

while (my ($chiave, $valore) = each %hash) { #Iterare su tutte le chiavi e i valori
    # Fa qualcosa con $chiave e $valore
}

#Ottenere tutte le chiavi o tutti i valori
my @chiavi = keys %hash;     # Restituisce un array di tutte le chiavi
my @valori = values %hash;   # Restituisce un array di tutti i valori

my $numero_elementi = scalar keys %hash; #Contare il numero di elementi nell'array associativo

/* PER L'ORDINE NUMERICO USARE VALORI NUMERICI (<=>), PER LE STRINGHE GLI ALTRI (cmp) */
print "\n*** Ordine crescente numerico";
foreach my $valore (sort { $a <=> $b } keys %elementi) {
    print "$elementi{$valore} $valore\n";
}

print "\n*** Stampa ***\n";
foreach $cognome  (keys %nomicompleti)             # for cognome in nomicompleti.keys():
{                                                  #     print(f"{nomicompleti[cognome]}  {cognome}")
print "$nomicompleti{$cognome} $cognome\n";
}

print "\n*** Stampa ordinata per chiave (cognome) ***\n"; #a differenza di python che si indicizza con [] qui si indicizza con ()
foreach $cognome  (sort keys %nomicompleti)             # for cognome in sorted(nomicompleti.keys()):
{                                                       #     print(f"{nomicompleti[cognome]}  {cognome}")
print "$nomicompleti{$cognome} $cognome\n";
}

print "\n*** Stampa ordinata per chiave (cognome) ascendente ***\n";
foreach $cognome (sort { $a cmp $b } keys %nomicompleti)             # for cognome in sorted(nomicompleti.keys()):
{                                                                    #     print(f"{nomicompleti[cognome]}  {cognome}")
print "$nomicompleti{$cognome} $cognome\n";
}

print "\n*** Stampa ordinata per chiave (cognome) discendente ***\n";
foreach $cognome (sort { $b cmp $a } keys %nomicompleti)             # for  cognome in sorted(nomicompleti.keys(),reverse=True):
{                                                                    #      print(f"{nomicompleti[cognome]}  {cognome}")
print "$nomicompleti{$cognome} $cognome\n";
}

print "\n*** Stampa ordinata in base al valore (nome) in corrispondenza della chiave ***\n";
foreach $cognome (sort { $nomicompleti{$a} cmp $nomicompleti{$b} } keys %nomicompleti)
{
print "$nomicompleti{$cognome} $cognome\n";
}

print "\n*** Stampa ordinata in base al valore (nome) e a parità di valore in base alla chiave (cognome) ***\n";
foreach $cognome (sort { $nomicompleti{$a} cmp $nomicompleti{$b} || $a cmp $b} keys %nomicompleti)
{
print "$nomicompleti{$cognome} $cognome\n";
}

/* INSERIRE ELEMENTI DI UNA DIRECTORY IN UN ARRAY */
$directory = '/home/giuseppel/Scrivania/Sistemi operativi';
opendir($dir_handle, $directory) or die "Impossibile aprire la directory: $!";
@elementi = readdir($dir_handle);
closedir($dir_handle);

/* CODICI GENERALI CHE POSSONO TORNARE UTILI */

#CONTROLLARE SI IN UNA DIRECTORY SI STA ANALIZZANDO UN FILE O UNA CARTELLA
for $elemento (@elementi) { #ciclo
    if ($elemento eq '.' || $elemento eq '..'){ #ignora gli elementi selezionati
        next;
    };
    $path = "$directory/$elemento"; #creazione path per il controllo
    if (-d $path) { #controlla se path è una directory
        $contatore += 1;
        print "Cartella: $elemento\n";
    }
    if(-f $path > $maggioreint){ #controlla se path è un file
        $maggioreint = -s $path;
        $maggiorestr = $elemento;
    }
}

    for my $el (@elementi) { #ciclo
        $path = "../$el"; #creazione path per il controllo
        if (-d $path) { #controlla se path è una directory
            $cont_dir += 1;
            print "Cartella: $el\n";
        }
        if(-f $path){ #controlla se path è un file
            print "File: $el\n";
        }
    }

#CONTROLLA SE UNA PAROLA SI TROVA IN UNA STRINGA
$attuale = "nutella";
my $stringa = "Questa è la stringa con il valore nutella";
my $valore_da_cercare = "$attuale";

if ($stringa =~ /$valore_da_cercare/) { #se lo inseriamo direttamente le / / non servono. if ($stringa =~ nutella)
    print "La stringa contiene il valore $attuale\n";
} else {
    print "La stringa non contiene il valore $attuale\n";
}

#FUNZIONE CHE RIMUOVE GLI SPAZI EXTRA. UTILE NEL CONFRONTO TRA STRIGHE PER EVITARE
#PROBLEMI DI FORMATTAZIONE
sub trim { #funzione esterna
    my $string = shift;
    $string =~ s/^\s+|\s+$//g;
    return $string;
}
.
.
$stringa = trim($stringa);

#FUNZIONE SPLIT CHE TI EIMINA GLI SPAZI DA UNA STRINGA. UTILISSIMA QUANDO SI HANNO TANTI
#DATI DIVERSI MAGARI E SE NE VUOLE SELEZIONARE SOLO UNO.
#sintassi : split(/pattern/, $stringa);
my $stringa = "Questo è un esempio di stringa";
my @sottostringhe = split(" ", $stringa);

foreach my $sottostringa (@sottostringhe) {
    print "$sottostringa\n";
}

L output di codice fornito sarà:
Questo
è
un
esempio
di
stringa

#CONTROLLARE CHE UN ELEMENTO NON SIA NULLO (IL "NOT NULL" DICIAMO):
my $variabile;

if (defined $variabile) {
    print "La variabile non è nulla.";
} else {
    print "La variabile è nulla.";
}

#INSERIRE ELEMENTI ALL'INTERNO DI UN FILE
my $cartella = 'percorso/della/cartella';  # Specifica il percorso della cartella

open(my $filehandle, '>', "$cartella/nome_file.txt") or die "Impossibile aprire il file: $!"; # Apri il file all'interno della cartella
print $filehandle "Contenuto da inserire nel file\n"; # Scrivi i dati nel file
close($filehandle); # Chiudi il filehandle

#INSERIRE ELEMENTI DI UNA LISTA ALL'INTERNO DI UN FILE
open(my $file_handle, '>', '/home/giuseppel/last_calls') or die "Impossibile aprire il file 'last calls'";
for my $val (@cartella) {
    print $file_handle "$val\n";
}
close($file_handle);

#INSERIRE FILE IN UNA CARTELLA SE LA CARTELLA ESISTE
use File::Copy;

my $file_da_copiare = 'percorso/del/file_origine';  # Specifica il percorso del file originale
my $cartella_destinazione = 'percorso/della/cartella_destinazione';  # Specifica il percorso della cartella di destinazione

copy($file_da_copiare, "$cartella_destinazione/nome_file_destinazione") or die "Impossibile copiare il file: $!"; # Copia il file nella cartella di destinazione

#INSERIRE FILE IN UNA CARTELLA SE LA CARTELLA NON ESISTE
usare: qx{mkdir $path_alla_cartella/'nome_cartella_nuova'};
use File::copy ecc.....

#CONCATENARE NEL qx{} NOMI DI VARIABILI A CARATTERI AGGIUNTIVI
$input = "luglio";
@lista = "/home/giuseppel/$input\_22.txt";
in questo modo aprire il path "/home/giuseppel/luglio_22.txt";

#COMANDI TERMINALE
'''
linea di comando shell che restituisca l identificativo del processo che ha 
utilizzato per più tempo la CPU, la linea di comando dovrà essere scritta su 
un file chiamato Soluzione_Esercizio_2
'''

my $pid_maxCpu = qx{ps -eo pid --sort=-%cpu | awk 'NR==2 {print $1}' > Soluzione_Esercizio_2};

'''
cat "nomefile" ---> //Per visulizzare il file su terminale 2

mkdir a ---> //crea una cartella di nome "a"

mkdir a/b ---> //crea una sottocartella "b" dentro la cartella "a"

mkdir -p a/b/e/ciao/sottoalbero ---> //con il "-p" in caso non ci siano le cartelle che hai indicato, te le crea

touch file.txt ---> //Il comando "touch" viene utilizzato per creare un file vuoto o per aggiornare la data di accesso e/o di modifica di un file esistente. In questo caso crea un nuovo file vuoto se esso non esiste. Se già esistente aggiorna la data di accesso e di modifica.

man touch ---> //Il comando "man touch" viene utilizzato per visualizzare il manuale del comando "touch". Il manuale fornisce informazioni dettagliate sulle opzioni e sull'utilizzo del comando.

ls -l a ---> //mostra tutto ciò che all'interno della cartella "a"

mv a/file1.txt a/file1.tmt --->// il comando mv permette di modificare il nome oppure di spostare un file per esempoio da una cartella ad un altra. In questo caso cambia il nome del file

mv a/file1.txt b/file1.txt --->//In questo caso invece sposta file1.txt dalla cartella "a" alla cartella "b"

mv b/e/file1.txt rinominato.txt --->//In questo modo rinomino il file però viene spostato nella cartella corrente
mv b/e/file1.txt b/e/rinominato.txt --->//In questo modo invece lo rinomino senza spostarlo

mv file1.txt file2.txt file3.txt b/ --->//In questo modo sposta questi file nella cartella "b"
mv *.txt b/ --->//In questo modo invece sposta in "b" tutti i file .txt senza doverli scriverli uno ad uno

mv -v b/e/d* f/ --->//Prende tutti i file che iniziano con la lettera d che si trovano in "e" e li sposta in "f"

pico ./creacartella.sh -->//questo comando apre il file di script nell'editor di testo "pico". L'estensione .sh indica che si tratta di uno script shell, ovvero un file di testo contenente una serie di comandi che possono essere eseguiti in sequenza dal sistema operativo Linux. L'editor di testo "pico" è un editor di testo semplice e facile da usare che consente di modificare il contenuto del file di script. Una volta aperto il file di script, è possibile modificare il codice, salvare le modifiche e chiudere l'editor.

chmod u+x creacartelle.sh ---> //Da il permesso di modifica all'utente proprietario del file. In altre parole rende eseguibile lo script "creacartelle.sh" solo per l'utente proprietario del file, mentre gli altri utenti non avranno il permesso di eseguire lo script.

chmod ugo+rw a --->//Permette di cambiare i diritti di "a" in modo che tutti vi possono leggere e scrivere all'interno

ls -R --->//Permette di vedere tutto l'albero della cartella con le sottocartelle

rm cartella --->//permette di eliminare la cartella solo se vuota
rm -r -f cartella/ --->//permette di cancellare le cartelle sia che siano vuote o meno

cd a --->//ti sposta in "a"

cp file1.txt copiafile1.txt --->//permette di copiare l'argomento di file1.txt in copiafile1.txt
cp file1.txt b/copiafile1.txt --->//se copiafile1.txt si trova nella cartella "b"
cp file1.txt /home/ianni/SANDBOX/a/b/e --->//in questo modo la copia viene salvata nella cartella "e" tramite percorso assoluto. ATTENZIONE perchè se "e" invece di essere una cartella è un file lo sovrascrive.

cp -v ?doc* c/ --->//In questo modo prende tutti i file che a partire dal secondo carattere hanno all'interno il nome "doc" e li copia nella cartella "c"

curl --->//Permette di vedere un url

wget URLdelfile --->//Il metodo wget consente di scaricare file da Internet. Utile per scaricare file di grandi dimensioni, come immagini o video.

ps --->//Permette di vedere i processi attivi sulla macchina
'''
