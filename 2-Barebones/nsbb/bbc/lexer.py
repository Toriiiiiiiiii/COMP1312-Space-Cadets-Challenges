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
    elif ch == ",":
        return Token(lex.line, lex.col, lex.path, "SEP", lexConsume(lex))

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

    if wrd in ["void", "int", "float", "string", "array"]:
        return Token(line, col, lex.path, "TYPENAME", wrd)

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


# Gets a float/int
def getNumber(lex) -> Token:
    numStarts = "-.0123456789"
    numBody = ".0123456789"

    numDots = 0
    if lexAt(lex) not in numStarts:
        return Token(lex.line, lex.col, lex.path, "NULL", "")

    line = lex.line
    col = lex.col
    lit = lexConsume(lex)

    while lex.index < len(lex.src) and lexAt(lex) in numBody:
        ch = lexConsume(lex)

        if ch == ".":
            if numDots != 0:
                print(f"{lex.path}:{line}:{col}: Lexer Error - Invalid Floating Point literal.")
                exit(1)

            numDots += 1

        lit += ch

    if numDots == 0:
        return Token(line, col, lex.path, "INTLIT", lit)
    else:
        return Token(line, col, lex.path, "FLOATLIT", lit)


# Gets a binary/unary operator.
def getOperator(lex) -> Token:
    operators = "+-*/%=<>"
    numStarts = ".0123456789"
    if lexAt(lex) not in operators:
        return Token(lex.line, lex.col, lex.path, "NULL", "")

    if lexAt(lex) == "-" and lex.src[lex.index + 1] in numStarts:
        return getNumber(lex)

    line = lex.line
    col = lex.col
    lit = ""

    while lex.index < len(lex.src) and lexAt(lex) in operators:
        lit += lexConsume(lex)

    return Token(line, col, lex.path, "OPER", lit)


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

        tok = getOperator(lex)
        if tok.tokType != "NULL":
            return tok

        tok = getNumber(lex)
        if tok.tokType != "NULL":
            return tok

        print(f"{lex.path}:{lex.line}:{lex.col}: Lexer Error - Unrecognised token '{lexAt(lex)}'.")
        return Token(lex.line, lex.col, lex.path, "ERROR", "ERR_INVALID_TOK")
        lexConsume(lex)

    return Token(lex.line, lex.col, lex.path, "EOF", "EOF")
