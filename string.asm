extern printf, atol ;déclaration des fonctions externes
global main ; declaration main
section .bss ; section des buffer
buffer resb 256 ; Buffer for string operations
section .data ; section des données
hex_chars: db '0123456789ABCDEF' 
long_format: db '%lld',10, 0 ; format pour les int64_t
string_format: db '%s',10, 0 ; format pour les string
argc : dq 0 ; copie de argc
argv : dq 0 ; copie de argv
s1: dq 0
s2: dq 0
X: dq 0
section .text ; instructions
main :push rbp; Set up the stack. Save rbp
mov [argc], rdi
mov [argv], rsi
mov rbx, [argv] ; initVar
mov rdi, [rbx + 8]
xor rax, rax
call atol
mov [s1], rax
mov rbx, [argv] ; initVar
mov rdi, [rbx + 16]
xor rax, rax
call atol
mov [s2], rax
mov rbx, [argv] ; initVar
mov rdi, [rbx + 24]
xor rax, rax
call atol
mov [X], rax
mov rax, "abcd"
mov [s1 ], rax ; asgt_str
mov rax, "efgh"
mov [s2 ], rax ; asgt_str
mov rax, [s2 ] 
mov [s1 ], rax ; asgt_str
mov rax, [s1] 
mov rsi, rax 
mov rdi, long_format 
xor rax, rax 
call printf 
pop rbp
xor rax, rax
ret
