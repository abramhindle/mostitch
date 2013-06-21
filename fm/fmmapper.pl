use strict;
my $map = shift @ARGV || "map.dump";
my $data = undef;
{
    $data = do $map;
    die "Bad dump" unless ref($data) eq 'ARRAY';
}

$| = 1;
my $t;
while(my $line = <STDIN>) {
    my @v = split(/\s+/,$line);
    my $i = $v[4];#pop @v;
    $t = $v[1];
    my @d = @{$data->[$i - 1]};
    print "i1 $t 0.1 ".join(" ",@d[1..$#d]).$/;
}
$t = $t+1;
print "i -555 $t 0$/";
