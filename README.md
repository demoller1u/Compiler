# Compiler

Le projet compilateur est un projet utilisant des notions drassembleur et de python. 
Ce git résume comment compiler le projet et comment il fonctionne.
Dans ce projet chaque fonctionnalité a été traité par une personne différente, Victor Matrat traitant les fonctions et Camille de Mollerat du Jeu traitant les chaînes de caractères. 


## Table des Matières

- [Branches](#branches)
- [Fonctions](#fonctions)
- [String](#string)

-------------------------------------------------------------------------------------------------------------------------------------

## Branches

Le projet est composé de 3 branches: 
- Une branche main qui regroupe le code de base du fonctionnement du compilateur, ainsi qu'un exemple de code nanoc fonctionnel.
- une branche fonction qui regroupe l'ensemble des codes permettant de compiler des fonctions. POur se faire, il suffit de faire la commande:
```bash
python main.py string.c hello.asm
```
puis pour lire le code assembleur, il faut faire :
```bash
Nasm –f elf64 hello.asm 
Gcc -no-pie hello.o
./a.out // suivi des entrées
```
- une branche function_string qui regroupe l'ensemble des codes permettant de compiler des chaînes de caractères. POur se faire, il suffit de faire la commande:
```bash
python main.py string.c string.asm
```
puis pour lire le code assembleur, il faut faire :
```bash
Nasm –f elf64 string.asm 
Gcc -no-pie string.o
./a.out // suivi des entrées
```


## Fonctions
La branche fonction regroupe un parser et un compilateur permettant certaines opérations avec des fonctions, de manière similaire à celle du C. Pour compiler, il est nécessaire que le programme ait une fonction main avec au moins 1 variable. Une sécurité a été ajoutée dans le cas de tentative d'éxecution de code avec un mauvais nombre d'argument, c'est à dire un nombre différent de celui qui est précisé dans la fonction main (et qui doit toujours être supérieur ou égal à 1).
### Exemples de codes
#### Cas avec un mauvais nombre d'arguments:
```c
main(A) {
  /////
}
```
Résultat
```
>./program.out 1 1 1
Error: wrong number of arguments
```
#### Exemple 1 -> Appel de fonction
```c
main(A) {
    test(A);
    return(0);
}

test(X) {
    printf(X);
    return(X);
}
```
Résultat:
```bash
>./program.out 1
1
```

#### Exemple 2 -> Appel d'une fonction avec argument;
```c
main(A) {
    X = test(A);
    printf(X);
    return(0);
}

test(X) {
    return(X);
}
```
Résultat:
```bash
>./program.out 1
1
```
#### Exemple 3 -> Appel d'une fonction au sein d'une fonction
```c
main(A) {
    printf(1);
    test();
    printf(5);
    return(0);
}

test() {
    printf(2);
    secondtest();
    printf(4);
    return(0);
}

secondtest() {
   printf(3);
   return(0);
}
```
Résultat:
```bash
>./program.out 1
1
2
3
4
5
```
#### Exemple 4 -> Utilisation d'une variable locale
```c
main(A) {
    B = test(A);
    A = A + B;
    printf(A);
    return(0);
}

test(X) {
    B = 1;
    X = X + B;
    return(X);
}
```
Résultat:
```bash
>./program.out 1
3
```
#### Exemple 5 -> Utilisation d'une fonction dans un calcul avec opérateur binaire
```c
main(A) {
    B = A + test();
    printf(B);
    B = test() + 2;
    printf(B);
    return(0);
}

test() {
    B = 1;
    return(B);
}
```
Résultat:
```bash
>./program.out 1
2
3
```
#### Exemple 6 -> Boucle avec appel de fonction
```c
main(A) {
    while(A){
        A = test(A);
        printf(A);
    }
    return(0);
}

test(X) {
    X = X - 1;
    return(X);
}
```
Résultat:
```bash
>./program.out 3
2
1
0
```
#### Exemple 7 -> Utilisation du résultat d'un appel de fonction dans un print
```c
main(A) {
    printf(test() + A);
    return(0);
}
test() {
    return(55);
}
```
Résultat:
```bash
>./program.out 10
65
```
### Principe de compilation
La grammaire fournie par le cours a été modifiée pour ajouter:
- Un nom de fonction, qui est un FUNCTOKEN:
  ```
  FUNCTOKEN : /[a-zA-Z_][a-zA-Z 0-9]*/
  ```
- Une liste d'arguments:
  ```
  arguments :                -> args_vide  # Pas d'arguments.
    | expression ("," expression)* -> args_normaux  # Arguments de fonction.
  ```
- Un objet fonction, définit comme suit:

  ```
  fonction : FUNCTOKEN "(" arguments ")" "{" commande* "return" "(" expression ")" ";" "}" -> func
  ```
- Une commande com_appel:
  ```
  FUNCTOKEN "(" arguments ");" -> com_appel
  ```
- Une expression exp_appel:
  ```
  FUNCTOKEN "(" arguments ")" -> exp_appel //appel de fonction
  ```
  
La compilation se réalise en 2 étape. A partir de l'ast récupéré après le parsing réalisé par lark, une première étape consiste à repérer les différentes fonctions (qui sont les noeuds enfants du noeud racine de l'arbre). Une fois ces fonctions identifiées, on va récupérer leurs arguments, leurs variables, leur nom, la variable de retour et leur sous-arbre, et les stocker dans un dictionnaire.
Le dictionnaire des fonctions aura comme clé un nom de fonction, comme valeur un sous dictionnaire, qui contiendra les clés ["args"], ["vars"], ["return"] et ["tree"], et qui contiendra les données récupérées.

Ensuite, on construit les corps des fonctions:
- Pour la fonction main, on commence par convertir les arguments reçus dans argv et argc en integer. Si argc est différent du nombre d'arguments de main (+1), alors on sautera directement à la fonction "exit_error".
- On positionne les arguments et les registres pour constituer le frame de la fonction (pour main, cela se fait avant de compiler le vrai corps de main), puis on appelle la fonction. Quand la fonction est terminée, on enregistre le résultat de la fonction dans rax, on supprime les variables locales de la pile, et on retourne à l'instruction d'appel (qui se situe sur le haut de la pile). On élimine l'espace qui était alloué aux arguments sur la pile, puis on continue l'éxecution.
### Fonctionnalités opérationnelles
Les fonctionnalités suivantes ont été testées avec les exemples ci-dessus:
- Appel de fonction simple
- Appel de fonction avec un argument
- Appel de fonction imbriqué dans une fonction
- Assignation d'une variable avec le résultat d'une fonction
- Utilisation de variables locales pour une fonction
- Utilisation de fonctions dans les calculs avec opérateurs binaires
- Utilisation du résultat d'une fonction dans un print
### Limites du projet

- Tout d'abord la grammaire utilisée n'est pas assez restrictive pour empêcher certaines erreurs de compilation:, puisque l'appel de fonction est une expression (ceci a du sens dans la mesure où on l'utilise pour les assignations), il est possible d'utiliser un appel de fonction comme on utiliserait un argument (à noter que la compilation réussit):
  ```c
  main(test()) {
    A = test();
    printf(test());
    return(0);
  }
  test() {
      return(55);
  }
  ```
  ```
  >./program.out 3
  55
  ```
- Ensuite, une fonction qui n'est pas appelée va tout de même être compilée (code mort)
- La récursivité n'est pas correctement assurée (en particulier l'état de la pile n'est pas correct).