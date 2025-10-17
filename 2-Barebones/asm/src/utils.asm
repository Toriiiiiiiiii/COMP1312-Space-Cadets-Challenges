; Returns the length of string in %rdi.
strlen:
	enter
	mov 	rax, 0
	
	push 	rdx
	mov		rdx, 0
.strlen_loop:
	mov		dl, [rdi+rax]
	cmp		dl, 0
	je 		.strlen_done
	inc		rax
	jmp		.strlen_loop
.strlen_done:
	pop		rdx
	leave
	ret	

; Determine if the strings in %rdi and %rsi are equal.
streq:
	enter
	push	rdx
	push	rcx
	push	rbx
	push	rdi
	push	rsi
	call	strlen
	
	push	rdi
	push	rax
	mov		rdi, rsi
	call	strlen
	mov		rdx, rax
	pop		rax
	pop		rdi

	cmp		rax, rdx
	jne		streq_neq

	mov		rdx, 0
streq_loop:
	cmp		rdx, rax
	je		streq_eq

	mov		bl, [rdi]
	mov		cl, [rsi]	
	cmp		bl, cl
	jne		streq_neq

	inc		rdi
	inc		rsi
	inc		rdx
	jmp		streq_loop

streq_neq:
	mov		rax, 0
	jmp		streq_done
streq_eq:
	mov		rax, 1
streq_done:
	pop		rsi
	pop		rdi
	pop		rbx
	pop		rcx
	pop		rdx
	leave
	ret


; Convert string to unsigned integer
; RDI - String to convert
; Returns:
; RAX - Converted number
strton:
	enter
	push	rdi
	push	rdx
	mov		rax, 0
	mov		rdx, rax
strton_lp:	
	mov		dl, [rdi]
	cmp		dl, 0
	je		strton_dn

	imul	rax, 10
	sub		dl, 48
	add		rax, rdx
	inc		rdi
	jmp		strton_lp

strton_dn:
	pop		rdx
	pop		rdi
	leave
	ret
