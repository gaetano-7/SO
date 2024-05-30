#!/usr/bin/perl

$cont = 0;
$attuale = "";
$contmax = 0;
%valmax;
%valmin;
if ($#ARGV == -1){
    @elementi = qx{cat /home/gaetano/.bash_history | cut -d ' ' -f 1};
    $contmin = $#elementi;
    for $elemento (@elementi){
        $attuale = $elemento;
        $contatt = 0;
        for $check ($cont,@elementi){
            if($check eq $attuale){
                $contatt += 1;
            }
        }
        if ($contatt > $contmax){
            undef %valmax;
            $valmax{$attuale} = $contatt;
            $contmax = $contatt;
        }
        elsif ($contatt == $contmax){
            $valmax{$attuale} = $contatt;
        }
        elsif ($contatt < $contmin){
            undef %valmin;
            $valmin{$attuale} = $contatt;
            $contmin = $contatt;
        }
        elsif ($contatt == $contmin){
            $valmin{$attuale} = $contatt;
        }
        $cont += 1;
    }
    print "\n Stampa MASSIMI\n";
    foreach $valore (sort { $b cmp $a } keys %valmax)
    {
    print "$valmax{$valore} $valore\n";
    }

    print "\n Stampa MINIMI\n";
    foreach $valore (sort { $b cmp $a } keys %valmin) 
    {
    print "$valmin{$valore} $valore\n";
    }
}
else{
    @elementi = qx{cat /home/gaetano/.bash_history};

    $valore = pop @ARGV;
    
    @ultimi_tre = @elementi[-3..-1];
    print "\n", @ultimi_tre;
}