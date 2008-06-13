#!/bin/sh
LOC=/var/captures/dns

fn=dns_$(date +"%Y-%m-%d_%H:%M").pcap

o=${LOC}/$fn
echo $o
tcpdump -n -i sniff1 'udp port 53 and ( udp[10] & 0x04 != 0 )' -w $o -s 0 -C 10
