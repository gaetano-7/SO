my $path_archivio = $ARGV[0];

qx{tar -xf $path_archivio};

$valore = <STDIN>;
chomp($valore);  # Rimuovi il carattere di nuova linea

while ($valore ne "END"){
    my $file_path = '/home/gaetano/SO/settembre2022/'.substr($valore, 3).'_22.txt';
    open(my $fh, '<', $file_path) or die "Impossibile aprire il file '$file_path': $!";
    
    my $contatore_riga = 0;
    my @totali_colonne;

    while (my $riga = <$fh>) {
        $contatore_riga++;

        # Stampa solo la terza colonna delle righe dispari
        if ($contatore_riga % 2 != 0 && $contatore_riga > 1) {
            chomp $riga;  # Rimuovi il carattere di nuova linea
            my @colonne = split /\s+/, $riga;  # Dividi la riga in colonne utilizzando gli spazi come delimitatori 

            # Inizializza l'array se è la prima riga
            if (!$totali_colonne[0]) {
                @totali_colonne = (0) x scalar(@colonne);
            }

            # Aggiungi il valore di ogni colonna al totale corrispondente
            for my $i (0 .. $#colonne) {
                $totali_colonne[$i] += $colonne[$i];
            }
        }
    }
    
    close($fh);

    print "Lunedì: $totali_colonne[0] \n";
    print "Martedì: $totali_colonne[1] \n";
    print "Mercoledì: $totali_colonne[2] \n";
    print "Giovedì: $totali_colonne[3] \n";
    print "Venerdì: $totali_colonne[4] \n";
    print "Sabato: $totali_colonne[5] \n";
    print "Domenica: $totali_colonne[6] \n";

    $valore = <STDIN>;
    chomp($valore);  # Rimuovi il carattere di nuova linea per la prossima iterazione
}

