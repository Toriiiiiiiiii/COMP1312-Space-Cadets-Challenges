include "macros.asm"

; Prints an *unsigned* integer stored in `rax`.
print:
	enter

	; Special case for when `rax` = 0
	cmp		rax, 0
	je		.zero

	; Push all the registers that will be used
	push	rax
	push	rdx
	push	rcx
	push	rbx
	push	rdi

	; RCX will point to the next character to write in the string.
	mov		rcx, rbp
	dec		rcx

	; Max number is (2^64)-1, which is 20 digits.
	sub 	rbp, 20

	; RBX will count the total length of the string
	mov 	rbx, 0

.conv_loop:
	; Increment counter
	inc		rbx

	; If `rax` == 0, the conversion is done.
	cmp		rax, 0
	je		.conv_loop_done

	; Reset RDX, which is used in `div`.
	mov		rdx, 0
	mov		rdi, 10
	div		rdi	

	; RDX will contain the remainder of the division, which is what we are interested in.
	; Adding 0x30 to any number < 10 will convert it to its ASCII code.
	add		dl, 0x30
	mov		[rcx], dl

	; Advance the pointer
	dec		rcx
	jmp		.conv_loop

.conv_loop_done:
	; Output the converted string
	write 	STDOUT, rcx, rbx
	write	STDOUT, newln, 1

	; Reset the value of RBP
	add		rbp, 20
	
	; Restore used registers
	pop		rdi
	pop		rbx
	pop		rcx
	pop		rdx
	pop		rax
	
	; Return from the function
	leave
	ret

.zero:
	; SPECIAL CASE:
	;  |-> When the number provided to `print` is zero, the above algorithm will result
	;      in a blank line being printed. Handle that here by simply printing "0\n".
	write	STDOUT, nZero, nZero.size
	leave
	ret

newln str 10
nZero str "0", 10
