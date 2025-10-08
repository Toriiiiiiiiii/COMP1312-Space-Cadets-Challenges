#!/usr/bin/python3

# COMP1312 : Programming 1
# Space Cadets Challenge 2/3 : Barebones
# ---
# Author: Tori Hall
# Date: 08-10-2025
# Description: Compiler for the Barebones programming language

import sys

from bbc import lexer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"USAGE: {sys.argv[0]} <file>")
        exit(1)

    with open(sys.argv[1], "r") as f:
        contents = f.read()

    lex = lexer.Lexer(contents, sys.argv[1])
    while lex.index < len(lex.src):
        tok: lexer.Token = lexer.getToken(lex)

        print(f"{tok.file}:{tok.line}:{tok.col}: TOKEN {tok.tokType}, {tok.val}")
