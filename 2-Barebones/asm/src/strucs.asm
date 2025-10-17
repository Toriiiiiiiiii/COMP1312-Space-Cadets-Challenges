struc str [data] 
{
    common
    .text db data
    .size = $-.text
}

struc op opc, var, ptr
{
	.opc db opc
	.var db var
	.ptr dw ptr
}
