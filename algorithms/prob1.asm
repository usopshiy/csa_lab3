section .text:
mv x0, 999
mv x1, 0
mv x2, 3
loop3:
    sub x0, x2
    jl preloop5
    mv x0, 999
    add x1, x2
    add x2, 3
    jmp loop3
preloop5:
    mv x0, 999
    mv x2, 5
loop5:
    sub x0, x2
    jl preloop15
    mv x0, 999
    add x1, x2
    add x2, 5
    jmp loop5
preloop15:
    mv x0, 999
    mv x2, 15
loop15:
    sub x0, x2
    jl exit
    mv x0, 999
    sub x1, x2
    add x2, 15
    jmp loop15
exit:
    out x1
    hlt