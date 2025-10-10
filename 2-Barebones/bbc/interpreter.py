from bbc import parser


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}


class Interpreter:
    def __init__(self):
        self.funcs = []
        self.state = "RUNNING"
        self.globalScope = Scope()


class RuntimeFunction:
    def __init__(self, name: str, ret: str, params: list, body: parser.ASTNode):
        self.name = name
        self.ret = ret
        self.params = params
        self.body = body


class RuntimeValue:
    def __init__(self, valType: str, val: str):
        self.valType = valType
        self.val = val


def intGetFunctions(inter: Interpreter, ast: parser.ASTNode):
    for child in ast.children:
        if child.nodeType != "DEFUN":
            continue

        [funcName, retType] = child.val.split(":")

        funcParams = []
        for param in child.children[0].children:
            funcParams.append(param.val)

        inter.funcs.append(RuntimeFunction(funcName, retType, funcParams, child.children[1]))


def intRunFunction(inter: Interpreter, name: str, params: list):
    # Find the function to run
    for func in inter.funcs:
        if func.name == name:
            return intRunCodeBlock(inter, func.body, inter.globalScope)


def buildNodeContainer(node) -> parser.ASTNode:
    res = parser.ASTNode(node.line, node.col, node.file, "ROOT", "ROOT")
    res.children = [node]
    return res


def intRunFNCall(inter, ast, scope, node):
    args = []
    for child in node.children:
        args.append(intRunCodeBlock(inter, buildNodeContainer(child), scope))

    if node.val == "print":
        for arg in args:
            if arg is None:
                print(f"{node.file}:{node.line}:{node.col}: Attempting to print an undefined value.")
                exit(1)

            print(arg.val, end=" ")

        print()


def intRunCodeBlock(inter: Interpreter, ast: parser.ASTNode, scope: Scope):
    for node in ast.children:
        if node.nodeType == "FNCALL":
            intRunFNCall(inter, ast, scope, node)

        elif node.nodeType == "STRING":
            return RuntimeValue("STRING", node.val)
