# BareBones interpreter in x86_64
*Because fuck you, thats why!*

## Introduction
Hi! This is my solution to the week 2 & 3 challenges for Space Cadets. It is a (barely functional) barebones interpreter, written ~~with hopes and dreams~~ using x86_64 fasm assembly for linux, with no libraries (not even libc!)
-# Please note that this solution will only be functional on x86_64-based machines running Linux, and is *only* tested on my personal machine. If you want to run this, good luck!

## Why?
I did this for the same reason humans do anything - pure overconfidence. This project has consumed hours of my life and left me in tears at least 3 times. Don't expect to understand this code - I don't even understand a large amount of it.

## Limitations
In order to make my life less painful, some sacrifices had to be made for this project.

1. All variables are only a single character in length. Any subsequent characters are ignored (eg `name == n`).
2. Limited to unsigned integers only.
3. No proper error detection - errors will cause unintended behaviour (most likely a segfault!)
4. Limited program size.

## Extensions
To try and counteract the limitations of the interpreter, I have also extended the language in several ways

1. (Almost) 256 variables!! Almost all characters can hold a variable, eg `£`, `0`, and `)` are all valid variable names!
2. `print` instruction: Prints the value of a variable.
3. `do` loops: Repeats some operations a fixed number of times before continuing
3. `read` instruction: Reads a number from the user and stores it in a variable.
4. Comments! All characters that appear after a `#` on the same line are ignored.

## Understanding the Source code
**Don't even try.**

The code is layed out as following:
* `src/bb.asm`: Main file. If you are compiling the source yourself, assemble this file.
* `src/lexer.asm`: Responsible for all lexical analysis (If you can even call it that!)
* `src/macros.asm`: Some useful macros used accross the codebase
* `src/ops.asm`: Contains code used for enqueueing/dequeueing operations.
* `src/print.asm`: Contains code to print numbers.
* `src/strucs.asm`: Contains data structure definitions.
* `src/syscall.asm`: Contains macros for various syscalls.
* `src/utils.asm`: General utility functions like `strlen` and `strton`.


-# Segfault Counter: 37
