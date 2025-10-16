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

entry main
main:
	enter

	; Ensure the correct number of arguments was supplied
	mov		rax, [rbp+8]
	cmp		rax, 2
	jl		arg_err

	argv 	1
	mov		[path], rax

	; Attempt to open the file
	open 	[path], O_RDONLY, fd	

	; Throw an error if return code < 0
	cmp		rax, 0
	jl		open_err	

	read	[fd], src, INPUT_MAX-1
	mov		byte [src+rax], 0
	mov		[src_ln], rax

	close 	fd

	mov		rdi, src
get_toks:
	mov		rsi, tok_buf					; Read statement from source code
	call	lex_getStatement				;
	mov		[tok_len], rax					;
	
	cmp		rax, 0							; Get length of statement and end if len == 0
	je		after_toks						;

	push	rax								; Print the statement to STDOUT
	push	rdi								;
	push	rdx								;
	push	rsi								;
	write	STDOUT, tok_buf, [tok_len]		;
	write	STDOUT, newln, newln.size		;
	pop		rsi								;
	pop		rdx								;
	pop		rdi								;
	pop		rax								;

	mov		rbx, rdi						; End loop if at EOF.
	sub		rbx, src						;
	cmp		rbx, [src_ln]					;
	jge		after_toks						;

	jmp 	get_toks

after_toks:
	exit 	0
	leave
	ret

open_err:
	write STDERR, err_opn, err_opn.size
	exit 1
	leave
	ret	

arg_err:
	write STDERR, err_arg, err_arg.size
	exit 1
	leave
	ret


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; DATA SEGMENT
segment readable writeable

msg 	str "Hello, World!", 10
err_opn	str "ERROR : Could not open file.", 10
err_arg str "USAGE : bb <filename>", 10

path:	dq 0
fd:		dq 0

INPUT_MAX = 8192
src:	rb INPUT_MAX
src_ln: dq 0

tok_buf: rb INPUT_MAX
tok_len: dq 0
