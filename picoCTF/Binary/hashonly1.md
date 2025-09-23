## Description
Here is a binary that has enough privilege to read the content of the flag file but will only let you know its hash. If only it could just give you the actual content!\
Additional details will be available after launching your challenge instance.

## Steps & Findings
**1. Access**

Boot the instance and SSH into the target.

**2. Discover the target binary**

There is a binary called flaghasher.\
Running it returns an MD5 hash of a root-owned file (we only get the hash, not the file contents.

**3. Inspect the binary for hints**

Command used:
```bash
strings flaghasher
```
Among other strings, this line is present:
```bash
/bin/bash -c 'md5sum /root/flag.txt'
```
The binary invokes /bin/bash -c 'md5sum /root/flag.txt' — so it runs the external md5sum program on /root/flag.txt.

**4. Trick the binary into revealing contents**
The binary uses md5sum without specifying the full path, so we can exploit PATH manipulation to substitute our own command
```bash
cp /usr/bin/cat /usr/bin/md5sum
```
Breaking it down:

● cp = copy command\
● /usr/bin/cat = source (the real cat command)\
● /usr/bin/md5sum = destination (replacing the real md5sum)

What happens: When flaghasher calls md5sum, it actually runs cat instead!

Result: Re-running flaghasher now prints the contents of /root/flag.txt.

## Flag: picoCTF{sy5teM_b!n@riEs_4r3_5c@red_0f_yoU_07e85021}
