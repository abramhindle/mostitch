use strict;

sub numsort {
    sort {$a<=>$b} @_;
}

my @amps = numsort qw(100 1000 10000 20000);
my @frqs = numsort qw(40 80 100 160 240 350 440 700 1000);
my @cars = numsort qw(0.1  0.5 1.0 2.0);
my @mods = numsort qw(0.7 1.0 2.8 5.0 7.5 10.0 0.3 0.1);
my @indx = numsort qw(0.1 0.5 1.0 2.0 4.0 5.0 7.0 8.0 10.0);
my $dur = 1024/44100.0;
my $t = 0;
my $time = 0;
sub mytime {
    my ($t) = @_;
    return sprintf('%0.5f',$t * $dur);
}


open(FILE,"fm.sco");
print $_ while <FILE>;
close(FILE);
my @params = ();

for my $amp (@amps) {
    for my $frq (@frqs) {
        for my $car (@cars) {
            for my $mod (@mods) {
                for my $indx (@indx) {
                    my $time = mytime( $t );
                    print "i1 $time 0.01 $amp $frq $car $mod $indx$/";
                    $t++;
                    push @params, [$t,$amp,$frq,$car,$mod,$indx];
                }
            }
        }
    }
}

print "i555 0 ".mytime( $t ).$/;
use Data::Dumper;
open(FILE,">","map.dump");
print FILE Dumper(\@params);
close(FILE);
