section .text:
in x0
loop:
    jz x0, exit
    out x0
    in x0
    jmp loop
exit:
    hlt