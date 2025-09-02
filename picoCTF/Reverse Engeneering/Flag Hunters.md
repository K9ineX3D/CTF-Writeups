## Description:
Lyrics jump from verses to the refrain kind of like a subroutine call. There's a hidden refrain this program doesn't print by default. Can you get it to print it? There might be something in it for you.

## 👉 Initial Connection:
Connected to the server and got this song lyrics program. It started playing through verses about hacking and CTFs:
```bash
Command line wizards, we're starting it right,
Spawning shells in the terminal, hacking all night.
...
Crowd:
```
## 👉 Testing the Input:
When it first asked for crowd input, I tried:
Crowd: hello
It printed "Crowd: hello" and continued to the next verse.

## 👉 Tried again with a fresh connection:
```bash
Crowd: """
```
Same behavior - it used my input from the first crowd prompt for all the later crowd sections too.

## 🔎 Source Code Analysis:
Looking at the code, I could see why:
```bash
elif re.match(r"CROWD.*", line):
    crowd = input('Crowd: ')
    song_lines[lip] = 'Crowd: ' + crowd  # Permanently modifies the line
    lip += 1"
```
It actually overwrites the song line with my input, so when the program loops back or hits that same line again, it just prints my modified version instead of asking again.

The flag gets loaded here:
```bash
flag = open('flag.txt', 'r').read()
secret_intro = '''Pico warriors rising, puzzles laid bare, ...''' + flag + '\n'
```
But the program starts from [VERSE1], skipping the beginning where the flag is.

## 🔎 Finding the Vuln:
This line processing looked exploitable:
```bash
for line in song_lines[lip].split(';'):
```
It splits on semicolons! So if I put a semicolon in my crowd input, it might treat parts as separate commands.\
Also saw the navigation system:
```bash
elif re.match(r"RETURN [0-9]+", line):
    lip = int(line.split()[1])
```
This can jump to any line number. Line 0 would be the beginning with the flag.

## 🚀 Exploit:
On a fresh connection, at the first (and only) crowd prompt:
```bash
Crowd: testtest;RETURN 0
```
The semicolon injection worked! It treated RETURN 0 as a separate command, jumped back to line 0 and started printing from the beginning, revealing the flag in the intro lyrics.

## 🚩flag: picoCTF{70637h3r_f0r3v3r_b248b032}
