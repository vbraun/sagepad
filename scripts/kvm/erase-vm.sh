#!/bin/sh


export NAME=f17-base


virsh destroy $NAME
virsh undefine --remove-all-storage f17-base
