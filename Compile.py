import lark

cpt = 0

op2asm = {"+": "add rax, rbx", "-": "sub rax, rbx"}

def compile(ast):
    asmString = ""
    asmString = asmString + "extern printf, atol ;déclaration des fonctions externes\n"
    asmString = asmString + "global main ; declaration main\n"
    asmString = asmString + "section .bss ; section des buffer\n"
    asmString = asmString + "buffer resb 256 ; buffer utilisé pour les opérations\n"
    asmString = asmString + "section .data ; section des données\n"
    asmString = asmString + "hex_chars: db '0123456789ABCDEF' \n"
    asmString = asmString + "long_format: db '%lld',10, 0 ; format pour les int64_t\n"
    asmString = asmString + "string_format: db '%s',10, 0 ; format pour les string\n"
    asmString = asmString + "argc : dq 0 ; copie de argc\n"
    asmString = asmString + "argv : dq 0 ; copie de argv\n"
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

def variable_declaration(ast) :  # pretty printer liste var
    asmVar = ""
    vars = set()
    if ast.data != "liste_vide":
        for child in ast.children:
            asmVar += f"{child.children[0].value}: dq 0\n"
            vars.add(child.children[0].value)
    return asmVar, vars

def initMainVar(ast): 
    asmVar = ""
    if ast.data != "liste_vide":
        index = 0
        for child in ast.children:
            asmVar += "mov rbx, [argv] ; initVar\n"
            asmVar += f"mov rdi, [rbx + { 8*(index+1)}]\n"
            if child.data == "var_string":
                asmVar += f"mov [{child.children[0].value}], rdi\n" 
            else :
                asmVar += "xor rax, rax\n"
                asmVar += "call atol\n"
                asmVar += f"mov [{child.children[0].value}], rax\n" 
            index += 1
    return asmVar

def compilReturn(ast):
    asm = compilExpression(ast)
    if ast.children[0].data == "var_string" :
        asm += "mov rdi, string_format \n"
    else :
        asm += "mov rsi, rax ; Return \n"
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
    elif ast.data == "com_asgt_string":
        asmVar = compilAsgtString(ast)
    return asmVar

def compilWhile(ast):
    global cpt
    cpt += 1
    return f""" 
            loop{cpt} : {compilExpression(ast.children[0])}  ; while
                cmp rax, 0
                jz fin{cpt}
                {compilCommand(ast.children[1])}
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
    for child in ast.children :
        asm += compilCommand(child)
        print(child)
    return asm

def compilAsgt(ast):
    asm = compilExpression(ast.children[1])
    asm += f"mov [{ast.children[0].value}], rax ; asgt\n"
    return asm

def compilPrintf(ast):
    asm = compilExpression(ast.children[0])
    asm += "mov rsi, rax ; printF\n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm

def compilAsgtString(ast):
    asm = compilExpression(ast.children[1])
    asm += f"mov [{ast.children[0].value}], rsi ; asgt_str\n"
    return asm


def compilVar(ast): 
    if ast.data == "var_string":
        return f"mov rsi, [{ast.children[0].value}] \n"
    if ast.data == "var_int":
        return f"mov rax, [{ast.children[0].value}] \n"

def compilExpression(ast):  
    if ast.data == "exp_variable":
        return compilVar(ast.children[0])
    elif ast.data ==  "exp_nombre":
        return f"mov rax, {ast.children[0].value}\n"
    elif ast.data ==  "exp_string":
        return f"mov rsi, {ast.children[0].value}\n"
    elif ast.data == "exp_binaire":
        return f"""
                {compilExpression(ast.children[2])} ; bin
                push rax
                {compilExpression(ast.children[0])}
                pop rbx
                {op2asm[ast.children[1].value]}
                """
    elif ast.data == "exp_concat" :
        return compilConcat(ast)
    elif ast.data == "exp_len" :
        return compilLen(ast)
    elif ast.data == "exp_char_at" :
        return compilCharAt(ast)
        
def compilConcat(ast):
    global cpt
    cpt += 1
    return f"""
            {compilExpression(ast.children[0])}
            {compilExpression(ast.children[1])}
            mov rdi, rsi 
            lea rax, [buffer]  
            mov rcx, rax  
            ; copie de la première chaine
            copy_first_{cpt}:
                lodsb
                stosb
                test al, al
                jnz copy_first_{cpt}
            dec rcx  
            ; Copie de la seconde chaine
            copy_second_{cpt}:
                lodsb
                stosb
                test al, al
                jnz copy_second_{cpt}
            mov rsi, rcx  
        """

def compilLen(ast):
    print(ast)
    global cpt
    cpt += 1
    return f""" 
            {compilExpression(ast.children[0])}
            mov rdi,rax ; Len
            xor rsi, rsi
            mov rsi, 1
            loop{cpt} : 
                mov rax,rdi
                cmp rax,0
                jz fin{cpt}
                mov rbx, 16
                test rbx, rbx
                div rbx
                inc rsi
                mov rdi,rax
                jmp loop{cpt}
            fin{cpt} : 
            mov rax, rdx
            mov rbx, 2
            div rbx
        """

def compilLen2(ast):
    global cpt
    cpt += 1
    return f"""
            {compilExpression(ast.children[0])} 
            xor rax, rax ; Compteur
            len_loop_{cpt} :
                cmp byte [rsi + rax], 0  
                je len_end_{cpt}  
                inc rax 
                jmp len_loop_{cpt} 
            len_end_{cpt} :
        """


# Résultat sous forme d'un entier correpondant à la lettre
def compilCharAt(ast):
    return f'''
    {compilExpression(ast.children[0])}
    {compilExpression(ast.children[1])}
    mov rcx, rax  
    mov al, [rsi + rcx] 
    mov rax, al
    '''

#Permet de convertir en hexadécimal les caractères écrit en décimal
def convertDecToHexdec():
    return f'''
        lea rdi, [buffer + 16]
        mov byte [rdi],0
        dec rdi
        convert :
            mov rbx, 16
            xor rdx,rdx
            div rbx
            mov bl,dl
            movzx bl, byte[hex_chars + rbx]
            mov [rdi], bl
            dec rdi
            test rax,rax
            jnz convert
        end :
            lea rsi,[rdi + 1]
'''