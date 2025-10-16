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
