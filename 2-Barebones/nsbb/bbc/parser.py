from bbc import lexer


class ASTNode:
    def __init__(self, line, col, file, nodeType, val):
        self.line = line
        self.col = col
        self.file = file
        self.nodeType = nodeType
        self.val = val

        self.children = []


def printASTNode(node: ASTNode, indent: int) -> None:
    print(" " * indent, end="")
    print(f"{node.nodeType} '{node.val}' ({node.file})", end="")

    if len(node.children):
        print(" (")
        for child in node.children:
            printASTNode(child, indent+4)

        print(" " * indent, end="")
        print(")")
    else:
        print()


class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.rootNode = ASTNode(1, 1, tokens[0].file, "ROOT", "ROOT")


def parseAt(par: Parser) -> lexer.Token:
    return par.toks[0]


def parseConsume(par: Parser) -> lexer.Token:
    return par.toks.pop(0)


def parseParen(tok: lexer.Token, par: Parser) -> ASTNode:
    if tok.val == "(":
        node = ASTNode(tok.line, tok.col, tok.file, "PAREN", tok.val)
        isDone = False

        if parseAt(par).tokType == "RPAREN" and parseAt(par).val == ")":
            isDone = True

        while len(par.toks) and not isDone:
            nd = parseExpression(par)
            if not nd:
                continue

            node.children.append(nd)
            if parseAt(par).tokType == "RPAREN" and parseAt(par).val == ")":
                isDone = True
            elif parseAt(par).tokType == "SEP":
                parseConsume(par)
                continue

        if not len(par.toks):
            print(f"{tok.file}:{tok.line}:{tok.col}: Syntax Error - Could not find matching ')' for '('.")
            exit(1)

        parseConsume(par)
        return node

    elif tok.val == "{":
        node = ASTNode(tok.line, tok.col, tok.file, "CODE", tok.val)
        isDone = False

        if parseAt(par).tokType == "RPAREN" and parseAt(par).val == "}":
            isDone = True

        while len(par.toks) and not isDone:
            nd = parseStatement(par)
            if not nd:
                continue

            node.children.append(nd)
            if parseAt(par).tokType == "RPAREN" and parseAt(par).val == "}":
                isDone = True

        if not len(par.toks):
            print(f"{tok.file}:{tok.line}:{tok.col}: Syntax Error - Unterminated code block.")
            exit(1)

        parseConsume(par)
        return node

def parseAtom(par: Parser) -> ASTNode:
    tok = parseConsume(par)

    if tok.tokType == "INTLIT":
        return ASTNode(tok.line, tok.col, tok.file, "INT", tok.val)

    elif tok.tokType == "STRING":
        return ASTNode(tok.line, tok.col, tok.file, "STRING", tok.val)

    elif tok.tokType == "TYPENAME":
        ident = parseConsume(par)
        if ident.tokType != "KEYWORD":
            # TODO: Improve error message
            print("Invalid syntax.")
            exit(1)

        return ASTNode(tok.line, tok.col, tok.file, "TYPE_IDENT", f"{tok.val}:{ident.val}")

    elif tok.tokType == "KEYWORD":
        if tok.val == "function":
            # Get function name
            name = parseConsume(par)
            if name.tokType != "KEYWORD":
                print(f"{tok.file}:{name.line}:{name.col}: Syntax Error - Expected <IDENTIFIER> after 'defun'.")
                exit(1)

            # Get function parameters
            params = parseExpression(par)
            if params.nodeType != "PAREN":
                print(f"{tok.file}:{params.line}:{params.col}: Syntax Error - Expected parameters in function definition.")
                exit(1)

            # Get function return type
            ret = parseConsume(par)
            if ret.tokType != "TYPENAME":
                print(f"{tok.file}:{ret.line}:{ret.col}: Syntax Error - Expected return type in function definition.")
                exit(1)

            # Get function body
            body = parseStatement(par)
            if not body or body.nodeType != "CODE":
                print(f"{tok.file}:{tok.line}:{tok.col}: Syntax Error - Defining functions with no body is currently not supported.")
                exit(1)

            node = ASTNode(tok.line, tok.col, tok.file, "DEFUN", f"{name.val}:{ret.val}")
            node.children = [params, body]
            return node

        return ASTNode(tok.line, tok.col, tok.file, "KEYWORD", tok.val)

    elif tok.tokType == "LPAREN":
        return parseParen(tok, par)


def parseFnCall(par: Parser) -> ASTNode:
    node = parseAtom(par)
    if len(par.toks) and node.nodeType == "KEYWORD" and parseAt(par).tokType == "LPAREN" and parseAt(par).val == "(":
        node.nodeType = "FNCALL"
        node.children = parseAtom(par).children

    return node



def parseExp(par: Parser) -> ASTNode:
    left = parseFnCall(par)

    while len(par.toks) and parseAt(par).val == "**":
        tok = parseConsume(par)
        right = parseFnCall(par)
        temp = ASTNode(tok.line, tok.col, tok.file, "OPER", tok.val)

        temp.children.append(left)
        temp.children.append(right)

        left = temp

    return left


def parseProd(par: Parser) -> ASTNode:
    left = parseExp(par)

    while len(par.toks) and parseAt(par).val in "*/":
        tok = parseConsume(par)
        right = parseExp(par)
        temp = ASTNode(tok.line, tok.col, tok.file, "OPER", tok.val)

        temp.children.append(left)
        temp.children.append(right)

        left = temp

    return left


def parseSum(par: Parser) -> ASTNode:
    left = parseProd(par)

    while len(par.toks) and parseAt(par).val in "+-":
        tok = parseConsume(par)
        right = parseProd(par)
        temp = ASTNode(tok.line, tok.col, tok.file, "OPER", tok.val)

        temp.children.append(left)
        temp.children.append(right)

        left = temp

    return left


def parseAssign(par: Parser) -> ASTNode:
    left = parseSum(par)

    if len(par.toks) and parseAt(par).val == "=":
        parseConsume(par)
        right = parseSum(par)

        if left.nodeType not in ["KEYWORD", "TYPE_IDENT"]:
            print(f"{left.file}:{left.line}:{left.col}: Attempting to assign to an invalid identifier.")
            exit(1)

        nType = "VARDECL"

        if left.nodeType != "TYPE_IDENT":
            nType = "ASSIGN"

        left.nodeType = nType
        left.children.append(right)

    return left



def parseExpression(par: Parser) -> ASTNode:
    node = parseAssign(par)

    if node.nodeType == "KEYWORD" and node.val == "return":
        node.nodeType = "RETURN"
        node.children.append(parseExpression(par))

    return node


# Parse a statement, simply falls through to parseExpression() for now.
def parseStatement(par: Parser) -> ASTNode:
    res = parseExpression(par)

    if res is None:
        print("PARSER ERROR -- INVALID TOKEN")
        exit(1)

    if res.nodeType == "CODE" or res.nodeType == "DEFUN":
        return res

    t = parseConsume(par)
    if t.tokType != "SEMICOLON":
        printASTNode(res, 0)
        print(f"{t.file}:{t.line}:{t.col}: Syntax Error - Expected semicolon at end of statement.")
        exit(1)

    return res


def buildAST(par: Parser) -> ASTNode:
    while len(par.toks) > 0 and parseAt(par).tokType != "EOF":
        node = parseStatement(par)
        if not node:
            continue

        par.rootNode.children.append(node)

    return par.rootNode
