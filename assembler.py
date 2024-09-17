from os.path import exists
from os import makedirs
import mcschematic
from re import sub
from json import loads, dumps


def new_schem():
    return mcschematic.MCSchematic()


NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
rotate = lambda dir_, angle: (dir_ + angle // 90) % 4
dir_strings = {
    NORTH: "north",
    EAST: "east",
    SOUTH: "south",
    WEST: "west"
}


def place_byte_at(schem, x, y, z, orientation, db):
    #print(f"[SCHEM] Pasting byte at {x}, {y}, {z}...")
    # x, y, z describes bottom bit repeater location
    for i in range(8):
        if db & 1:
            schem.setBlock((x, y, z), f"minecraft:repeater[facing={orientation}]")
        else:
            schem.setBlock((x, y, z), "minecraft:diamond_block")
        y += 2
        db >>= 1


def add_in_direction(x, y, z, direction, magnitude):
    if direction == NORTH:
        return (x, y, z-magnitude)
    if direction == EAST:
        return (x+magnitude, y, z)
    if direction == SOUTH:
        return (x, y, z+magnitude)
    if direction == WEST:
        return (x-magnitude, y, z)
    raise ValueError(f"Invalid direction {direction}")


def place_bytes(schem, xyz, orientation, bytes_, flip=False):
    #print(f"[SCHEM] Pasting program at {xyz}...")
    if len(bytes_) == 0: return
    # north negz
    # east posx
    # south posz
    # west negx
    x, y, z = xyz
    row_index = 0
    word_index = 0
    bank_index = 0
    current_orientation = rotate(orientation, (-1 if flip else 1)*90)
    while len(bytes_) > 0:
        # find out byte
        next_byte = bytes_[0]
        del bytes_[0]
        # place
        place_byte_at(schem, x, y, z, dir_strings[current_orientation], next_byte)

        # find out next coordinates
        if row_index == 15 and word_index == 1:
            current_orientation = rotate(current_orientation, 180) # will rotate back
            row_index = 0
            word_index = 0
            offset = 7-(bank_index%2)*2
            bank_index += 1
            x, y, z = add_in_direction(x, y, z, rotate(orientation, (-1 if flip else 1)*90), offset)
            x, y, z = add_in_direction(x, y, z, rotate(orientation, 180), 30)
            y += 1
        elif word_index == 0:
            word_index = 1
            y -= 1
            x, y, z = add_in_direction(x, y, z, rotate(orientation, (-1 if flip else 1)*90*(-1 if bank_index & 1 else 1)), 3)
        else:
            word_index = 0
            y += 1
            x, y, z = add_in_direction(x, y, z, rotate(orientation, (1 if flip else -1)*90*(-1 if bank_index & 1 else 1)), 3)
            x, y, z = add_in_direction(x, y, z, orientation, 2)
            row_index += 1
        # find out orientation
        current_orientation = rotate(current_orientation, 180)


def save_schem(schem, name):
    #schem.save(r"D:\Minecraft\mchpr_0924\MCHPRS\target\release\schems", "autogen."+name,
    #           mcschematic.Version.JE_1_20_1)
    # alternately, core.autogen.<name>
    schem.save(r"C:\Users\Stevious\AppData\Roaming\.minecraft\schematics", "gpu.autogen."+name.replace("/", "."),
               mcschematic.Version.JE_1_20_1)


def place_value_in_number(number, value, bit_offset, bit_width):
    offset_value = (value & ((1<<bit_width)-1)) << bit_offset
    return number | offset_value


def format_16bit(num):
    s = bin(num).removeprefix("0b").zfill(16)
    return f"{s[:8]} {s[8:]}"


def assemble(fp):
    try:
        with open("isa.json") as isafile:
            isa_json = loads(isafile.read())
            wildcards = isa_json["wildcards"]
            operations = isa_json["operations"]
            pseudos = isa_json["pseudooperations"]
    except Exception as e:
        print("Error loading ISA file:", repr(e))
        return
    if not exists(fp):
        print(f"File path '{fp}' does not exist!")
        raise FileNotFoundError(fp)
    with open(fp) as infile:
        line_list = []
        for line in infile.readlines():
            # very basic comment preprocessing
            if "#" in line:
                line = line[:line.find("#")]
            line_list.append(line.removesuffix("\n"))
    for i in range(len(line_list)):
        print(f"\033[32m{str(i).rjust(len(str(len(line_list))))}\033[0m {line_list[i]}")
    # the beast awakens
    amalgamation = " ".join(line_list)
    amalgamation = sub(",", " , ", amalgamation)
    amalgamation = sub(";", " ; ", amalgamation)
    amalgamation = sub(r"\s+", " ", amalgamation)
    print("\n\033[36mPass: Space Parsing\033[0m")
    print(amalgamation)

    # slowly process the beast one step at a time

    print("\n\033[36mPass: Wildcard replacing\033[0m")
    for wc in wildcards:
        amalgamation = amalgamation.replace(wc, wildcards[wc])
    amalgamation = amalgamation.strip()
    print(amalgamation)

    print("\n\033[36mPass: Label collection\033[0m")
    labels = {}
    tmp = []
    instruction_pointer = 0
    last_lex = ";"
    for lexeme in amalgamation.split(" "):
        if lexeme == ";":
            instruction_pointer += 1
            tmp.append(lexeme)
        elif lexeme.startswith("."): #label
            if last_lex == ";":
                labels[lexeme] = instruction_pointer
            else:
                tmp.append(lexeme)
        else:
            tmp.append(lexeme)
        last_lex = lexeme
    amalgamation = " ".join(tmp)
    print("\033[36mPass: Label replacement\033[0m")
    for label in labels:
        amalgamation = sub(f"{label}\\b", "!"+str(labels[label]), amalgamation)
        #amalgamation = amalgamation.replace(label, "!"+str(labels[label]))
    print(amalgamation)
    print(labels)

    print("\033[36mPass: Instruction collection\033[0m")
    primary_instructions = []
    secondary_instructions = []
    current_instruction = []
    is_primary = True
    for lexeme in amalgamation.split(" "):
        if is_primary:
            if lexeme == ",":
                if current_instruction == []:
                    current_instruction.append("NOP")
                primary_instructions.append(" ".join(current_instruction))
                current_instruction = []
                is_primary = False
            elif lexeme == ";":
                raise RuntimeError("Kill yourself")
            else:
                current_instruction.append(lexeme)
        else:
            if lexeme == ";":
                if current_instruction == []:
                    current_instruction.append("LDI $0 !0")
                    raise RuntimeError("Programmer is an idiot!")
                secondary_instructions.append(" ".join(current_instruction))
                current_instruction = []
                is_primary = True
            elif lexeme == ",":
                raise RuntimeError("Fucking slit your wrists")
            else:
                current_instruction.append(lexeme)
    for i, instr in enumerate(primary_instructions):
        line = f"\033[32m{str(i).rjust(len(str(len(primary_instructions))))}\033[31m"
        line += f" {instr.ljust(20)}\033[34m"
        line += f" {secondary_instructions[i]}\033[0m"
        print(line)

    print("\n\033[36mPass: Pseudooperation Resolution\033[0m")
    prims = []
    seconds = []
    for operation in primary_instructions:
        opname, *args = operation.split(" ")
        if opname in pseudos.keys():
            customArgs = {}
            argn = 1
            for arg in args:
                customArgs["%"+str(argn)] = arg
            opFmt = pseudos[opname]["translation"]
            for arg in customArgs:
                opFmt = opFmt.replace(arg, customArgs[arg])
            prims.append(opFmt)
        else:
            prims.append(operation)
    for operation in secondary_instructions:
        opname, *args = operation.split(" ")
        if opname in pseudos.keys():
            customArgs = {}
            argn = 1
            for arg in args:
                customArgs["%"+str(argn)] = arg
                argn += 1
            opFmt = pseudos[opname]["translation"]
            for arg in customArgs:
                opFmt = opFmt.replace(arg, customArgs[arg])
            seconds.append(opFmt)
        else:
            seconds.append(operation)
    for i, instr in enumerate(prims):
        line = f"\033[32m{str(i).rjust(len(str(len(prims))))}\033[31m"
        line += f" {instr.ljust(20)}\033[34m"
        line += f" {seconds[i]}\033[0m"
        print(line)

    print("\n\033[36mPass: Binary generation\033[0m")
    primary_bytes = []
    secondary_bytes = []
    for instr in prims:
        op, *args = instr.split(" ")
        op_fmt = operations[op]["format"]
        fmt_operands = op_fmt.split(" ")
        assert len(fmt_operands) - 1 == len(args)
        instruction_bin = 0
        src_counter = 0
        for i, op_ in enumerate(fmt_operands):
            if op_[0] not in isa_json["schema"]:
                # opcode
                instruction_bin = place_value_in_number(instruction_bin, operations[op]["opcode"], 12, 4)
            elif op_[0] == "$":
                # register
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 6-6*src_counter, 6)
                src_counter += 1
        primary_bytes.append(instruction_bin)
    for instr in seconds:
        op, *args = instr.split(" ")
        op_fmt = operations[op]["format"]
        fmt_operands = op_fmt.split(" ")
        assert len(fmt_operands) - 1 == len(args)
        instruction_bin = 0
        sel_counter = 0
        for i, op_ in enumerate(fmt_operands):
            if op_[0] not in isa_json["schema"]:
                # opcode
                instruction_bin = place_value_in_number(instruction_bin, operations[op]["opcode"], 6, 2)
            elif op_[0] == "&":
                # selector
                if op.lower() == "wbb":
                    offset = (15, 14, 13)[sel_counter]
                else:
                    offset = (15, 14, 8)[sel_counter]
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), offset, 1)
                sel_counter += 1
            elif op_[0] == "$":
                # register
                if not args[i-1][0] == "$":
                    raise RuntimeError("Go die in a hole")
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 0, 6)
            elif op_[0] == "@":
                # port
                if not args[i-1][0] == "@":
                    raise RuntimeError("Go jump off a bridge")
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 9, 5)
            elif op_[0] == "!":
                # immediate
                if not args[i-1][0] == "!":
                    raise RuntimeError("Go choke on rice")
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 8, 8)
            elif op_[0] == ">":
                # jump target
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 8, 7)
            elif op_[0] == "=":
                # condition
                if not args[i-1][0] == "=":
                    raise RuntimeError("Go slip in the shower")
                instruction_bin = place_value_in_number(instruction_bin, int(args[i-1][1:]), 0, 3)
        secondary_bytes.append(instruction_bin)
    makedirs("binaries/"+"/".join(fp.split("/")[:-1]),
             exist_ok=True)
    with open("binaries/"+fp.lstrip("/")+".bin.txt", "w") as wf:
        for i, instr in enumerate(primary_bytes):
            line = f"\033[32m{str(i).rjust(len(str(len(prims))))}\033[33;2m"
            line += f" {format_16bit(instr)}\033[0;31m ({prims[i].ljust(11)})\033[36m"
            line += f" {format_16bit(secondary_bytes[i])}\033[34m ({seconds[i].ljust(20)})\033[0m"
            line_no_colors = line.replace("\033[32m", "").replace("\033[0;31m", "").replace("\033[34m", "").replace("\033[0m", "").replace("\033[33;2m", "").replace("\033[36m", "") # TODO: use regex ffs
            wf.write(line_no_colors+"\n")
            print(line)

    with open("binaries/"+fp.lstrip("/"), "w") as wf:
        json_data = {
            "primary": primary_bytes,
            "secondary": secondary_bytes
        }
        wf.write(dumps(json_data, indent=4))

    print("\n\033[36mPass: Byte string generation\033[0m")
    p_bin = []
    s_bin = []
    for instr in primary_bytes:
        lo = instr & 255
        hi = (instr >> 8) & 255
        p_bin.append(hi)
        p_bin.append(lo)
    for instr in secondary_bytes:
        lo = instr & 255
        hi = (instr >> 8) & 255
        s_bin.append(hi)
        s_bin.append(lo)
    print(p_bin)
    print(s_bin)
    print("Total number of bytes generated:")
    print("\033[31mPrimary:", len(p_bin))
    print("\033[34mSecondary:", len(s_bin), "\033[0m")

    print("\nFilling rest of memory with zeroes...")
    while len(p_bin) < 256:
        p_bin.append(0)
    while len(s_bin) < 256:
        s_bin.append(0)

    print("\n\033[36mFinal pass: Schematic generation\033[0m")

    s = new_schem()
    x = -1
    z = 0
    for i in range(4):
        place_bytes(s, (x, -16, z), SOUTH, p_bin.copy())
        place_bytes(s, (x, -16, z-13), NORTH, s_bin.copy(), True)
        x += 61
    x = -1
    z -= 144
    for i in range(4):
        place_bytes(s, (x, -16, z), NORTH, p_bin.copy(), True)
        place_bytes(s, (x, -16, z+13), SOUTH, s_bin.copy())
        x += 61
    s.setBlock((-49, -17, z-30), "minecraft:glass")
    save_schem(s, fp)

    print("\033[32mAll passes completed successfully.\033[0m")


if __name__ == "__main__":
    assemble("demo/heart.asm")
