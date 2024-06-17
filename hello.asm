extern printf, atol ;déclaration des fonctions externes
section .data ; section des données
long_format: db '%lld',10, 0 ; format pour les int64_t
error_msg_args : db 'Error: wrong number of arguments',10, 0
argc : dd 0 ; copie de argc
argv : dd 0 ; copie de argv
section .text ; instructions

global exit_error
global main
global test

main:
push rbp
mov rbp, rsp
push rdi
push rsi
cmp rdi, 3
jne exit_error
mov rbx, rsi
mov rdi, [rbx + 8]
xor rax, rax
call atol
push rax
mov rdi, [rbx + 16]
xor rax, rax
call atol
push rax
push rbp
mov rbp, rsp
sub rsp, 8
mov rax, 0
mov [rbp - 8], rax
loop1 :
mov rax, [rbp + 8]
cmp rax, 0
jz fin1
mov rax, 1
push rax
mov rax, [rbp + 8]
pop rbx
sub rax, rbx
mov [rbp + 8], rax
mov rax, 1
push rax
mov rax, [rbp + 16]
pop rbx
add rax, rbx
mov [rbp + 16], rax
jmp loop1
fin1 :mov rax, [rbp + 16]
mov rsi, rax 
mov rdi, long_format 
xor rax, rax 
call printf 
push 20
mov rax, [rbp + 16]
push rax
xor rax, rax
call test
mov [rbp + 8], rax
mov rax, [rbp + 16]
mov rsi, rax 
mov rdi, long_format 
xor rax, rax 
call printf 
add rsp, 8
pop rbp
mov rax, 60
xor rdi, rdi
syscall

test:
push rbp
mov rbp, rsp
sub rsp, 8
mov rax, [rbp + 24]
push rax
mov rax, [rbp + 16]
pop rbx
add rax, rbx
mov [rbp - 8], rax
mov rax, 1
push rax
mov rax, [rbp + 16]
pop rbx
add rax, rbx
mov [rbp + 16], rax
mov rax, [rbp - 8]
push rax
mov rax, [rbp + 16]
pop rbx
add rax, rbx
mov [rbp + 16], rax
add rsp, 8
mov rax, [rbp + 16]
pop rbp
ret

exit_error:
mov rsi, error_msg_args
mov rdi, long_format
xor rax, rax
call printf
mov rax, 60
xor rdi, rdi
syscall
