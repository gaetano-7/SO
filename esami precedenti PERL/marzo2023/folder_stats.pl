my $path = $ARGV[0];

my $contenuto_cart = qx{ls -l $path};

my @linee_contenuto = split /\n/, $contenuto_cart;

my $num_cart = 0;

foreach my $linea (@linee_contenuto) {
    my @campi = split /\s+/, $linea;

    if ($campi[0] eq "drwxr-xr-x"){
        $num_cart += 1;
    }
}

#1
print "$num_cart\n";

#2
foreach my $linea (@linee_contenuto) {
    my @campi = split /\s+/, $linea;

    if ($campi[0] eq "drwxr-xr-x"){
        print "$campi[8]\n";
    }
}

#3
my $dim_max = 0;
foreach my $linea (@linee_contenuto) {
    my @campi = split /\s+/, $linea;

    if ($campi[0] eq "-rw-r--r--" && $campi[4] > $dim_max){
        $dim_max = $campi[4];
    }
}
my $nome_file;
foreach my $linea (@linee_contenuto) {
    my @campi = split /\s+/, $linea;
    if ($campi[4] == $dim_max){
        $nome_file = $campi[8];
    }
}
print "$nome_file: $dim_max\n";

#4
my $input = <STDIN>;
my $contenuto_cart = qx{ls -l $path/$input};

my @linee_contenuto = split /\n/, $contenuto_cart;
foreach my $linea (@linee_contenuto) {
    my @campi = split /\s+/, $linea;
    print "$campi[8]\n";
}
