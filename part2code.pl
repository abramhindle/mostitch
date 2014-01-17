#!/usr/bin/perl
# takes a weka PART output and produces python code!
my @rules = ();
my $rule ="";
while(my $line = <DATA>) {
	chomp($line);
	if ($line) {
		$rule .= "$line ";
	} else {
		push @rules, $rule;
		$rule = "";
	}
}
my $i = 1;
warn $i++." ".$_.$/ foreach @rules;

@newrules = map { 
	my ($cond,$return) = split(/:/,$_);
	$cond =~ s/AND/and/g;
	$return =~ s/\(.*\)//;
	$return =~ s/\s//g;
	my $ret;
	if ($cond !~ /^\s*$/) {
		$ret = "\telif ($cond):\n\t\treturn \"$return\"\n";
	} else { # last one
		$ret = "\telse:\n\t\treturn \"$return\"\n";
	}
	$ret
} @rules;
$newrules[0] =~ s/elif/if/;
print "def partfun(a,b):\n";
print join("", @newrules);
print "\n";


__DATA__
a > 299 AND
a <= 410 AND
b <= 410: D (163.0)

b > 408 AND
b <= 423 AND
b > 410: A (116.0/1.0)

a > 153 AND
a <= 338 AND
a > 181 AND
b <= 238 AND
a > 199 AND
a <= 232: B (92.0)

a > 152 AND
a > 338 AND
b <= 459 AND
a > 423 AND
a > 436: C (74.0/1.0)

b <= 92 AND
b <= 53 AND
b <= 38: A (38.0)

a > 152 AND
b <= 354 AND
a > 233 AND
b <= 238 AND
a <= 266: B (48.0)

a > 152 AND
b <= 354 AND
b > 238 AND
a <= 277 AND
b <= 301: D (22.0)

b <= 92 AND
b <= 53 AND
a > 42 AND
b <= 44: A (30.0/3.0)

a > 152 AND
b <= 354 AND
b > 167 AND
a <= 181 AND
b <= 181: C (95.0/30.0)

b <= 92 AND
b > 69: A (20.0)

b > 459: D (39.0)

a <= 83 AND
b <= 53 AND
a > 43 AND
a <= 53 AND
a <= 52 AND
a > 49: A (13.0)

b > 417 AND
a <= 433 AND
a > 423: C (27.0)

a > 167 AND
b > 354 AND
a > 411: A (31.0/3.0)

a > 153 AND
a > 167 AND
b <= 301 AND
b <= 251 AND
a > 181 AND
a <= 216: B (60.0/13.0)

a > 152 AND
b > 354 AND
b <= 409 AND
b > 408: A (8.0/2.0)

a > 152 AND
a > 167 AND
b > 251 AND
b <= 301: B (18.0)

a > 152 AND
a > 167 AND
b > 267 AND
a <= 302: B (8.0/3.0)

a > 152 AND
a > 167 AND
b <= 303: B (75.0/37.0)

a > 152 AND
b > 165 AND
b > 166: D (44.0/8.0)

a <= 83 AND
b <= 53 AND
a > 43 AND
a <= 53: B (15.0/3.0)

b <= 70 AND
b <= 52 AND
a > 40 AND
b > 39: A (28.0/6.0)

b <= 70 AND
b > 56 AND
a > 55: D (27.0/6.0)

a <= 128 AND
a > 83 AND
b <= 196: C (71.0/1.0)

b <= 150 AND
b > 55 AND
a <= 141 AND
a > 54 AND
b > 70 AND
b > 130: B (31.0/4.0)

a > 153 AND
b <= 165 AND
a > 156 AND
a <= 165: B (28.0)

b <= 150 AND
b > 141: A (104.0/59.0)

a > 152 AND
b <= 165 AND
b > 153 AND
b <= 155: D (19.0/5.0)

b > 146 AND
a <= 153 AND
b <= 338 AND
a > 141: A (41.0/12.0)

b > 165 AND
a <= 118 AND
a > 94: A (23.0/4.0)

b > 147 AND
b > 165: C (34.0/4.0)

b > 105 AND
a <= 150 AND
b > 134: B (12.0/1.0)

b > 105 AND
b > 154 AND
a > 161: D (14.0/8.0)

b > 105: C (20.0/6.0)

b > 55 AND
b <= 57: B (11.0/2.0)

b > 56 AND
b <= 94: A (6.0)

b > 70 AND
a <= 98: B (4.0/1.0)

a > 98 AND
b <= 70: B (3.0/1.0)

a > 44 AND
b <= 70: D (33.0/10.0)

a <= 41 AND
a <= 40 AND
a > 39 AND
b <= 40: D (3.0/1.0)

b > 39: A (15.0/7.0)

: B (2.0)

