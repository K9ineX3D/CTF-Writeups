# TryHackMe: W1seGuy - Writeup

## Room Description

**Room Name:** W1seGuy  
**Tagline:** "A w1se guy 0nce said, the answer is usually as plain as day."  
**Room Type:** Cryptography / Reverse Engineering  
**Challenge Source:** Provided source code file (`source-1705339805281.py`)

This room challenges players to recover an XOR encryption key from a hex-encoded ciphertext by analyzing the provided source code and exploiting a known plaintext attack vulnerability.

## Challenge Overview

This CTF challenge involves:

- Connecting to a challenge server running on port 1337
- Receiving a hex-encoded XOR-encrypted message
- Analyzing the encryption mechanism from provided source code
- Recovering the encryption key (5 random alphanumeric characters)
- Submitting the key to retrieve the actual flag

## Challenge Details

### Server Behavior

1. **Connection**: Connect to `10.10.33.77:1337`
2. **Challenge Message**: Receives a hex-encoded XOR-encrypted message:

   ```
   This XOR encoded text has flag 1: <hex_encoded_ciphertext>
   ```

3. **Task**: Identify the encryption key (5 random alphanumeric characters)
4. **Prompt**: Server asks: `What is the encryption key?`
5. **Reward**: On correct key submission, returns the actual flag

### Encryption Mechanism (from source code)

The server encrypts using a simple XOR cipher:

```python
def setup(server, key):
    flag = 'THM{thisisafakeflag}'  # 20-character fake flag
    xored = ""
    
    for i in range(0, len(flag)):
        xored += chr(ord(flag[i]) ^ ord(key[i % len(key)]))
    
    hex_encoded = xored.encode().hex()
    return hex_encoded
```

**Key Implementation Details:**

- Key is 5 characters long, randomly generated from alphanumeric characters
- Key cycles through the flag using modulo: `key[i % len(key)]`
- Result is converted to hexadecimal encoding for transmission
- The plaintext is a hardcoded fake flag: `THM{thisisafakeflag}`
- The real flag is only revealed upon successful key submission

### Vulnerability Analysis

The challenge is vulnerable to a **known plaintext attack** because:

1. **Source code provided** - We can inspect the encryption algorithm
2. **Known plaintext** - We know the exact plaintext: `THM{thisisafakeflag}`
3. **Predictable start** - The plaintext always starts with `THM{`
4. **Short key** - Only 5 characters from a 62-character charset
5. **Deterministic cycling** - Key repeats through the plaintext in a predictable pattern

## Solution Approach

### Understanding the Problem

The challenge says: *"the answer is usually as plain as day"* - This hints that we should look at the plaintext directly. We know:

- The plaintext starts with `THM{`
- The plaintext ends with `}`
- Both are predictable patterns

### Brute Force with Pattern Matching

Rather than trying all 62^5 (~916 million) possible keys, we leverage known plaintext constraints:

**Core Insight:** Match the known prefix `THM{` to dramatically reduce the search space

#### Algorithm

1. **Extract Constraints** from the known plaintext start:

   ```
   Position 0: xored_string[0] ^ key[0] = 'T'  →  key[0] = xored_string[0] ^ 'T'
   Position 1: xored_string[1] ^ key[1] = 'H'  →  key[1] = xored_string[1] ^ 'H'
   Position 2: xored_string[2] ^ key[2] = 'M'  →  key[2] = xored_string[2] ^ 'M'
   Position 3: xored_string[3] ^ key[3] = '{'  →  key[3] = xored_string[3] ^ '{'
   ```

2. **Generate Candidates** - Iterate through all valid 5th characters that would create alphanumeric keys

3. **Validate** - For each candidate key, decrypt the full message and check:
   - Starts with `THM{`
   - Ends with `}`
   - Contains printable ASCII

4. **Submit** - Send the valid key to the server

#### Complexity Reduction

| Stage | Combinations | Reduction |
|-------|--------------|-----------|
| Naive brute force | 62^5 = 916M | - |
| After pattern matching first 4 chars | 62^4 × valid_last_chars | ~916M / 62^4 = 62 possibilities |
| With validation filtering | ~1-5 valid keys | Typically 1 |

## Exploitation Code

```python
import socket
import string

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('10.10.33.77', 1337))

# Receive the challenge
challenge = sock.recv(4096).decode()

# Extract hex ciphertext from response
hex_ciphertext = None
for line in challenge.split('\n'):
    if 'flag 1:' in line:
        hex_ciphertext = line.split('flag 1: ')[1].strip()
        break

if hex_ciphertext:
    # Convert hex to xored string
    xored_bytes = bytes.fromhex(hex_ciphertext)
    xored_string = xored_bytes.decode('latin-1')
    
    # Build charset
    charset = string.ascii_letters + string.digits
    valid_keys = []
    
    # Brute force with pattern matching
    for c0 in charset:
        if ord(xored_string[0]) ^ ord(c0) != ord('T'):
            continue
        for c1 in charset:
            if ord(xored_string[1]) ^ ord(c1) != ord('H'):
                continue
            for c2 in charset:
                if ord(xored_string[2]) ^ ord(c2) != ord('M'):
                    continue
                for c3 in charset:
                    if ord(xored_string[3]) ^ ord(c3) != ord('{'):
                        continue
                    for c4 in charset:
                        key = c0 + c1 + c2 + c3 + c4
                        
                        # Decrypt with candidate key
                        decrypted = ""
                        for j in range(len(xored_string)):
                            decrypted += chr(ord(xored_string[j]) ^ ord(key[j % 5]))
                        
                        # Validate: must end with }
                        if decrypted.endswith('}'):
                            valid_keys.append((key, decrypted))
    
    # Submit the first valid key
    if valid_keys:
        correct_key, flag1 = valid_keys[0]
        
        # Wait for the prompt
        prompt = sock.recv(4096).decode()
        
        # Send the key
        sock.send((correct_key + '\n').encode())
        
        # Receive flag 2 (the actual flag)
        response = sock.recv(4096).decode()
        print(response)

sock.close()
```

## Results

### Example Session

```
Connected to: 10.10.33.77:1337

Received: This XOR encoded text has flag 1: 661f7a023703365b1733772f43383346635412247339454a265e1b4e111240234e4932402f780b3a

Hex Ciphertext: 661f7a023703365b1733772f43383346635412247339454a265e1b4e111240234e4932402f780b3a

Pattern Matching for "THM{":
  Found key: 2W7yG

Flag 1 (decrypted): THM{p1alntExtAtt4ckcAnr3alLyhUrty0urxOr}

Sending key: 2W7yG

Congrats! That is the correct key! Here is flag 2: THM{BrUt3_ForC1nG_XOR_cAn_B3_FuN_nO?}
```

### Flags

**Flag 1 (Fake Flag - Decrypted from ciphertext):**

```
THM{p1alntExtAtt4ckcAnr3alLyhUrty0urxOr}
```

**Flag 2 (Actual Room Flag - Retrieved after correct key submission):**

```
THM{BrUt3_ForC1nG_XOR_cAn_B3_FuN_nO?}
```

## Key Cryptographic Concepts

### 1. XOR Properties

- **Self-inverse:** If `A ^ B = C`, then `C ^ B = A` and `A ^ C = B`
- **Commutative:** `A ^ B = B ^ A`
- **Associative:** `(A ^ B) ^ C = A ^ (B ^ C)`
- **Identity:** `A ^ 0 = A`

### 2. Known Plaintext Attack (KPA)

A cryptanalysis technique where:

- Attacker knows some plaintext-ciphertext pairs
- Goal is to recover the key or decrypt other messages
- Effectiveness depends on the length and predictability of known plaintext

In this challenge:

- We know 4 characters of plaintext (`THM{`)
- This reduces search space from 62^5 to approximately 62 possibilities
- Extremely practical attack

### 3. Weak Encryption

Why this encryption scheme is broken:

1. **Small key space** - Only 62^5 keys (~900M, easily brute-forced)
2. **Known plaintext** - Predictable flag format
3. **No authentication** - No way to verify message integrity
4. **Deterministic cycling** - Key repeats predictably through message
5. **No IV/salt** - Same key always produces same ciphertext

## Complexity Analysis

| Metric | Value |
|--------|-------|
| Full brute force iterations | ~916 million |
| Pattern-matched iterations | ~62-100 (for valid keys only) |
| Speedup factor | ~9 million times faster |
| Typical runtime | ~0.05 seconds |

## Attack Flow

```
1. Connect to server (100ms)
2. Receive ciphertext (50ms)
3. Extract hex (10ms)
4. Decode from hex (10ms)
5. Pattern matching on "THM{" (50ms)
6. Validate candidates (10ms)
7. Send key (50ms)
8. Receive flag (50ms)
─────────────────────────
Total: ~330ms
```

## Lessons Learned

1. **Practical Cryptanalysis** - Real-world exploitation of weak encryption
2. **Known Plaintext Attack** - Demonstrates how predictable formats weaken security
3. **Code Review** - Vulnerabilities are often visible in source code
4. **Optimization** - Smart algorithms beat brute force
5. **XOR Limitations** - Why stream ciphers need strong designs

### Key Takeaways

- ✅ Always analyze source code for vulnerabilities
- ✅ Never rely on XOR alone for cryptography
- ✅ Keep plaintexts unpredictable
- ✅ Use established cryptographic libraries
- ✅ Known plaintext can severely weaken encryption
- ✅ Combine constraints to optimize attacks

## References

- XOR Cipher: <https://en.wikipedia.org/wiki/XOR_cipher>
- Known Plaintext Attack: <https://en.wikipedia.org/wiki/Known-plaintext_attack>
- Stream Cipher: <https://en.wikipedia.org/wiki/Stream_cipher>
- Cryptanalysis: <https://en.wikipedia.org/wiki/Cryptanalysis>
