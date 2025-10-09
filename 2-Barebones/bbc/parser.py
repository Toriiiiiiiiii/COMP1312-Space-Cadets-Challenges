import lexer


class ASTNode:
    def __init__(self, line, col, file, nodeType, val):
        self.line = line
        self.col = col
        self.file = file
        self.nodeType = nodeType
        self.val = val

        self.children = []


class Parser:
    def __init__(self, tokens):
        self.toks = tokens
