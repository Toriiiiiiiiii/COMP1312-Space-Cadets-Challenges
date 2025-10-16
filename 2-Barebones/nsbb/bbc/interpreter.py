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


def getTypenameFromKeyword(key):
    match key:
        case "int":
            return "INTEGER"
        case "string":
            return "STRING"
        case "void":
            return "VOID"


def intGetFunctions(inter: Interpreter, ast: parser.ASTNode):
    for child in ast.children:
        if child.nodeType != "DEFUN":
            continue

        [funcName, retType] = child.val.split(":")
        retType = getTypenameFromKeyword(retType)

        funcParams = []
        for param in child.children[0].children:
            funcParams.append(param.val)

        inter.funcs.append(RuntimeFunction(funcName, retType, funcParams, child.children[1]))


def getVariable(name: str, scope: Scope):
    for var in scope.vars:
        if var == name:
            return scope.vars[name]

    if scope.parent:
        return getVariable(name, scope.parent)

    return None


def setVariable(name: str, val: RuntimeValue, scope: Scope):
    res = None
    if scope.parent:
        res = setVariable(name, val, scope.parent)

    if res is not None:
        return val

    for var in scope.vars:
        if var == name:
            scope.vars[name] = val
            return val

    scope.vars[name] = val
    return val


def intRunFunction(inter: Interpreter, name: str, params: list):
    # Find the function to run
    for func in inter.funcs:
        if func.name == name:
            scope = Scope(inter.globalScope)

            if len(params) != len(func.params):
                # TODO: better error message
                print("Invalid function arguments.")
                exit(1)

            for i, paramName in enumerate(func.params):
                [t, n] = paramName.split(":")
                if getTypenameFromKeyword(t) != params[i].valType:
                    # TODO: better error message
                    print("Invalid function arguments.")
                    exit(1)

                scope.vars[n] = params[i]

            res, fn = intRunCodeBlock(inter, func.body, scope, True), func
            if res.valType != func.ret:
                # TODO: better error message
                print("Invalid function return.")
                exit(1)

            return res, fn

    return None

def buildNodeContainer(node) -> parser.ASTNode:
    res = parser.ASTNode(node.line, node.col, node.file, "ROOT", "ROOT")
    res.children = [node]
    return res


def intRunFNCall(inter, scope, node):
    args = []
    for child in node.children:
        args.append(intRunNode(inter, child, scope))

    if node.val == "print":
        for arg in args:
            if arg is None:
                print(f"{node.file}:{node.line}:{node.col}: Attempting to print an undefined value.")
                exit(1)

            print(arg.val, end=" ")

        print()
        return RuntimeValue("VOID", "VOID")

    else:
        res, func = intRunFunction(inter, node.val, args)
        if res is None:
            print(f"{node.file}:{node.line}:{node.col}: Undefined Function Reference '{node.val}'.")
            exit(1)

        if res.valType != func.ret:
            # TODO: Fix error message
            print("Returning wrong type from function.")
            exit(1)

        return res


def intRunOper(inter: Interpreter, node: parser.ASTNode, scope: Scope):
    op = node.val
    left = intRunNode(inter, node.children[0], scope)
    right = intRunNode(inter, node.children[1], scope)

    if right.valType != left.valType:
        print(f"{node.file}:{node.line}:{node.col}: Attempting to perform '{op}' on values of different type.")
        exit(1)

    if right.valType != "INTEGER":
        print(f"{node.file}:{node.line}:{node.col}: Operation '{op}' is undefined for type {right.valType}")
        exit(1)

    match op:
        case '+':
            return RuntimeValue("INTEGER", int(left.val) + int(right.val))
        case '-':
            return RuntimeValue("INTEGER", int(left.val) - int(right.val))
        case '*':
            return RuntimeValue("INTEGER", int(left.val) * int(right.val))
        case '/':
            return RuntimeValue("INTEGER", int(int(left.val) // int(right.val)))


def intRunNode(inter: Interpreter, node: parser.ASTNode, scope: Scope):
    if node.nodeType == "FNCALL":
        return intRunFNCall(inter, scope, node)

    elif node.nodeType == "STRING":
        return RuntimeValue("STRING", node.val)
    elif node.nodeType == "INT":
        return RuntimeValue("INTEGER", int(node.val))

    elif node.nodeType == "VARDECL":
        [varType, varName] = node.val.split(":")
        typename = getTypenameFromKeyword(varType)

        if getVariable(varName, scope) is not None:
            print(f"{node.file}:{node.line}:{node.col}: Attempting to declare an existing variable in scope.")
            exit(1)

        val = intRunNode(inter, node.children[0], scope)
        if val.valType != typename:
            print(f"{node.file}:{node.line}:{node.col}: Attempting to assign value to variable of different type.")
            exit(1)

        setVariable(varName, val, scope)

    elif node.nodeType == "KEYWORD":
        val = getVariable(node.val, scope)
        if val is not None:
            return val

        print(f"{node.file}:{node.line}:{node.col}: Undefined reference to variable '{node.val}'")
        exit(1)

    elif node.nodeType == "OPER":
        return intRunOper(inter, node, scope)


def intRunCodeBlock(inter: Interpreter, ast: parser.ASTNode, scope: Scope, isFunction=False):
    for node in ast.children:
        if node.nodeType == "RETURN":
            if not isFunction:
                # TODO: Fix error message
                print("Attempt to return from non-function.") 
                exit(1)

            retVal = intRunNode(inter, node.children[0], scope)
            return retVal

        intRunNode(inter, node, scope)

    return RuntimeValue("VOID", "VOID")
