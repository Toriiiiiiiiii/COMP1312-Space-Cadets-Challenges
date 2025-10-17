format ELF64 executable

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; CODE SEGMENT
segment readable executable

include "strucs.asm"
include "macros.asm"
include "syscall.asm"
include "print.asm"
include "utils.asm"
include "lexer.asm"
include "ops.asm"

entry main
main:
	enter
	mov		rax, [rbp+8]					; Ensure the correct number of arguments was supplied
	cmp		rax, 2							
	jl		arg_err							

	argv 	1								; Read Arguments
	mov		[path], rax

	open 	[path], O_RDONLY, fd			; Attempt to open the file
	cmp		rax, 0							; Return an error if the file could not be opened.
	jl		open_err	

	read	[fd], src, INPUT_MAX-1			; Read the source code from file
	mov		byte [src+rax], 0
	mov		[src_ln], rax

	close 	fd								; Close the file

	mov		rdi, src
get_toks:
	mov		rsi, tok_buf					; Read statement from source code
	call	lex_getStatement				
	mov		[tok_len], rax					
	
	cmp		rax, 0							; Get length of statement and end if len == 0
	je		after_toks						

	mov		byte [tok_buf+rax], 0			; Ensure the string is null-terminated

	push	rax								; Preserve all registers modified in nested loop
	push	rbx
	push	rcx
	push	rdx
	push	rsi
	push	rdi

	mov		qword [cur_off], 0				; Reset offset before starting loop
tok_loop:
	getword	tok_buf, [cur_off], cur_tok		; Get next word in the statement
	add		[cur_off], rbx					; Store the new offset
	cmp		rbx, 1
	je		tok_loop

	dec		rbx								; If no char was read, break out of loop
	cmp		rbx, 0
	je		next_stmt

	mov		rdx, 0
	mov		rdi, cur_tok	
	mov		rsi, tok_zero
	call	streq
	cmp		rax, 0
	je		not_zero

	getword	tok_buf, [cur_off], cur_tok
	add		[cur_off], rbx
	mov		dl, [cur_tok]

	enqueue OPC_ZERO, dl, 0
	jmp		next_stmt

not_zero:
	mov		rsi, tok_incr
	call	streq
	cmp		rax, 0
	je		not_incr

	getword	tok_buf, [cur_off], cur_tok
	add		[cur_off], rbx
	mov		dl, [cur_tok]

	enqueue	OPC_INCR, dl, 0
	jmp		next_stmt

not_incr:
	mov		rsi, tok_decr
	call	streq
	cmp		rax, 0
	je		not_decr

	getword	tok_buf, [cur_off], cur_tok
	add		[cur_off], rbx
	mov		dl, [cur_tok]

	enqueue	OPC_DECR, dl, 0
	jmp		next_stmt

not_decr:
	mov		rsi, tok_outp
	call	streq
	cmp		rax, 0
	je		not_outp

	getword	tok_buf, [cur_off], cur_tok
	add		[cur_off], rbx
	mov		dl, [cur_tok]

	enqueue OPC_OUTP, dl, 0
	jmp		next_stmt
	
not_outp:	
	mov		rsi, tok_whle
	call	streq
	cmp		rax, 0
	je		not_whle

	getword	tok_buf, [cur_off], cur_tok
	add		[cur_off], rbx
	mov		dl, [cur_tok]

	enqueue	OPC_WHLE, dl, 0
	jmp		next_stmt

not_whle:
	mov		rsi, tok_endw
	call	streq
	cmp		rax, 0
	je		not_endw

	enqueue	OPC_ENDW, 0, 0
	jmp		next_stmt

not_endw:
	cmp		rax, 0							; If at end of statement, breakout
	je		next_stmt
	jmp		tok_loop						; Else, restart loop

next_stmt:
	pop		rdi
	pop		rsi								; Restore registers
	pop		rdx
	pop		rcx
	pop		rbx
	pop		rax

	mov		rbx, rdi						; End loop if at EOF.
	sub		rbx, src						
	cmp		rbx, [src_ln]					
	jge		after_toks						

	jmp 	get_toks
after_toks:
	enqueue	OPC_ENDP, 0, 0
	call 	run_program
	exit 	0
	leave
	ret

open_err:
	write 	STDERR, err_opn, err_opn.size
	exit 	1
	leave
	ret	

arg_err:
	write 	STDERR, err_arg, err_arg.size
	exit 	1
	leave
	ret


; Run a program from the operation queue
run_program:
	enter

run_loop:
	dequeue
	cmp		rax, OPC_ENDP
	je		run_done

	cmp		rax, OPC_ZERO
	jne		run_notzero

	mov		qword [varTable+rbx*8], 0
	jmp		run_loop
run_notzero:
	cmp		rax, OPC_INCR
	jne		run_notincr

	add		qword [varTable+rbx*8], 1
	jmp		run_loop
run_notincr:
	cmp		rax, OPC_DECR
	jne		run_notdecr

	sub		qword [varTable+rbx*8], 1
	jmp		run_loop
run_notdecr:
	cmp		rax, OPC_OUTP
	jne		run_notoutp

	mov		rax, [varTable+rbx*8]
	call	print
	jmp		run_loop
run_notoutp:
	cmp		rax, OPC_WHLE
	jne		run_notwhle

	mov		rax, [varTable+rbx*8]
	cmp		rax, 0
	je		skip_whle
	jmp		run_loop
skip_whle:
	mov 	rcx, 1
skip_whle_lp:
	push	rcx
	dequeue	
	pop		rcx
	cmp		rax, OPC_ENDP
	je		err_no_end
	cmp		rax, OPC_ENDW
	jne		skip_notend

	dec		rcx
	cmp		rcx, 0
	je		run_loop	
skip_notend:
	cmp		rax, OPC_WHLE
	jne		skip_notwhle

	inc		rcx
skip_notwhle:
	jmp		skip_whle_lp
run_notwhle:
	cmp		rax, OPC_ENDW
	jne		run_notendw

	mov		rcx, 0
endw_lp:
	sub		qword [op_head], 4
	mov		rdi, [op_head]
	cmp		rdi, 0
	jl		err_no_whle

	mov		rax, 0
	mov		al, [op_queue+rdi]
	cmp		al, OPC_WHLE
	jne		endw_lp_notwhle

	dec		rcx
	cmp		rcx, 0
	je		run_loop	
endw_lp_notwhle:
	cmp		al, OPC_ENDW
	jne		endw_lp_notendw

	inc		rcx
endw_lp_notendw:
	jmp		endw_lp
run_notendw:
	jmp		run_loop
run_done:
	leave
	ret

err_no_whle:
	write STDERR, err_whl, err_whl.size
	leave
	ret

err_no_end:
	write STDERR, err_end, err_end.size
	leave
	ret	

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; DATA SEGMENT
segment readable writeable

msg		str "here", 10
err_opn	str "ERROR : Could not open file.", 10
err_arg str "USAGE : bb <filename>", 10
err_end str "ERROR : Unterminated WHLE loop.", 10
err_whl str "ERROR : Unmatched ENDW statement.", 10

path:	dq 0
fd:		dq 0

INPUT_MAX = 8192
src:	rb INPUT_MAX
src_ln: dq 0
src_off: dq 0

tok_buf: rb INPUT_MAX
tok_len: dq 0

cur_tok: rb INPUT_MAX
cur_len: dq 0
cur_off: dq 0

tok_zero: db "clear", 0
tok_incr: db "incr", 0
tok_decr: db "decr", 0
tok_outp: db "print", 0
tok_whle: db "while", 0
tok_endw: db "end", 0

varTable: rq 256
op_head: dq 0
op_tail: dq 0

; Each operation is 4 bytes in size - 1 byte for operation, 1 byte for variable, and 2 bytes for pointers.
op_queue:
repeat 2048
	rb 4
end repeat

newln str 10
nZero str "0", 10
