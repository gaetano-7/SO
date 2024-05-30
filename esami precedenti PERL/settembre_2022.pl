#!/usr/bin/perl

@cartella = qx{ls /home/giuseppel/Book.tar.gz};

$input = "";
@mesi;
while($input ne 'END'){
    for $mese (@cartella){
        if ($mese =~ /(\w+)\_/){
            $month = $1;
            push @mesi, $month;
        }
    }
    $input = <STDIN>;
    chomp $input;
    $cnt = 0;
    if($input eq '-m'){
        $contatore_zeri = 0;
        for $elem (@cartella){
            $cont = 0;
            @file = qx{cat /home/giuseppel/Book.tar.gz/$elem};
            for $i (@file){
                if($cont % 2 == 0){
                    @sottoi = split(" ",$i);
                    for $numero (@sottoi){
                        if ($numero eq '0'){
                            print "$numero\n";
                            $contatore_zeri += 1;
                        }
                    }
                }
                $cont += 1;
            }
        }
        print "Nei mesi analizzati, ci sono stati $contatore_zeri giorni con 0 camere disponibili\n";
    }
    else{
        for $elem (@mesi){
            $elemento = $cartella[$cnt];
            if($input =~ $elem){
                if (defined $elemento){
                    print qx{cat /home/giuseppel/Book.tar.gz/$elemento};
                }
            }
            $cnt += 1;
        }
        $cnt = 0;
    }
}