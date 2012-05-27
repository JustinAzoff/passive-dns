passive-dns consists of a number of independent tools:

 * passive-dns-capture: creates pcaps
 * passive-dns-process: converts pcaps to .txt files
 * passive-dns-merge: merges multiple .txt together
 * passive-dns-do-merge: runs passive-dns-merge with the appropriate arguments
 * passive-dns-searchserver: HTTP REST Server
 * passive-dns-upload: uploads a pcap to the HTTP Server


If you have one box that does everything, run:

 * passive-dns-capture
 * passive-dns-process
 * passive-dns-do-merge
 * passive-dns-searchserver

If you have multiple sensors, then on the head node run:

 * passive-dns-process
 * passive-dns-do-merge
 * passive-dns-searchserver

and on the sensors, run:

 * passive-dns-capture
 * passive-dns-upload


The recommended setup is to run everything using runit. `passive-dns-conf` can set everything up for you

    adduser --system pdns
    passive-dns-conf pdns pdns /etc/passive-dns /var/log/passive-dns
    for s in capture process merge server; do
        update-service --add /etc/passive-dns/$s passive_dns_$s
    done

