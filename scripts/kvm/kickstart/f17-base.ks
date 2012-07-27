
lang en_US.UTF-8
keyboard us
timezone US/Eastern
auth --useshadow --passalgo=sha512
bootloader --timeout=1 --append="acpi=force console=tty0 console=ttyS0,9600 rhgb quiet biosdevname=0"
network --bootproto=dhcp --device=eth0 --onboot=yes --hostname f17-base
services --enabled=network
selinux --enforcing

# Uncomment the next line
# to make the root password be thincrust
# By default the root password is emptied
#rootpw --iscrypted $1$uw6MV$m6VtUWPed4SqgoW6fKfTZ/

#Partitions
zerombr
clearpart --all --initlabel
part biosboot   --fstype=biosboot --ondisk vda --size=1
part /          --fstype ext3 --ondisk vda --grow
part swap       --fstype swap --ondisk vda --size 1024

poweroff

%packages --excludedocs
@core

#
# Packages to Remove
#

-kudzu
-setserial
-ed
-rhpl
-wireless-tools
-kbd
-usermode
-kpartx
-dmraid
-mdadm
-lvm2

# Things it would be nice to loose
-fedora-logos
generic-logos
-fedora-release-notes
%end

#
# Add custom post scripts after the base post.
#
%post

%end

