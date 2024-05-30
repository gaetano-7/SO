#!/usr/bin/perl

sub trim {
    my $string = shift;
    $string =~ s/^\s+|\s+$//g;
    return $string;
}

if($#ARGV == -1){
    print "NESSUN INGREDIENTE SELEZIONATO";
}
else{
    %elementi;
    %svolgimenti;
    $cnt = 1;
    $conta = 0;
    @ricette = qx{ls /home/giuseppel/ricette};
    foreach $arg (@ARGV){
        $attuale = $arg;
        for $rice (@ricette){
            chomp($rice);
            @ricetta = qx{cat /home/giuseppel/ricette/$rice};
            #print "\n", @ricetta;
            for $stringa (@ricetta){
                $stringa = trim($stringa);
                #print "ATTUALE: $stringa, Preparazione";
                if ($stringa eq 'Preparazione'){
                    last;
                }
                if($stringa =~ /$attuale/){
                    $nome_file = $rice;
                    $nome_file =~ s/\.txt$//;
                    $nome_file = uc($nome_file);
                    $elementi{$cnt} ="- $nome_file: $stringa";
                    $cnt += 1;
                }
            }
            $conta += 1;
        }
    }
    foreach my $valore (sort { $a <=> $b } keys %elementi) {
        print "$valore $elementi{$valore}\n";
    }
}

$valore = <STDIN>;
chomp $valore;
if($valore eq 'end' or $valore eq 'END') {}
else{
    if (exists $elementi{$valore}) {
        $frase = $elementi{$valore};
        if ($frase =~ /(\w+)\s*:/) {
            $parola = $1;
            $parola = lc($parola);
            #print "$parola\n";
            @testo = qx{cat /home/giuseppel/ricette/$parola.txt};
            #print "@testo";
            $bool = 0;
            for $word (@testo){
                $word = trim($word);
                if($bool == 1){
                    print"$word";
                }
                if ($word eq 'Preparazione'){
                    $bool = 1;
                }
            }
            print"\n";
        }
    }
}