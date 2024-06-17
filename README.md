# Compiler

Le projet compilateur est un projet utilisant des notions drassembleur et de python. 
Ce git résume comment compiler le projet et comment il fonctionne.


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
python main.py hello.c hello.asm
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

### Exemples de codes
### Principe de compilation
### Fonctionnalités opérationnelles
### Limites du projet

  

## String

Cette partie du projet permet de traiter les chaînes de caractères grâce au compilateur.

### Exemples de codes
```python
main(s1,s2,X){
    s1 = "abcd";
    s2 = "efgh" ;
    s1 = s2 ;
    return(s1);
}
```
### Principe de compilation

Les prinipales opérations rajoutées sont : 
- l'assignation de chaînes de caractères
- le calcul de la taille d'une chaîne de caractères
- la recherche d'un caractère
- la concaténation de deux chaînes de caractères

### Fonctionnalités opérationnelles

Nous avons commencé par mettre en place le parser. Pour qu'il fonctionne correctement, nous avons séparé les variables en deux : celles qui correspondent à des chaînes de caractères qui commencent par s et les autres qui correspondent à des nombres. 
Puis nous nous sommes occupés de l'assignation des chaînes de caractères. 

### Limites du projet

