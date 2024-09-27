section .data:
word: "Hello, world!\n\0"
section .text:
ld x0, word
mv x1, word
inc x1
loop:
    cmp x0, 0
    jz exit
    out x0
    ld x0, x1
    inc x1
    jmp loop
exit:
    hlt
