if (@ARGV) {
    my $file_path = "/usr/include/$ARGV[0]";
    open(my $fh, '<', $file_path) or die "Impossibile aprire il file '$file_path': $!";
    my $file_content = join('', <$fh>);  # Combina le linee del file in una singola stringa
    close($fh);

    # Estrae e memorizza tutti i commenti dal file
    my @commenti;
    while ($file_content =~ m{(/\*.*?\*/)}gs) {
        my $commento = $1;
        $commento =~ s/^\s+//gm;  # Rimuove spazi bianchi iniziali da ogni riga del commento
        push @commenti, $commento;
    }

    # Ordina i commenti per lunghezza e ordine lessicografico
    my @commenti_ordinati = sort { length($a) <=> length($b) || $a cmp $b } @commenti;

    # Stampa i commenti ordinati
    print "$_\n" for @commenti_ordinati;
}
else {
    my $directory = '/usr/include';
    opendir(my $dir_handle, $directory) or die "Impossibile aprire la directory: $!";
    my @elementi = readdir($dir_handle);
    closedir($dir_handle);

    foreach my $arg (@elementi) {
        if ($arg =~ /\.h$/){
            print "$arg\n";
        }
    }
}
