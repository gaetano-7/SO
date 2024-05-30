#! /usr/bin/perl

if (@ARGV==0){ # non sono stati passati argomenti
    # fa terminare lo script emettendo un messaggio di errore
    die "E' necessario specificare almeno un ingrediente\n"
} 

@ricette = qx(ls RICETTE);

foreach my $ricetta (@ricette){
    # tutto quello che viene da input va chompato
    chomp $ricetta;

    # estrae il nome del file senza estensione
    # lo assegna a $1 e viene convertito in maiuscolo con uc
    $nome = uc $1 if $ricetta =~ "(.*)\.txt";

    # apro il file controllando che non vada in errore
    open(FH, "<RICETTE/$ricetta") || die "Impossibile aprire il file RICETTE/$ricetta\n";

    # leggo una riga per volta
    while (<FH>){
        # se la riga contiene la stringa Ingredienti
        if (/Ingredienti/){
            # imposto la variabile ingredienti a 1
            $ingredienti = 1;
            next;
        }
        # se la riga contiene la stringa Preparazione
        if (/Preparazione/){
            # ciudo il file
            close(FH);
        }
        # se la variabile ingredienti esiste siamo nella sezione giusta
        if ($ingredienti){
            # itero gli argomenti passati allo script -> ingredienti da cercare
            foreach $ingrediente (@ARGV){
                chomp $ingrediente;
                # controllo che la riga corrente contiene l'ingrediente passato allo script
                if (/$ingrediente/){
                    # aggiungo il nome della ricetta corrente all'array @match
                    push @match,$ricetta;
                    #uso la size dell'array (scalar @match) per sapere quante ricette ho già stampato
                    print scalar @match."- $nome: $_";
                    close(FH);
                }
            }
        }
    }
}

# se l'array è vuoto non sono state trovate corrispondenze
if (@match == 0){
    print "Spiacente, nessuna ricetta contiene questo ingrediente.\n";
}

# mi metto in attesa della scelta, sto in loop per gestire eventuali errori
while (<STDIN>){
    # se l'utente ha scelto 'END' il ciclo viene interroto
    if (/END/){
        last;
    }
    
    # se l'utente inserisce un numero non valido
    if ($_ <= 0 || $_ > @match){
        print "Ricetta non in elenco, scegliere un valore tra 1 e ".scalar @match."\n";
        next;
    }
    
    # l'utente ha inserito un numero valido
    # apro il file della ricetta scelta
    open(FH,"<RICETTE/$match[$_-1]");

    # leggo le righe del file aperto
    while(<FH>){
        # se la riga contiene Preparazione siamo nella sezione giusta
        if (/Preparazione/){
            # imposto la variabile a 1
            # indico che le prossime righe sono quelle da stampare
            $print = 1;
            next;
        }
        # se print esiste vuol dire che mi trovo nella riga
        # del contenuto della preparazione
        if ($print){
            # stampo la riga
            print $_;
        }
    }
    # chiudo il file
    close(FH);
    print "\n";
    # termino il ciclo
    last;
}