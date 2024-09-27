section .text:
in x0
loop:
    cmp x0, 0
    jz exit
    out x0
    in x0
    jmp loop
exit:
    hlt