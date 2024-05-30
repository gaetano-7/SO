#!/usr/bin/perl

if(scalar @ARGV == 2){
    $comando = $ARGV[1];
    @cartella = qx{man $comando};
    #print "\n", @cartella;
    $descrizione = "";
    $lettera = "";
    $cnt_brevi = 0;
    $stamp = 0;
    %descr;
    for $elem (@cartella){
        if($bool == 1){
            if ($elem =~ /^\s*$/){
                $bool = 0;
                $descr{$lettera} = "$descrizione";
                $descrizione = "";
                next;
            }
            else{
                $descrizione .= $elem;
            }
        }
        if($elem =~ /^\s*-([a-zA-Z])\)/){
            next;
        }
        if($elem =~ /^\s*-([a-zA-Z]),/){
            $cnt_brevi += 1;
            #print "$elem\n";
            $elem = "-$1:";
            $lettera = $elem;
            $bool = 1;
        }
        if($elem =~ /^\s*-(\w)\s+(.*)/){
            $cnt_brevi += 1;
            #print "$elem\n";
            $temp = "-$1:";
            $elem =~ s/^\s*-\w+\s+//;
            $descr{$temp} = "$elem";
        }
    }
    if($ARGV[0] eq '-n'){
        print "$cnt_brevi opzioni brevi\n";
    }
    if($ARGV[0] eq '-o'){
        foreach $elem (sort { $descr{$a} cmp $descr{$b} } keys %descr){
            print "$elem $descr{$elem}";
        }
    }

}
else{
    die "Numero di informazioni errato";
}