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

### Exemples de codes
### Principe de compilation
### Fonctionnalités opérationnelles

### Limites du projet

