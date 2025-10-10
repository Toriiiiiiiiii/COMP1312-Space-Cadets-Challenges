#!/usr/bin/python3

# COMP1312 : Programming 1
# Space Cadets Challenge 2/3 : Barebones
# ---
# Author: Tori Hall
# Date: 08-10-2025
# Description: Compiler for the Barebones programming language

import sys

from bbc import lexer, parser, interpreter


def printUsage():
    print(f"USAGE: {sys.argv[0]} <subcommand> <file>")
    print()
    print("Valid Subcommands:")
    print(" * com  -> Compiles a program.")
    print(" * int  -> Interprets a program.")


def interpretProgram(ast: parser.ASTNode):
    inter = interpreter.Interpreter()
    interpreter.intGetFunctions(inter, ast)

    returnValue = interpreter.intRunFunction(inter, "main", [])

    # print(f"-- Process finished with code {returnValue.val}")
    # return int(returnValue.val)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        printUsage()
        exit(1)

    if sys.argv[1] not in ["com", "int"]:
        printUsage()
        exit(1)

    with open(sys.argv[2], "r") as f:
        contents = f.read()

    lex = lexer.Lexer(contents, sys.argv[2])
    toks = []
    while lex.index < len(lex.src):
        tok: lexer.Token = lexer.getToken(lex)
        if tok.tokType == "EOF":
            break

        if tok.tokType == "ERROR":
            print(f"Lexer returned with error {tok.val}. Aborting...")
            exit(1)

        toks.append(tok)

    par = parser.Parser(toks)
    ast = parser.buildAST(par)

    parser.printASTNode(ast, 0)

    # Interpret AST
    if sys.argv[1] == "int":
        interpretProgram(ast)
