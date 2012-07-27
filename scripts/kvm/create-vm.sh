#!/bin/sh


export NAME=f17-base
export UUID=`uuidgen`

fallocate -l 5G /var/lib/libvirt/images/$NAME.img

virt-install --connect qemu:///system \
     --name $NAME \
     --ram 512 --vcpus=2 --uuid=$UUID \
     --disk path=/var/lib/libvirt/images/$NAME.img \
     --location /home/vbraun/Virtual/iso/Fedora-17-x86_64-DVD/ \
     --initrd-inject kickstart/$NAME.ks \
     --extra-args "ks=file:/$NAME.ks console=ttyS0,115200 text" \
     --os-type=linux --os-variant=fedora17 --graphics none --hvm \
     --network network=kvm-nat,mac=54:52:00:00:10:00

