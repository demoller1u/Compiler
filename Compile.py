import lark

cpt = 0

op2asm = {"+": "add rax, rbx", "-": "sub rax, rbx"}


def compile_ast(ast):
    try:
        asmString = ""
        asmString = asmString + "extern printf, atol ;déclaration des fonctions externes\n"
        asmString = asmString + "section .data ; section des données\n"
        asmString = asmString + "long_format: db '%lld',10, 0 ; format pour les int64_t\n"
        asmString = asmString + "argc : dq 0 ; copie de argc\n"
        asmString = asmString + "argv : dq 0 ; copie de argv\n"
        asmFunc, func = function_declaration(ast.children[0])
        asmVar, vars = variable_declaration(ast.children[0])
        asmString = asmString + asmVar
        asmString = asmString + "section .text ; instructions\n"
        asmString += "main :"
        asmString += "push rbp; Set up the stack. Save rbp\n"
        asmString += "mov [argc], rdi\n"
        asmString += "mov [argv], rsi\n"
        asmString += initMainVar(ast.children[0])
        asmString += compilCommand(ast.children[1])
        asmString += compilReturn(ast.children[2])
        asmString += "pop rbp\n"
        asmString += "xor rax, rax\n"
        asmString += "ret\n"
        return asmString
    except ValueError as e:
        print("Error was raised:" + str(e))


def function_declaration(ast):
    asmFunc = ""
    asmVar = ""
    vars = set()
    func = set()
    contains_main = False
    for child in ast.children:
        if child.data == "func":
            if child.children[0].value in func:
                raise SyntaxError(f"Function {child.children[0].value} already defined")
            if child.children[0].value == "main":
                contains_main = True
            # Function declaration
            func.add(child.children[0].value)
            # Declare the variables
            curVarAsm, curVarSet = variable_declaration(child.children[1])

            asmFunc += f"{child.children[0].value}:\n"
            asmFunc += "push rbp\n"
            asmFunc += "mov rbp, rsp\n"
            asmFunc += compilCommand(child.children[1])
            asmFunc += compilReturn(child.children[2])
            asmFunc += "pop rbp\n"
            asmFunc += "ret\n"
    if not contains_main:
        raise SyntaxError("No main function found. Your program needs a main function")


def variable_declaration(ast):
    asmVar = ""
    vars = set()
    if ast.data != "liste_vide":
        for child in ast.children:
            asmVar += f"{child.value}: dq 0\n"
            vars.add(child.value)
    return asmVar, vars


def initMainVar(ast):
    asmVar = ""
    if ast.data != "liste_vide":
        index = 0
        for child in ast.children:
            asmVar += "mov rbx, [argv]\n"
            asmVar += f"mov rdi, [rbx + {8 * (index + 1)}]\n"
            asmVar += "xor rax, rax\n"
            asmVar += "call atol\n"
            asmVar += f"mov [{child.value.strip()}], rax\n"
            index += 1
    return asmVar


def compilReturn(ast):
    asm = compilExpression(ast)
    asm += "mov rsi, rax \n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm


def compilCommand(ast):
    asmVar = ""
    if ast.data == "com_while":
        asmVar = compilWhile(ast)
    elif ast.data == "com_if":
        asmVar = compilIf(ast)
    elif ast.data == "com_sequence":
        asmVar = compilSequence(ast)
    elif ast.data == "com_asgt":
        asmVar = compilAsgt(ast)
    elif ast.data == "com_printf":
        asmVar = compilPrintf(ast)
    return asmVar


def compilWhile(ast):
    global cpt
    cpt += 1
    return f""" 
            loop{cpt} :
                {compilExpression(ast.children[0]).strip()}
                cmp rax, 0
                jz fin{cpt}
                {compilCommand(ast.children[1]).strip()}
                jmp loop{cpt}
            fin{cpt} :
        """


def compilIf(ast):
    global cpt
    cpt += 1
    return f""" 
            {compilExpression(ast.children[0])}
            cmp rax, 0
            jz fin{cpt}
            {compilCommand(ast.children[1])}
            fin{cpt} :
        """


def compilSequence(ast):
    asm = ""
    for child in ast.children:
        asm += compilCommand(child)
    return asm


def compilAsgt(ast):
    asm = compilExpression(ast.children[1])
    asm += f"mov [{ast.children[0].value.strip()}], rax \n"
    return asm


def compilPrintf(ast):
    asm = compilExpression(ast.children[0]).strip()
    asm += "mov rsi, rax \n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm


def compilExpression(ast):
    if ast.data == "exp_variable":
        return f"mov rax, [{ast.children[0].value}]\n"
    elif ast.data == "exp_nombre":
        return f"mov rax, {ast.children[0].value.strip()}\n"
    elif ast.data == "exp_binaire":
        return f"""{compilExpression(ast.children[2])}
                push rax
                {compilExpression(ast.children[0]).strip()}
                pop rbx
                {op2asm[ast.children[1].value]}
                """
    return ""
