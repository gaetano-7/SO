#!/usr/bin/perl
use strict;
use warnings;

# Verifica che siano presenti due argomenti
if (@ARGV != 2) {
    die "Usage: $0 -n|-o COMMAND\n";
}

my $opzione = shift @ARGV;
my $comando = shift @ARGV;

# Verifica che l'opzione sia valida
unless ($opzione eq '-n' || $opzione eq '-o') {
    die "Opzione non valida. Deve essere -n o -o.\n";
}

# Esegui il comando man per ottenere la documentazione del comando specificato
my $man_output = `man $comando`;

# Estrai le opzioni brevi dal risultato del comando man
my @opzioni_brevi = $man_output =~ /(?:^|\s)(-\w)(?=\s)/g;

# Conta il numero di opzioni brevi
if ($opzione eq '-n') {
    my $numero_opzioni = scalar @opzioni_brevi;
    print "$numero_opzioni opzioni brevi\n";
}
# Stampa le opzioni brevi su un file
elsif ($opzione eq '-o') {
    open my $file_output, '>', 'opzioni_brevi.log' or die "Impossibile aprire il file opzioni_brevi.log: $!";
    print $file_output join("\n", @opzioni_brevi), "\n";
    close $file_output;
    print "Le opzioni brevi sono state scritte su opzioni_brevi.log\n";
}
