; Setup stack frame for function
macro enter 
{
	push	rbp
	mov		rbp, rsp
}

; Restore stack frame for function
macro leave
{
	mov		rsp, rbp
	pop		rbp
}

; Gets argv[n]
macro argv n
{
	local	..loop
	local	..done
	mov		rcx, 0
	mov		rdi, [rbp+16]
..loop:
	cmp		rcx, n
	je		..done

	call	strlen
	add		rdi, rax
	inc		rdi
	inc		rcx
	jmp 	..loop
..done:
	mov		rax, rdi
}
