#!/usr/bin/perl

use strict;
use Net::DNS::Resolver;

my $certname;
my $currentIp;
my $query;
my $publicDNS;
#don't put ft.com in...
#my $domainName         = "<%= scope.function_hiera(["dns_name", 'set.my.domain']) %>";
#my $konstructorPass    = "<%= scope.function_hiera(["konstructor_password", 'IdidntSetApasswordForAutoDNS']) %>";
#my $konstructorUname   = "<%= scope.function_hiera(["konstructor_user", 'IdidntSetAuserForAutoDNS']) %>";
my $domainName         = "dave";#<%= scope.function_hiera(["dns_name", 'set.my.domain']) %>";
my $konstructorPass    = "dave";#<%= scope.function_hiera(["konstructor_password", 'IdidntSetApasswordForAutoDNS']) %>";
my $konstructorUname   = "dave";#<%= scope.function_hiera(["konstructor_user", 'IdidntSetAuserForAutoDNS']) %>";

my $resolver           = Net::DNS::Resolver->new(nameservers => [qw(8.8.8.8)],);


#perl doesn't have a trim function apparently.
sub ltrim($);
#http://www.somacon.com/p114.php
sub ltrim($){
    my $string = shift;
    $string =~ s/^\s+//;
    return $string;
}



#get our public from AWS metadata thingy
$currentIp = `curl --silent  http://169.254.169.254/latest/meta-data/public-ipv4`;
if ($?){
    #then we got an error, lets assume that we don't have a public IP
    print "No public IP found\n";

    die();
}

#drop out to the shell to extract the cert name from the puppet conf
$certname = `cat /etc/puppet/puppet.conf | grep certname`;
#comes out in the form of certname = dfgsdf.sgf.sfgs.fgs.com

#get rid of anything before the =
my @certnameParts = split('=', $certname );

#now split up the domain name
@certnameParts = split ('\.', $certnameParts[1]);


#we now have our node name.
$certname =  $certnameParts[0];

#get rid of the white space at the start of the string
$certname = ltrim($certname);

print "We have the following info:\n\t $currentIp\n\t $certname\n";

#Lets see if we need to change anything first:
$query       = $resolver->search("$certname.$domainName.ft.com");

if ($query){
    foreach my $rr ($query->answer) {
        next unless $rr->type eq "A";
        $publicDNS = $rr->address;
        print "Found DNS record: ". $publicDNS ."\n";

    }
}
#check to see if the public IP matches the DNS:

if ($publicDNS eq $currentIp){
    print "Current IP $currentIp matches current DNS $certname.$domainName.ft.com IP: $publicDNS\n";
    exit(0);
}else{

    print "Current IP $currentIp doesnt match current DNS $certname.$domainName.ft.com IP: $publicDNS\n";
}

#first, we have to delete the record.
print "Deleting old record, if any:\n";
print `curl -sS -u $konstructorUname:$konstructorPass -X DELETE  "http://konstructor.svc.ft.com:80/v1/dns/delete?zone=ft.com&name=$certname.$domainName"`;

if ($?){
    print "Deleteing record failed\n";
}else{
    print "Old record Deleted\n";
}
print "Creating new record:\n";
print `curl -sS -u $konstructorUname:$konstructorPass -X POST "http://konstructor.svc.ft.com:80/v1/dns/create?zone=ft.com&name=$certname.$domainName&rdata=$currentIp&ttl=30"`;

if ($?){
    print "Creating new record failed\n";
}else{
    print "New address created\n";
}
