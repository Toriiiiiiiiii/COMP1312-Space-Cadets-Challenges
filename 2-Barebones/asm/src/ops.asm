OPC_ZERO = 0
OPC_INCR = 1
OPC_DECR = 2
OPC_OUTP = 3
OPC_WHLE = 4
OPC_ENDW = 5
OPC_DO   = 6
OPC_ENDD = 7
OPC_READ = 8

OPC_ENDP = 255

include "strucs.asm"

macro enqueue opc, var, ptr
{
	mov		rax, [op_tail]
	mov		byte [op_queue+rax], opc
	inc		rax
	mov		byte [op_queue+rax], var
	inc		rax
	mov		word [op_queue+rax], ptr
	add		rax, 2
	mov		[op_tail], rax
}

; RAX: Opcode
; RBX: Variable
; RCX: Pointer
macro dequeue
{
	mov		rsi, [op_head]
	mov		rax, 0
	mov		rbx, 0
	mov		rcx, 0
	mov		al, [op_queue+rsi]
	inc		rsi
	mov		bl, [op_queue+rsi]
	inc		rsi
	mov		cx, [op_queue+rsi]
	add		rsi, 2
	mov		[op_head], rsi
}
