from enum import Enum


class Opcode(str, Enum):
    MV = "mv"
    INC = "inc"
    ADD = "add"
    SUB = "sub"
    JMP = "jmp"
    JZ = "jz"
    JL = "jl"
    LD = "ld"
    ST = "st"
    HLT = "h*lt"

    def __str__(self):
        return str(self.value)


class Instruction:
    def __init__(self, opcode: Opcode, args: list[str] | None = None):
        if args is None:
            args = []
        self.opcode: Opcode = opcode
        self.args: list[str] = args

    def __str__(self):
        return f"{self.opcode} {self.args}"

    def __repr__(self):
        return self.__str__()
