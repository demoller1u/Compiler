import lark

grammaire = """
%import common.SIGNED_NUMBER  #bibliothèque lark.
%import common.WS
%ignore WS
// %ignore /[ ]/   #ignore les blancs, mais l'arbre ne contient pas l'information de leur existence. problématique du pretty printer. 

VARIABLE : /[a-zA-Z_][a-zA-Z 0-9]*/
FUNCTOKEN : /[a-zA-Z_][a-zA-Z 0-9]*/
STRING : "/[a-zA-Z 0-9]*/"
NOMBRE : SIGNED_NUMBER
// NOMBRE : /[1-9][0-9]*/
OPBINAIRE: /[+*\/&><]/|">="|"-"|">>"  //lark essaie de faire les tokens les plus long possible

expression: VARIABLE -> exp_variable
| NOMBRE         -> exp_nombre
| expression OPBINAIRE expression -> exp_binaire
| FUNCTOKEN "(" arguments ")" -> exp_appel //appel de fonction
| STRING -> exp_string

commande : VARIABLE "=" expression ";"-> com_asgt //les exp entre "" ne sont pas reconnues dans l'arbre syntaxique
| "printf" "(" expression ")" ";" -> com_printf
| commande+ -> com_sequence
| "while" "(" expression ")" "{" commande "}" -> com_while
| "if" "(" expression ")" "{" commande "}" "else" "{" commande "}" -> com_if
| "c" VARIABLE "=" STRING ";" -> com_asgt_string
| FUNCTOKEN "(" arguments ");" -> com_appel

liste_var :                -> liste_vide
| VARIABLE ("," VARIABLE)* -> liste_normale

//Function
arguments :                -> args_vide  # Pas d'arguments.
    | expression ("," expression)* -> args_normaux  # Arguments de fonction.

fonction : FUNCTOKEN "(" arguments ")" "{" commande* "return" "(" expression ")" ";" "}" -> func

programme : fonction* -> prog
"""


# main : symbole de départ.
# VARIABLE : une suite de lettres et de chiffres.
# main : VARIABLE : la règle de production de main est VARIABLE.
# expression : VARIABLE | NOMBRE : la règle de production de expression est VARIABLE ou NOMBRE
#               ou expression '+' expression qui définit une addition.

def pretty_printer_liste_var(t):
    if t.data == "liste_vide":
        return ""
    return ", ".join([u.value for u in t.children])


def pretty_printer_commande(t):
    if (t.data == "com_asgt"):
        return f"{t.children[0].value} = {pretty_printer_expression(t.children[1])} ;"
    if (t.data == "com_printf"):
        return f"printf ({pretty_printer_expression(t.children[0])}) ;"
    if (t.data == "com_sequence"):
        return "while (%s){ %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]))
    if (t.data == "com_if"):
        return "if (%s){ %s} else { %s}" % (
            pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]),
            pretty_printer_commande(t.children[2]))
    if (t.data == "com_sequence"):
        return "\n".join([pretty_printer_commande(u) for u in t.children])


def pretty_printer_expression(t):
    if t.data in ("exp_variable", "exp_nombre"):
        return t.children[0].value
    return f"{pretty_printer_expression(t.children[0])} {t.children[1].value} {pretty_printer_expression(t.children[2])}"


def pretty_printer_commande(t):
    if t.data == "com_asgt":
        return f"{t.children[0].value} = {pretty_printer_expression(t.children[1])} ;"
    if t.data == "com_printf":
        return f"printf ({pretty_printer_expression(t.children[0])}) ;"
    if t.data == "com_while":
        return "while (%s){ %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]))
    if t.data == "com_if":
        return "if (%s){ %s} else { %s}" % (
            pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]),
            pretty_printer_commande(t.children[2]))
    if t.data == "com_sequence":
        return "\n".join([pretty_printer_commande(u) for u in t.children])


def pretty_print(t):
    return "main (%s) { %s return (%s); }" % (pretty_printer_liste_var(t.children[0]),
                                              pretty_printer_commande(t.children[1]),
                                              pretty_printer_expression(t.children[2]))


def parse(source_code):
    parser = lark.Lark(grammaire, start='programme')
    return parser.parse(source_code)


if __name__ == "__main__":
    parser = lark.Lark(grammaire, start='programme')
    with open("ideal.c", 'r') as file:
        tree = parser.parse(file.read())
    # print(pretty_print(tree))
    print(tree)
    print(tree.data)
