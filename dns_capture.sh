#!/bin/sh
LOC=/var/captures/dns

fn=dns_$(date +"%Y-%m-%d_%H:%M").pcap

D=$(date +"%Y/%m/%d")
mkdir -p ${LOC}/${D}
o=${LOC}/${D}/$fn
echo $o
timeout -2 300 tcpdump -n -i sniff1 'udp port 53 and ( udp[10] & 0x04 != 0 )' -w $o -s 0
