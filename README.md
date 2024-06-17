# Compiler

Le projet compilateur est un projet utilisant des notions d'assembleur et de python. 
Ce git résume comment compiler le projet et comment il fonctionne.
Dans ce projet chaque fonctionnalité a été traitée par une personne différente, Victor Matrat traitant les fonctions et Camille de Mollerat du Jeu traitant les chaînes de caractères. 


## Table des Matières

- [Branches](#branches)
- [Fonctions](#fonctions)
- [String](#string)

-------------------------------------------------------------------------------------------------------------------------------------

## Branches

Le projet est composé de 3 branches: 
- Une branche "main" qui regroupe le code de base du fonctionnement du compilateur, ainsi qu'un exemple de code nanoc fonctionnel.
- une branche "functions" qui regroupe l'ensemble des codes permettant de compiler des fonctions. POur se faire, il suffit de faire la commande:
```bash
python main.py hello.c hello.asm
```
puis pour lire le code assembleur, il faut faire :
```bash
Nasm –f elf64 hello.asm 
Gcc -no-pie hello.o
./a.out // suivi des entrées
```
- une branche "function_string" qui regroupe l'ensemble des codes permettant de compiler des chaînes de caractères. POur se faire, il suffit de faire la commande:
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

### Exemples de codes
### Principe de compilation
### Fonctionnalités opérationnelles
### Limites du projet

  

## String

Cette partie du projet permet de traiter les chaînes de caractères grâce au compilateur.

### Exemple de codes

```python
main(s1,s2,X){
    print(s1);
    print(s2);
    X = len(s1); 
    print(X);
    return 0;
}
```

### Principe de compilation

Les prinipales opérations rajoutées sont : 
- l'assignation de chaînes de caractères, qui assigne une chaîne de caractère à une variable.
- le calcul de la taille d'une chaîne de caractères, qui prend en entrée la chaîne de caractère et qui la parcourt jusqu'à arriver à la fin de la chaîne tout en comptant le nombre de caractères parcouru.
- la recherche d'un caractère, qui prend la chaîne de caractère et la position du caractère recherché et qui renvoie le caractère sous forme de nombre. Pour cela on place le pointer directement à l'endroit concerné et on place ce qui s'y trouve dans rax
- la concaténation de deux chaînes de caractères, qui s'opére en copiant directement la chaîne numéro deux à la suite de la chaîne numéro une.

### Fonctionnalités opérationnelles

Nous avons commencé par mettre en place le parser. Pour qu'il fonctionne correctement, nous avons séparé les variables en deux : celles qui correspondent à des chaînes de caractères qui commencent par s et les autres qui correspondent à des nombres. 
Puis nous nous sommes occupés de la façon de gérer les chaînes de caractères dans le compilateur, ainsi que de la façon dont calcule la longueur d'une chaîne.  

### Limites du projet
L'assignation peut entraîner des problèmes des pointeurs lorsqu'on fait une assignation du type:
'''python
s1 = "abd"
'''
