### Name: heap 0
### Catagory: Binary Exploitation
### Difficulty: Easy

## 👉 What I Did:
So I connected to this heap0 challenge and saw it had two buffers on the heap:\
Heap State:\
+-------------+----------------+\
[*] Address   ->   Heap Data   
+-------------+----------------+\
[*]   0x59c100c0d2b0  ->   pico\
+-------------+----------------+\
[*]   0x59c100c0d2d0  ->   bico\
+-------------+----------------+

The program said the second one (safe_var) was "protected" but looking at the addresses, they're pretty close together.\
Differnce was about 32 bytes.

## 👉 Finding the Bug:
I checked the source code and found this sketchy function:\
void write_buffer() {\
    printf("Data for buffer: ");\
    fflush(stdout);\
    scanf("%s", input_data);

The input_data buffer is only 5 bytes but scanf will read however much I give it. Classic overflow setup.

## 👉 The Win Condition:
void check_win() {\
    if (strcmp(safe_var, "bico") != 0) {\
        printf("\nYOU WIN\n");

Looking at check_win(), I need safe_var to be anything except "bico". So if I can corrupt safe_var with literally anything else, I win.

## ☠️ My Attack:
I tried a long string: Hellothisisatestpayloadof32character\
This overflowed from the first buffer into the second one, changing safe_var from "bico" to some garbage. Now I checked option 1:\
Heap State:\
+-------------+----------------+\
[*] Address   ->   Heap Data   \
+-------------+----------------+\
[*]   0x606a5e3272b0  ->   Hellothisisatestpayloadof32character\
+-------------+----------------+\
[*]   0x606a5e3272d0  ->   cter\
+-------------+----------------+

safe_var got corrupted and value changed.

Now try to print the flag.\
YOU WIN\
picoCTF{my_first_heap_overflow_4fa6dd49}

## 👉 Why It Worked
The two malloc(5) calls put the buffers right next to each other in memory. When I stuffed 35 characters into a 5-byte buffer, it spilled over and corrupted the "protected" variable.\
Pretty straightforward heap overflow - no fancy ROP chains or shellcode needed, just change one value to win.
