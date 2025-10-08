# Token -- Smallest unit that will be used by the parser.
class Token:
    def __init__(self, line, col, file, tokType, val):
        self.line = line
        self.col = col
        self.file = file
        self.tokType = tokType
        self.val = val


# Lexer - Containing structure for performing lexical analysis.
class Lexer:
    def __init__(self, src, path):
        self.src = src
        self.path = path
        self.line = 1
        self.col = 1
        self.index = 0


# Helper function to get current character from source code.
def lexAt(lex) -> str:
    return lex.src[lex.index]


# Helper function to get current character and move on.
def lexConsume(lex: Lexer) -> str:
    ch = lexAt(lex)
    lex.index += 1

    lex.col += 1
    if ch == "\n":
        lex.col = 1
        lex.line += 1

    return ch


# Skip any whitespace characters during analysis
def skipWhitespace(lex) -> None:
    while lex.index < len(lex.src) and lexAt(lex) in " \t\r\n":
        lexConsume(lex)


# Get any single-char tokens.
def getSingleton(lex) -> Token:
    ch = lexAt(lex)
    if ch in "([{":
        return Token(lex.line, lex.col, lex.path, "LPAREN", lexConsume(lex))
    elif ch in ")]}":
        return Token(lex.line, lex.col, lex.path, "RPAREN", lexConsume(lex))
    elif ch == ";":
        return Token(lex.line, lex.col, lex.path, "SEMICOLON", lexConsume(lex))

    else:
        return Token(lex.line, lex.col, lex.path, "NULL", "")


# Get a keyword
def getKeyword(lex: Lexer) -> Token:
    validStarters = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if lexAt(lex) not in validStarters:
        return Token(lex.line, lex.col, lex.path, "NULL", "")

    validBody = validStarters + "0123456789"

    line = lex.line
    col = lex.col
    wrd = ""

    while lex.index < len(lex.src):
        if lexAt(lex) not in validBody:
            break

        wrd += lexConsume(lex)

    return Token(line, col, lex.path, "KEYWORD", wrd)


# Get a string literal
def getStringLiteral(lex: Lexer) -> Token:
    if lexAt(lex) in "\"'":
        line = lex.line
        col = lex.col
        terminator = lexConsume(lex)
        lit = ""

        # Don't try to read past the EOF!!!
        while lex.index < len(lex.src):
            if lexAt(lex) == terminator and (len(lit) == 0 or lit[-1] != '\\'):
                lexConsume(lex)
                return Token(line, col, lex.path, "STRING", lit)

            lit += lexConsume(lex)

        # If EOF was reached before a terminator, throw an error.
        print(f"{lex.path}:{line}:{col}: Lexer Error - Unterminated string literal.")
        exit(1)
    else:
        return Token(lex.line, lex.col, lex.path, "NULL", "")


# Extract the next token from the source code.
def getToken(lex) -> Token:
    while lex.index < len(lex.src):
        skipWhitespace(lex)
        if lex.index >= len(lex.src):
            break

        tok = getSingleton(lex)
        if tok.tokType != "NULL":
            return tok

        tok = getKeyword(lex)
        if tok.tokType != "NULL":
            return tok

        tok = getStringLiteral(lex)
        if tok.tokType != "NULL":
            return tok

        lexConsume(lex)

    return Token(lex.line, lex.col, lex.path, "EOF", "EOF")
