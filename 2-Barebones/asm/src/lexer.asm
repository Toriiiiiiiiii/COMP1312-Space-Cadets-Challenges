include "macros.asm"

; Get next statement from input
; rdi -> Source
; rsi -> Output Buffer
; Returns:
; rax -> Length of statement
lex_getStatement:
	enter

	push 	rsi
	push	rdx

	mov		rax, 0
	mov		rdx, 0	
lex_gs_loop:
	mov		dl, [rdi]	

	cmp		dl, 59			; Break out of loop if character is ';' or '\0'
	je		lex_gs_done		;
	cmp		dl, 0			;
	je		lex_gs_done		;

	cmp		dl, 10
	je 		lex_gs_skip_append

	mov		[rsi], dl
	inc		rsi
	inc		rax
lex_gs_skip_append:
	inc		rdi

	jmp		lex_gw_loop
lex_gs_done:
	pop 	rdx
	pop 	rsi
	
	inc		rdi

	leave
	ret
