extern printf, atol ;déclaration des fonctions externes
section .data ; section des données
long_format: db '%lld',10, 0 ; format pour les int64_t
string_format: db '%s',10, 0 ; format pour les int64_t
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
cmp rdi, 2
jne exit_error
mov rbx, rsi
mov rdi, [rbx + 8]
xor rax, rax
call atol
push rax
push rbp
mov rbp, rsp
sub rsp, 8
call test
push rax
mov rax, [rbp + 8]
pop rbx
add rax, rbx
mov [rbp - 8], rax
mov rax, [rbp - 8]
mov rsi, rax 
mov rdi, long_format 
xor rax, rax 
call printf 
mov rax, 2
push rax
call test
pop rbx
add rax, rbx
mov [rbp - 8], rax
mov rax, [rbp - 8]
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
mov rax, 1
mov [rbp - 8], rax
add rsp, 8
mov rax, [rbp - 8]
pop rbp
ret

exit_error:
mov rsi, error_msg_args
mov rdi, string_format
xor rax, rax
call printf
mov rax, 60
xor rdi, rdi
syscall
