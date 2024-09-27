import json
import sys

from src.isa import Instruction, Opcode


def get_meaningful_token(line: str) -> str:
    return line.strip()


def pre_translate(input_file: str) -> list[str]:
    f = open(input_file, 'r')
    lines = [get_meaningful_token(line) for line in f.readlines()]
    f.close()
    while "" in lines:
        lines.remove("")
    return lines


def get_meaningful_text(text: str) -> str:   # removes extra spaces and commas from text
    text.strip()
    return text[1:-1]


def get_instruction(line: str) -> Instruction:
    if line == "hlt":
        return Instruction(Opcode.HLT)
    instr: str = line[:line.find(" ")].lower()
    args = line[line.find(" ") + 1:].split(", ")
    if instr == "in":
        instr = "ld"
        args.append(str(0))     # 0 - in port
    elif instr == "out":
        instr = "st"
        args = [str(1), args[0]]    # 1 - out port
    opcode: Opcode = Opcode(instr)
    return Instruction(opcode, args)


def translate_tokens(data: list[str]):
    jmpdict: dict[str, int] = {}
    datadict: dict[int, str] = {}
    instrdict: dict[int, Instruction] = {}

    textcnt = 0
    if ".data:" in data[0]:
        textcnt += 1
        datacnt: int = 2    # 0, 1 - IO ports
        while True:
            if data[textcnt] == "section .text:":
                break

            label, text = data[textcnt].split(":")
            get_meaningful_text(text)
            jmpdict[label] = datacnt
            for i in text:
                datadict[datacnt] = i
                datacnt += 1

    instrcnt: int = 0
    for i in data[textcnt:]:
        if ":" in i:
            jmpdict[i[:-1]] = instrcnt
        else:
            instr: Instruction = get_instruction(i)
            instrdict[instrcnt] = instr
            instrcnt += 1
    
    return jmpdict, datadict, instrdict


def assert_navigation(jmpdict: dict[str, int], instrdict: dict[int, Instruction]):
    for value in instrdict.values():
        if value.opcode == Opcode.HLT:
            break
        if value.args[-1] in jmpdict.keys():
            value.args[-1] = str(jmpdict[value.args[-1]])


def translate(input_file: str, data_output_file: str, instr_output_file: str):
    tokens = pre_translate(input_file)
    jmpdict, datadict, instrdict = translate_tokens(tokens)
    assert_navigation(jmpdict, instrdict)

    with open(data_output_file, "w") as out_file:
        json.dump(datadict, out_file, indent=4, default=lambda o: o.__dict__)

    with open(instr_output_file, "w") as out_file:
        json.dump(instrdict, out_file, indent=4, default=lambda o: o.__dict__)


if __name__ == '__main__':
    args = sys.argv[1:]
    assert len(args) == 3, "Usage: translator.py <input> <data_output> <instr_output>"

    translate(args[0], args[1], args[2])
