import lark

cpt = 0

op2asm = {"+": "add rax, rbx", "-": "sub rax, rbx"}


def compile_ast(ast):
    global functions_dict
    functions_dict = build_fonct_dict(ast)
    try:
        asmString = ""
        asmString = asmString + "extern printf, atol ;déclaration des fonctions externes\n"
        asmString = asmString + "section .data ; section des données\n"
        asmString = asmString + "long_format: db '%lld',10, 0 ; format pour les int64_t\n"
        asmString = asmString + "string_format: db '%s',10, 0 ; format pour les int64_t\n"
        asmString = asmString + "error_msg_args : db 'Error: wrong number of arguments',10, 0\n"
        asmString = asmString + "argc : dd 0 ; copie de argc\n"
        asmString = asmString + "argv : dd 0 ; copie de argv\n"
        asmString = asmString + "section .text ; instructions\n"
        asmString = asmString + "\n"
        asmString = asmString + "global exit_error\n"
        for key, value in functions_dict.items():
            asmString += f"global {key}\n"
        # Set up functions
        asmString += build_function_body(functions_dict)
        # Set up exit error
        asmString += initExitWithError()
        return asmString
    except ValueError as e:
        print("Error was raised:" + str(e))


def build_fonct_dict(ast):
    # Each child is a function
    functions_dict = {}
    for function in ast.children:
        function_data = function.children
        function_name = function_data[0]
        function_args_tree = function_data[1]
        function_args_label = []
        # Store args
        for arg in function_args_tree.children:
            label = arg.children[0]
            function_args_label.append(label)
        # Use find var to find the variable names recursively
        # Store vars
        function_child = function_data[2:]
        function_vars_label = set()
        for child in function_child:
            function_vars_label = function_vars_label.union(find_var(child))
        function_vars_label = list(function_vars_label.difference(set(function_args_label)))
        function_return = function_data[-1]
        if function_name.value not in functions_dict:
            functions_dict[function_name.value] = {}
            functions_dict[function_name.value]["args"] = function_args_label
            functions_dict[function_name.value]["vars"] = function_vars_label
            functions_dict[function_name.value]["tree"] = function
            functions_dict[function_name.value]["return"] = function_return
        else:
            raise SyntaxError("Function name must be unique")
    return functions_dict


def find_var(ast):
    vars = set()
    if type(ast) == lark.Tree and ast.data != "liste_vide":
        for child in ast.children:
            if type(child) == lark.Token and child.type == "VARIABLE":
                vars.add(child.value.strip())
            elif type(child) != lark.Token and child.data == "exp_variable":
                vars.add(child.children[0].value.strip())
            else:
                vars = vars.union(find_var(child))
    return vars


def store_function(ast):
    function_dict = {}
    for child in ast.children:
        if child.data == "func":
            if child.children[0].value not in function_dict:
                function_dict[child.children[0].value] = {}
            function_dict[child.children[0].value]["tree"] = child
    return function_dict


def initStart(function_dict):
    # Get the main args from the function_dict
    varNum = 0
    for key, value in function_dict.items():
        if key == "main":
            varNum = len(value["tree"].children[1].children) + 1
    asmVar = "push rbp\n"
    asmVar += "mov rbp, rsp\n"
    # Push the arguments to the stack
    asmVar += "push rdi\n"  # argc
    asmVar += "push rsi\n"  # argv
    # test if the number of arguments is correct
    asmVar += f"cmp rdi, {varNum}\n"
    asmVar += "jne exit_error\n"
    asmVar += "mov rbx, rsi\n"
    # Get the arguments of main and push them in the stack
    mainArgs = function_dict["main"]["args"]
    for i in range(len(mainArgs)):
        asmVar += f"mov rdi, [rbx + {8 * (i+1)}]\n"
        asmVar += "xor rax, rax\n"
        asmVar += "call atol\n"
        asmVar += f"push rax\n"
    # Call the main function
    return asmVar


def initExitWithError():
    asmVar = "\nexit_error:\n"
    asmVar += "mov rsi, error_msg_args\n"
    asmVar += "mov rdi, string_format\n"
    asmVar += "xor rax, rax\n"
    asmVar += "call printf\n"
    asmVar += "mov rax, 60\n"
    asmVar += "xor rdi, rdi\n"
    asmVar += "syscall\n"
    return asmVar


def build_function_body(function_dict):
    asm_var = ""
    for key, value in function_dict.items():
        func_name = key
        asm_var += f"\n{key}:\n"
        if func_name == "main":
            asm_var += initStart(function_dict)
        asm_var += "push rbp\n"
        asm_var += "mov rbp, rsp\n"
        # Allocate space for the variables
        var_number = len(value["vars"])
        if var_number > 0:
            asm_var += f"sub rsp, {8 * var_number}\n"
        # Compile body
        for child in value["tree"].children[1:]:
            if child.data == "com_sequence":
                for command in child.children:
                    asm_var += compilCommand(command, func_name)
            elif child.data == "args_normaux":
                pass
            else:
                asm_var += compilCommand(child, func_name)

        # We must free the space allocated for the variables
        if func_name == "main":
            if var_number > 0:
                asm_var += f"add rsp, {8 * var_number}\n"
            asm_var += "pop rbp\n"
            asm_var += "mov rax, 60\n"
            asm_var += "xor rdi, rdi\n"
            asm_var += "syscall\n"
        else:
            if var_number > 0:
                asm_var += f"add rsp, {8 * var_number}\n"
            #Move the result into rax
            #If the return is a variable
            if value["return"].data == "exp_variable":
                var_name = value["return"].children[0].value.strip()
                if var_name in value["args"]:
                    # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of args
                    arg_index = value["args"].index(var_name)
                    if func_name == "main":
                        arg_index -= 1
                    asm_var += f"mov rax, [rbp + {16 + arg_index * 8}]\n"
                elif var_name in value["vars"]:
                    # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of vars
                    arg_index = value["vars"].index(var_name)
                    asm_var += f"mov rax, [rbp - {8 + arg_index * 8}]\n"
            #If the return is a number
            elif value["return"].data == "exp_nombre":
                asm_var += f"mov rax, {value['return'].children[0].value.strip()}\n"
            asm_var += "pop rbp\n"
            asm_var += "ret\n"
    return asm_var


def variable_declaration(ast):
    asm_var = ""
    vars = set()
    if ast.data != "liste_vide":
        for child in ast.children:
            asm_var += f"{child.value}: dq 0\n"
            vars.add(child.value)
    return asm_var, vars


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


def compilCommandCall(ast, func_name):
    asm_call = ""
    # We get the arguments, and we must differentiate between variables and numbers
    for child in ast.children[1:]:
        if child.data == "args_normaux":
            # We must push the arguments in the reverse order
            for arg in reversed(child.children):
                if arg.data == "exp_variable":
                    # We know that the argument is a variable, we must push the value of the variable
                    # -> If the variable is a local variable, then it is in the stack after rbp ex: [rbp - 8]
                    # -> If the variable is an argument, then it is in the stack before rbp + 16 ex: [rbp + 16]
                    var_name = arg.children[0].value.strip()
                    if var_name in functions_dict[func_name]["args"]:
                        # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of
                        # args
                        arg_index = functions_dict[func_name]["args"].index(var_name)
                        if func_name == "main":
                            arg_index -= 1
                        asm_call += f"mov rax, [rbp + {16 + arg_index * 8}]\n"
                        asm_call += f"push rax\n"
                        asm_call += "xor rax, rax\n"
                    else:
                        # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of
                        # vars
                        arg_index = functions_dict[func_name]["vars"].index(var_name)
                        asm_call += f"mov rax, [rbp - {8 + arg_index * 8}]\n"
                        asm_call += f"push rax\n"
                        asm_call += "xor rax, rax\n"
                elif arg.data == "exp_nombre":
                    # We know it's a number, we must push the number
                    asm_call += f"push {arg.children[0].value.strip()}\n"
    asm_call += f"call {ast.children[0].value}\n"
    return asm_call



def compilCommand(ast, func_name):
    asmVar = ""
    if ast.data == "com_while":
        asmVar = compilWhile(ast, func_name)
    elif ast.data == "com_if":
        asmVar = compilIf(ast, func_name)
    elif ast.data == "com_sequence":
        asmVar = compilSequence(ast, func_name)
    elif ast.data == "com_asgt":
        asmVar = compilAsgt(ast, func_name)
    elif ast.data == "com_printf":
        asmVar = compilPrintf(ast, func_name)
    elif ast.data == "com_appel":
        asmVar = compilCommandCall(ast, func_name)
    return asmVar


def compilWhile(ast, func_name):
    global cpt
    cpt += 1
    asm = (f"loop{cpt} :\n" +
           f"{compilExpression(ast.children[0], func_name).strip()}\n" +
           f"cmp rax, 0\n" +
           f"jz fin{cpt}\n" +
           f"{compilCommand(ast.children[1], func_name).strip()}\n" +
           f"jmp loop{cpt}\n" +
           f"fin{cpt} :")
    return asm


def compilIf(ast, func_name):
    asm = ""
    global cpt
    cpt += 1
    asm = (f"{compilExpression(ast.children[0], func_name).strip()}\n" +
           f"cmp rax, 0\n" +
           f"jz fin{cpt}\n" +
           f"{compilCommand(ast.children[1], func_name).strip()}\n" +
           f"fin{cpt} :")
    return asm


def compilSequence(ast, func_name):
    asm = ""
    for child in ast.children:
        asm += compilCommand(child, func_name)
    return asm


def compilCall(ast, func_name):
    asm_asgt = ""
    # We get the arguments, and we must differentiate between variables and numbers
    for child in ast.children[1].children[1:]:
        if child.data == "args_normaux":
            # We must push the arguments in the reverse order
            for arg in reversed(child.children):
                if arg.data == "exp_variable":
                    # We know that the argument is a variable, we must push the value of the variable
                    # -> If the variable is a local variable, then it is in the stack after rbp ex: [rbp - 8]
                    # -> If the variable is an argument, then it is in the stack before rbp + 16 ex: [rbp + 16]
                    var_name = arg.children[0].value.strip()
                    if var_name in functions_dict[func_name]["args"]:
                        # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of
                        # args
                        arg_index = functions_dict[func_name]["args"].index(var_name)
                        if func_name == "main":
                            arg_index -= 1
                        asm_asgt += f"mov rax, [rbp + {16 + arg_index * 8}]\n"
                        asm_asgt += f"push rax\n"
                        asm_asgt += "xor rax, rax\n"
                    else:
                        # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of
                        # vars
                        arg_index = functions_dict[func_name]["vars"].index(var_name)
                        asm_asgt += f"mov rax, [rbp - {8 + arg_index * 8}]\n"
                        asm_asgt += f"push rax\n"
                        asm_asgt += "xor rax, rax\n"
                elif arg.data == "exp_nombre":
                    # We know it's a number, we must push the number
                    asm_asgt += f"push {arg.children[0].value.strip()}\n"
    asm_asgt += f"call {ast.children[1].children[0].value}\n"
    return asm_asgt


def compilAsgt(ast, func_name):
    # If the asignement is a function call, we need to push the arguments and call the function
    if ast.children[1].data == "exp_appel":
        asm_asgt =  compilCall(ast, func_name)
        # If the asignement is a variable, we need to move the value of the expression to the variable
        # We must find the variable in the args or in the vars
        var_name = ast.children[0].value.strip()
        if var_name in functions_dict[func_name]["args"]:
            # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of args
            arg_index = functions_dict[func_name]["args"].index(var_name)
            if func_name == "main":
                arg_index -= 1
            asm_asgt += f"mov [rbp + {16 + arg_index * 8}], rax\n"
            return asm_asgt
        elif var_name in functions_dict[func_name]["vars"]:
            # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of vars
            arg_index = functions_dict[func_name]["vars"].index(var_name)
            asm_asgt += f"mov [rbp - {8 + arg_index * 8}], rax\n"
            return asm_asgt
    else:
        # If the asignement is a variable, we need to move the value of the expression to the variable
        # We must find the variable in the args or in the vars
        var_name = ast.children[0].value.strip()
        if var_name in functions_dict[func_name]["args"]:
            # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of args
            arg_index = functions_dict[func_name]["args"].index(var_name)
            asm_asgt = compilExpression(ast.children[1], func_name)
            if func_name == "main":
                arg_index -= 1
            asm_asgt += f"mov [rbp + {16 + arg_index * 8}], rax\n"
            return asm_asgt
        elif var_name in functions_dict[func_name]["vars"]:
            # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of vars
            arg_index = functions_dict[func_name]["vars"].index(var_name)
            asm_asgt = compilExpression(ast.children[1], func_name)
            asm_asgt += f"mov [rbp - {8 + arg_index * 8}], rax\n"
            return asm_asgt


def compilPrintf(ast, func_name):
    asm = compilExpression(ast.children[0], func_name).strip() + "\n"
    asm += "mov rsi, rax \n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm


def compilExpression(ast, func_name):
    if ast.data == "exp_variable":
        # We must find the variable in the args or in the vars
        var_name = ast.children[0].value.strip()
        if var_name in functions_dict[func_name]["args"]:
            # We assume that the adress of the arg is rbp + 16 + i*8, i being the position in the list of args
            arg_index = functions_dict[func_name]["args"].index(var_name)
            if func_name == "main":
                arg_index -= 1
            return f"mov rax, [rbp + {16 + arg_index * 8}]\n"
        elif var_name in functions_dict[func_name]["vars"]:
            # We assume that the adress of the arg is rbp - 8 - i*8, i being the position in the list of vars
            arg_index = functions_dict[func_name]["vars"].index(var_name)
            return f"mov rax, [rbp - {8 + arg_index * 8}]\n"
    elif ast.data == "exp_nombre":
        return f"mov rax, {ast.children[0].value.strip()}\n"
    elif ast.data == "exp_binaire":
        asm = ("" + f"{compilExpression(ast.children[2], func_name).strip()}\n"
               + f"push rax\n"
               + f"{compilExpression(ast.children[0], func_name).strip()}\n"
               + f"pop rbx\n" + f"{op2asm[ast.children[1].value]}\n")
        return asm
    return ""
