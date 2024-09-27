section .data:
greeting: "What is your name?\n\0"
hello: "Hello, \0"
hello_end: "!\n\0"
section .text:
    mv x1, greeting
    inc x1
    ld x0, greeting
loop1:
    cmp x0, 0
    jz x0, preloop2
    out x0
    ld x0, x1
    inc x1
    jmp loop
preloop2:
    mv x1, word
    add x1, 3
    mv x2, x1
loop2:
    in x0
    st x0, x1
    cmp x0, 0
    jz preloop3
    inc x1
    jmp loop2
preloop3:
    ld x0, hello
    mv x1, hello
    inc x1
loop3:
    cmp x0, 0
    jz loop4
    out x0
    ld x0, x1
    inc x1
    jmp loop3
loop4:
    ld x0, x2
    cmp x0, 0
    jz x0, preloop5
    out x0
    inc x2
    jmp loop4
preloop5:
    ld x0, hello_end
    mv x1, hello_end
    inc x1
loop5:
    cmp x0, 0
    jz x0, exit
    out x0
    ld x0, x1
    inc x1
    jmp loop5
exit:
    hlt