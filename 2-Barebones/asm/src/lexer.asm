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
lex_skip_whitespace:
	mov		dl, [rdi]
	cmp		dl, 10
	je		lex_skip
	cmp		dl, 9
	je		lex_skip
	jmp		lex_gs_loop

lex_skip:
	inc		rdi
	jmp		lex_skip_whitespace
lex_gs_loop:
	mov		dl, [rdi]	

	cmp		dl, 59			; Break out of loop if character is ';' or '\0'
	je		lex_gs_done		;
	cmp		dl, 0			;
	je		lex_gs_done		;

	cmp		dl, 10
	je 		lex_gs_skip_append
	;cmp		dl, 9
	;je 		lex_gs_skip_append

	mov		[rsi], dl
	inc		rsi
	inc		rax
lex_gs_skip_append:
	inc		rdi

	jmp		lex_gs_loop
lex_gs_done:
	pop 	rdx
	pop 	rsi
	
	inc		rdi

	leave
	ret

; Get word from token
macro getword input, offset, buf 
{
    local   ..loop                  ; Define local labels
    local   ..done                  ; Only accessible from within the macro.
    mov     rsi, input              ; Load the input string into RSI
    add     rsi, offset             ; Add the input offset to RSI
    mov     rdi, buf                ; Load the buffer address into RDI
    mov     rax, 0                  ; RAX is used to store the last character
    mov     rbx, 0                  ; RBX is used to return the number of bytes read
..loop:
    mov     al, [rsi]               ; Load the next character from the input
    cmp     al, 32                  ; ' '  
    je      ..done
    cmp     al, 10                  ; '\n'
    je      ..done
    cmp     al, 9                   ; '\t'
    je      ..done
    cmp     al, 0                   ; Nullchar
    je      ..done                  ; End of buffer reached.
    mov     [rdi], al               ; Store the character to output buffer
    inc     rsi                     ; Incrememnt source pointer
    inc     rdi                     ; Increment buffer pointer
    inc     rbx                     ; Increment read counter
    jmp     ..loop                  ; Restart loop
..done:
	mov		byte [rdi], 0
	inc		rbx
}
