use strict;
my $map = shift @ARGV || "map.dump";
my $data = undef;
{
    $data = do $map;
    die "Bad dump" unless ref($data) eq 'ARRAY';
}

$| = 1;
while(my $line = <STDIN>) {
    my @v = split(/\s+/,$line);
    my $i = pop @v;
    my @d = @{$data->[$i]};
    print "i1 0 0.1 ".join(" ",@d[1..$#d]).$/;
}
