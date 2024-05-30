my $processi = qx{ps aux};

my @linee_processi = split /\n/, $processi;

my $cpu_minor_carico = 0;
my $nome_proc = "";
my $pid_proc_yes = 0;

foreach my $linea (@linee_processi) {
    my @campi = split /\s+/, $linea;

    if ($campi[2]==0.0 && $campi[1] > $cpu_minor_carico){
        $cpu_minor_carico = $campi[1];
        $nome_proc = $campi[10];
    }

    if ($campi[10] eq "yes"){
        $pid_proc_yes = $campi[1]
    }
    
}

print "Il PID del processo '$nome_proc' con minor carico è: $cpu_minor_carico\n";
print "Il PID del processo 'yes' è: $pid_proc_yes\n";
qx{taskset -cp $cpu_minor_carico $pid_proc_yes};
print "Affinità impostata\n";