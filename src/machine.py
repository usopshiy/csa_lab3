from __future__ import annotations

import json
import logging
import sys
from enum import Enum

from src.isa import Instruction, Opcode


class ControlSignal(str, Enum):
    # DataMemory
    WriteMem = "write_mem"
    ReadMem = "read_mem"
    # ALU MUX latch
    SelectorSourceRegisterRight = "reg_alu_right"
    IncRight = "inc_right"
    ZeroRight = "zero_right"
    # Register writing
    ReadImmediate = "read_imm"
    # ALU
    ReadALU = "read_alu"
    SumALU = "sum_alu"
    SubALU = "sub_alu"
    IncALU = "inc_alu"
    CmpALU = "cmp_alu"
    # Control
    PCJumpJZ = "jz"
    PCJumpJL = "jl"
    PCJump = "jmp"
    PCNext = "next"
    LatchPC = "latch_pc"


OPCODE_IMPL = {Opcode.ADD: lambda a, b: a + b, Opcode.SUB: lambda a, b: a - b, Opcode.INC: lambda a, _: a + 1}


# ALU processing part
class Alu:
    zf: bool = False
    nf: bool = False

    def process(self, sig: Opcode, left: int, right: int) -> int:
        answer: int = 0
        if sig == Opcode.CMP:
            calc = left - right
            self.nf = calc < 0
            self.zf = calc == 0
            answer = left
        elif sig in OPCODE_IMPL:
            answer = OPCODE_IMPL[sig](left, right)
            self.nf = answer < 0
            self.zf = answer == 0
        else:
            raise ValueError(f"Invalid Control Signal: {sig}")
        return answer


# IO buffers implementation for stream IO
class IO:
    def __init__(self, charset: list[int]):
        self.charset: list[int] = charset
        self.output: str = ""

    def read_byte(self) -> int:
        if len(self.charset) == 0:
            return 0

        value: int = self.charset[0]
        self.charset = self.charset[1:]

        return value

    def write_byte(self, value: int):
        if value > 255:
            self.output += str(value)
            for i in str(value):
                print(i, end="")
        else:
            self.output += chr(value)
            print(chr(value), end="")

    def __repr__(self):
        chars = ""
        for c in self.charset:
            chars += f"{c} "
        return f"{self.charset} {self.output}"


MEMORY_SIZE = 2**10


class DataPath:
    alu: Alu = Alu()

    def __init__(self, instr, data: dict[str, int], inp: list[int]):
        self.data_mem: list[int | IO] = [0 for i in range(MEMORY_SIZE)]
        self.data_mem[0] = IO(inp)
        self.data_mem[1] = IO([])
        self.instr_mem: list[Instruction] = [Instruction(Opcode.NOP) for i in range(MEMORY_SIZE)]
        self.regs: dict[int, int] = dict()
        for reg in range(0, 3):
            self.regs[reg] = 0

        i: int = 2
        while i < len(data):
            if data[str(i)] == ord("\\"):
                if data[str(i + 1)] == ord("n"):
                    self.data_mem[i] = ord("\n")
                else:
                    self.data_mem[i] = ord("\0")
                i += 2
            else:
                self.data_mem[i] = int(data[str(i)])
                i += 1
        for key, value in instr.items():
            self.instr_mem[int(key)] = Instruction(Opcode(value["opcode"]), list(value["args"]))

    def latch_reg(self, reg: int, value: int) -> None:
        self.regs[reg] = value

    def load_reg(self, reg: int) -> int:
        return self.regs[reg]

    def get_zf(self) -> bool:
        return self.alu.zf

    def get_nf(self) -> bool:
        return self.alu.nf

    def ld(self, target_reg: int, memory_address: int):
        # intercept input
        if memory_address == 0:
            self.latch_reg(target_reg, self.data_mem[memory_address].read_byte())
        else:
            self.latch_reg(target_reg, self.data_mem[memory_address])

    def st(self, source_reg: int, memory_address: int):
        # intercept output
        if memory_address == 1:
            self.data_mem[memory_address].write_byte(self.load_reg(source_reg))
        else:
            self.data_mem[memory_address] = self.load_reg(source_reg)


def is_reg(reg: str) -> bool:
    return "x" in reg


class ControlUint:
    @staticmethod
    def parse_instruction_args(instr: Instruction) -> dict[str, int]:
        regs: list[int] = []
        imm: int | None = None
        for arg in instr.args:
            if is_reg(arg):
                regs.append(int(arg[1:]))
            else:
                imm = int(arg)
        return {"tr": regs[0] if len(regs) > 0 else None, "sr": regs[1] if len(regs) > 1 else None, "imm": imm}

    def __init__(self, dp: DataPath):
        self.data_path: DataPath = dp
        self.pc: int = 0
        self.tick_counter: int = 0

    def tick(self) -> None:
        self.tick_counter += 1

    def get_tick(self) -> int:
        return self.tick_counter

    def latch_pc(self, sel_next: bool):
        if sel_next:
            self.pc += 1
        else:
            instr: Instruction = self.data_path.instr_mem[self.pc]
            self.pc = int(instr.args[0])

    def decode_and_execute_control_flow_instruction(self, instr: Instruction):
        opcode: Opcode = instr.opcode

        if opcode is Opcode.HLT:
            raise StopIteration()

        if opcode is Opcode.JMP:
            addr: int = int(instr.args[0])
            self.pc = addr
            self.tick()

            return True

        if opcode is Opcode.JZ:
            self.tick()
            if self.data_path.get_zf():
                self.latch_pc(sel_next=False)
            else:
                self.latch_pc(sel_next=True)
            self.tick()

            return True

        if opcode is Opcode.JL:
            self.tick()
            if self.data_path.get_nf():
                self.latch_pc(sel_next=False)
            else:
                self.latch_pc(sel_next=True)
            self.tick()

            return True

        return False

    def decode_and_execute_instructions(self):
        inst: Instruction = self.data_path.instr_mem[self.pc]
        opcode: Opcode = inst.opcode
        decoded: dict[str, int] = ControlUint.parse_instruction_args(inst)

        if self.decode_and_execute_control_flow_instruction(inst):
            return

        if opcode in [Opcode.ADD, Opcode.SUB, opcode.INC, opcode.CMP]:
            self.tick()  # select for right alu input
            if decoded["imm"] is not None:
                digit: int = decoded["imm"]
            elif decoded["sr"] is not None:
                digit: int = self.data_path.load_reg(decoded["sr"])
            else:
                digit: int = None
            self.data_path.latch_reg(
                decoded["tr"], self.data_path.alu.process(opcode, self.data_path.load_reg(decoded["tr"]), digit)
            )
            self.tick()  # for alu latch
            self.tick()  # for reg mux latch
            self.tick()  # for reg latch

        elif opcode == Opcode.MV:
            self.tick()  # select for right alu input
            if decoded["imm"] is not None:
                addr: int = decoded["imm"]
            else:
                addr: int = self.data_path.load_reg(decoded["sr"])
            self.data_path.latch_reg(decoded["tr"], self.data_path.alu.process(Opcode.ADD, addr, 0))
            self.tick()  # for alu latch
            self.tick()  # for reg mux latch
            self.tick()  # for reg latch

        elif opcode == Opcode.LD:
            if decoded["imm"] is not None:
                addr: int = decoded["imm"]
            else:
                addr: int = self.data_path.load_reg(decoded["sr"])
            self.data_path.ld(decoded["tr"], addr)
            self.tick()  # for ld signal
            self.tick()  # for mux selection
            self.tick()  # for latch_reg

        elif opcode == Opcode.ST:
            if decoded["imm"] is not None:
                addr: int = decoded["imm"]
            else:
                addr: int = self.data_path.load_reg(decoded["sr"])
            self.data_path.st(decoded["tr"], addr)
            self.tick()  # for st signal
            self.tick()  # for data latch

        self.latch_pc(sel_next=True)

    def __repr__(self):
        regs_str: str = ""
        for reg, value in self.data_path.regs.items():
            regs_str += f"{reg}: {value} "
        state_repr: str = f"TICK {self.tick_counter}\n REGS: [{regs_str.strip()}]\n"
        inst: Instruction = self.data_path.instr_mem[self.pc]
        opcode: Opcode = inst.opcode
        instr_repr: str = str(opcode)
        instr_repr += f" {inst.args}"
        return f"{state_repr} {instr_repr}"


def simulate(instr_dict: dict[int, Instruction], data_dictionary: dict[int, str], tokens: list[int]) -> None:
    data_mem: dict[int, int] = dict()
    for key, value in data_dictionary.items():
        data_mem[key] = ord(value)

    dp = DataPath(instr_dict, data_mem, tokens)
    cu = ControlUint(dp)
    try:
        while True:
            logging.debug("%s", cu)
            cu.decode_and_execute_instructions()
    except StopIteration:
        logging.debug("%s", cu)
        pass


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(format="%(levelname)-7s %(module)s:%(funcName)-13s %(message)s")
    if len(sys.argv) == 3:
        instr_dictionary = json.load(open(sys.argv[1], encoding="utf-8"))
        data_dictionary = json.load(open(sys.argv[2], encoding="utf-8"))
        simulate(instr_dictionary, data_dictionary, [0])
    elif len(sys.argv) == 4:
        instr_dictionary = json.load(open(sys.argv[1], encoding="utf-8"))
        data_dictionary = json.load(open(sys.argv[2], encoding="utf-8"))
        with open(sys.argv[3], encoding="utf-8") as file:
            input_token = [ord(i) for i in file.read()]
        simulate(instr_dictionary, data_dictionary, input_token)
    else:
        raise Exception("Wrong arguments")
