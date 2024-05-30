$matricola = "220666";
qx{mkdir $matricola};

if($#ARGV==0){
    qx{cp $ARGV[0]/*.pl $matricola};
}else{
    qx{cp ../*/*.pl $matricola};
}

$n_file = qx{ls -1 $matricola | wc -l};
print "Numero di file copiati: $n_file";