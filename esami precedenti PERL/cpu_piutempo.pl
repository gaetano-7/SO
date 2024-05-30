@ps = qx(ps -A);
$max = "00:00:00";
shift @ps;
for (@ps){
	@split = split " ";
	if ($split[2] ge $max){
		$max = $split[2];
		$pid = $split[0];
	}
}
print "$pid\n";