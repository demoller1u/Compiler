import lark

grammaire = """
%import common.SIGNED_NUMBER  
%import common.WS
%ignore WS
// %ignore /[ ]/   #ignore les blancs, mais l'arbre ne contient pas l'information de leur existence. problématique du pretty printer. 

INT_VAR : /[a-rt-zA-RT-Z_][a-zA-Z 0-9]*/
STRING_VAR : /s[a-zA-Z 0-9]*/
NOMBRE : SIGNED_NUMBER
OPBINAIRE: /[+*\/&><]/|">="|"-"|">>"  //lark essaie de faire les tokens les plus long possible
STRING: /"[a-zA-Z]*"/

variable: INT_VAR -> var_int
| STRING_VAR -> var_string

expression: variable -> exp_variable
| NOMBRE         -> exp_nombre
| expression OPBINAIRE expression -> exp_binaire
| "concat" "("expression "," expression ")" -> exp_concat
| STRING -> exp_string
| "len" "(" expression ")" -> exp_len
| "charAt" "(" expression "," expression")" -> exp_char_at

commande : INT_VAR "=" expression ";"-> com_asgt //les exp entre "" ne sont pas reconnues dans l'arbre syntaxique
| "printf" "(" expression ")" ";" -> com_printf
| commande+ -> com_sequence
| "while" "(" expression ")" "{" commande "}" -> com_while
| "if" "(" expression ")" "{" commande "}" "else" "{" commande "}" -> com_if
| STRING_VAR "=" expression ";"  -> com_asgt_string // typage spécial choisi pour écrire les chaînes de caractères



liste_var :                -> liste_vide
| variable ("," variable)* -> liste_normale
programme : "main" "(" liste_var ")" "{" commande "return" "(" expression ")" ";" "}" -> prog_main // ressemble à une déclaration de fonction
"""

parser = lark.Lark(grammaire, start = "programme")

t = parser.parse("""main(x,y){
                 while(x) {
                    y = y + 1;
                    printf(y);
                 }
                 return (y);
                }
                 """)
u = parser.parse("""main(s1,s2){
                s2 = "efgh" ;
                x = charAt(s2,3);
                y = len(s2);
                return(s2);
                }
                 """)

def pretty_printer_liste_var(t):
    if t.data == "liste_vide" :
        return ""
    return ", ".join([pretty_printer_var(u) for u in t.children])
    
def pretty_printer_var(t):
    return t.children[0].value

def pretty_printer_expression(t):
    if t.data in ("exp_nombre", "exp_string"):
        return t.children[0].value
    if t.data == "exp_variable":
        return pretty_printer_var(t.children[0])
    if t.data == "exp_concat" :
        return f"concat({pretty_printer_expression(t.children[0])}, {pretty_printer_expression(t.children[1])})"
    if t.data =="exp_len":
        return f"len({pretty_printer_expression(t.children[0])})"
    if t.data =="exp_char_at":
        return f"charAt({pretty_printer_expression(t.children[0])},{pretty_printer_expression(t.children[1])})"
    return f"{pretty_printer_expression(t.children[0])} {t.children[1].value} {pretty_printer_expression(t.children[2])}"

def pretty_printer_commande(t):
    if t.data == "com_asgt":
        return f"{t.children[0].value} = {pretty_printer_expression(t.children[1])} ;"
    if t.data == "com_printf":
        return f"printf ({pretty_printer_expression(t.children[0])}) ;"
    if t.data == "com_while":
        return "while (%s){ %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]))
    if t.data == "com_if":
        return "if (%s){ %s} else { %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]), pretty_printer_commande(t.children[2]))
    if t.data == "com_sequence":
        return "\n".join([pretty_printer_commande(u) for u in t.children])
    if t.data =="com_asgt_string":
        return f" {t.children[0].value} = {pretty_printer_expression(t.children[1])} ;"


def pretty_print(t):
    return  "main (%s) { %s return (%s); }" % (pretty_printer_liste_var(t.children[0]), 
                                               pretty_printer_commande(t.children[1]),
                                                pretty_printer_expression( t.children[2]))

print(pretty_print(u))
print(u)