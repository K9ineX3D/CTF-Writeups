## Compiled
Strings can only help you so far.

**Summary:**\
We were given a challenge binary that prompts for a password. Running the binary without the password fails, so we perform static analysis to inspect how the binary validates input.
```bash
└─$ ./Compiled.Compiled
Password: 1234
Try again!
```
It asks for a password, but we don't have it. Let's analyze the binary to see what's happening.\
Open the binary in Binary Ninja or Ghidra. After inspecting for a while, this code block looks interesting:
```bash
undefined8 main(void)

{
  int iVar1;
  char local_28 [32];
  
  fwrite("Password: ",1,10,stdout);
  __isoc99_scanf("DoYouEven%sCTF",local_28);
  iVar1 = strcmp(local_28,"__dso_handle");
  if ((-1 < iVar1) && (iVar1 = strcmp(local_28,"__dso_handle"), iVar1 < 1)) {
    printf("Try again!");
    return 0;
  }
  iVar1 = strcmp(local_28,"_init");
  if (iVar1 == 0) {
    printf("Correct!");
  }
  else {
    printf("Try again!");
  }
  return 0;
}
```
## Let’s breakdown what this code does
The program asks for a password, which follows the format:
```bash
DoYouEven%sCTF
```
Whatever we type between DoYouEven and CTF gets stored in the variable local_28.

The program then performs two important string comparisons:

1. First, it checks if our input matches __dso_handle.

  ● If it does, the program immediately prints “Try again!” and exits.

2. Next, it checks if our input matches _init.

  ● If the input equals _init, the password is accepted and the challenge is solved.

So the actual goal is to make local_28 equal to _init.

## Understanding the Input Handling
● The tricky part lies in how the program uses:
```bash
__isoc99_scanf("DoYouEven%sCTF", local_28);
```
This scanf call extracts everything that appears between “DoYouEven” and the first occurrence of “CTF” (ignoring spaces and non-whitespace rules).\
So, it’s clear that whatever we put right after DoYouEven (and before CTF) gets stored directly into local_28.
## Final Answer
To make local_28 equal _init, we simply provide:
```bash
DoYouEven_init
```
That satisfies the condition and solves the challenge.
