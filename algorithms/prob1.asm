section .text:
mv x0, 1000
mv x1, 0
mv x2, 3
loop3:
    sub x0, x2
    jl x0, preloop5
    mv x0, 1000
    add x1, x2
    add x2, 3
    jmp loop3
preloop5:
    mv x0, 1000
    mv x2, 5
loop5:
    sub x0, x1
    jl x0, preloop15
    mv x0, 1000
    add x1, x2
    add x2, 5
    jmp loop5
preloop15:
    mv x0, 1000
    mv x2, 15
loop15:
    sub x0, x1
    jl x0, exit
    sub x1, x2
    add x2, 15
    jmp loop15
exit:
    out x0
    hlt