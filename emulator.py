from rsrender import rsrender, tiles
from assembler import assemble

import pygame
from pygame.locals import *

from json import loads
from random import randint
from math import sqrt
import sys
#from time import sleep


TRIG_LUT = loads(open("trig_lut.json").read())

BLOCKING_WARNING = """WARNING!
The active kernel has tried to read from a port that is not 2 or 3. Since these are physically disconnected in the hardware design, the GPU will never resume from the blocking state until reset. This means an effective termination of the program."""


def extract_value_from_number(number, offset, bitwidth):
    return (number >> offset) & (2**bitwidth-1)


class ProgramRunner:
    def __init__(self, p, s, ls: rsrender.RSLampScreen):
        self.lampscreen = ls
        self.primary = p
        self.secondary = s
        self.parameter = 0
        self.pc = 0
        self.regfile = [randint(0, 255) for i in range(64)]
        self.regfile[0] = 0
        self.port_values = [randint(0, 255) for i in range(16)]
        self.lo = randint(0, 255)
        self.hi = randint(0, 255)
        self.active = False


    def obtain_new_parameter(self):
        p = self.parameter
        self.parameter += 1
        if self.parameter == 64:
            self.active = False
        return p

    def reset(self):
        self.parameter = 0
        self.active = False
        self.pc = 0
        self.regfile = [randint(0, 255) for i in range(64)]
        self.regfile[0] = 0
        self.port_values = [randint(0, 255) for i in range(16)]
        self.lo = randint(0, 255)
        self.hi = randint(0, 255)

        self.clear_screen()

    def clear_screen(self):
        self.lampscreen.initialize_data()

    def plot_rect(self, x1, x2, y1, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                self.lampscreen.set_data(x, 63-y, True)

    def run_program(self):
        # because i cant be fucked to do multicore or interleaving rn
        # im gonna sim a 1-core machine
        self.active = True
        n_primaries = 0
        n_secondaries = 0
        while True:
            # IF
            n_primaries += 1
            n_secondaries += 1
            if self.parameter == 33:
                pass
            current_primary = self.primary[self.pc]
            current_secondary = self.secondary[self.pc]
            self.pc += 1
            # ID
            evfn = extract_value_from_number
            prim_opcode = evfn(current_primary, 12, 4)
            prim_src1 = evfn(current_primary, 6, 6)
            prim_src2 = evfn(current_primary, 0, 6)
            sec_opcode = evfn(current_secondary, 6, 2)
            sec_dest = evfn(current_secondary, 0, 6)
            sec_imm = evfn(current_secondary, 8, 8)
            sec_sbyte = evfn(current_secondary, 15, 1)
            sec_srsh = evfn(current_secondary, 14, 1)
            sec_slrsh = evfn(current_secondary, 13, 1)
            sec_spst = evfn(current_secondary, 8, 1)
            sec_jtgt = evfn(current_secondary, 8, 7)
            sec_prt = evfn(current_secondary, 9, 4)
            sec_cond = evfn(current_secondary, 0, 3)
            # EX
            operand1 = self.regfile[prim_src1] & 255
            operand2 = self.regfile[prim_src2] & 255
            if prim_opcode == 2:
                # addition
                operation_result = operand1 + operand2
                self.lo = operation_result & 255
                self.hi = evfn(operation_result, 8, 1) # cout
            elif prim_opcode == 3:
                # subtraction
                operation_result = operand1 - operand2
                self.lo = operation_result & 255
                self.hi = evfn(operation_result, 8, 1) # cout
            elif prim_opcode == 4:
                # multiplication
                operation_result = operand1 * operand2
                self.lo = operation_result & 255
                self.hi = evfn(operation_result, 8, 8)
            elif prim_opcode == 5:
                # division
                operation_result1 = operand1 // operand2
                operation_result2 = operand1 % operand2
                self.lo = operation_result2 & 127
                self.hi = operation_result1 & 127
            elif prim_opcode == 6:
                # sqrt
                operation_result = int(sqrt(operand1))
                self.lo = operation_result & 15
                self.hi = 0
            elif prim_opcode == 7:
                # trig
                sin, cos = TRIG_LUT[str(operand1)]
                self.lo = sin
                self.hi = cos
            else:
                n_primaries -= 1
            # WB
            if sec_opcode == 0:
                # ldi
                self.regfile[sec_dest] = sec_imm
                if sec_dest == 0:
                    n_secondaries -= 1
            elif sec_opcode == 1:
                wbval = (self.lo, self.hi)[sec_sbyte]
                if sec_srsh:
                    if sec_slrsh:
                        wbval = wbval >> 1
                    else:
                        wbval = (wbval >> 1) + (wbval & 128)
                self.regfile[sec_dest] = wbval
            elif sec_opcode == 2:
                wbval = (self.lo, self.hi)[sec_sbyte]
                branch_taken = False
                invert = sec_cond & 4
                sec_cond = sec_cond & 3
                if sec_cond == 0:
                    branch_taken = True
                elif sec_cond == 1:
                    branch_taken = wbval == 0
                elif sec_cond == 2:
                    branch_taken = wbval and not wbval & 128
                elif sec_cond == 3:
                    branch_taken = wbval & 128
                if invert:
                    branch_taken = not branch_taken
                if branch_taken:
                    self.pc = sec_jtgt
            elif sec_opcode == 3:
                if sec_spst:
                    # port store
                    wbval = (self.lo, self.hi)[sec_sbyte]
                    self.port_values[sec_prt] = wbval
                else:
                    if sec_prt == 3:
                        wbval = self.obtain_new_parameter()
                        if wbval == 64:
                            break # done
                    elif sec_prt == 2:
                        x1, y1, x2, y2 = self.port_values[:4]
                        self.plot_rect(x1, x2, y1, y2)
                    else:
                        sys.stderr.write(BLOCKING_WARNING)
                        break
                    if sec_srsh:
                        if sec_slrsh:
                            wbval = wbval >> 1
                        else:
                            wbval = (wbval >> 1) + (wbval & 128)
                    self.regfile[sec_dest] = wbval
            self.regfile[0] = 0 # 0 cannot be changed :3
        print(f"Executed {n_primaries}/{n_secondaries} primary/secondary instructions!")
        instrs_per_core = n_secondaries / 8
        instr_time_bounds = (120, 240, 160)
        est_server_tps = 27
        exe_time_lower = round(instrs_per_core*instr_time_bounds[0]/est_server_tps)
        exe_time_upper = round(instrs_per_core*instr_time_bounds[1]/est_server_tps)
        exe_time_pred = round(instrs_per_core*instr_time_bounds[2]/est_server_tps, 2)
        print(f"Estimated execution time bounds: [{exe_time_lower}s/{exe_time_upper}s]")
        print(f"Exact runtime estimation: {exe_time_pred}s")


if __name__ == "__main__":
    program_name = "demo/heart.asm"
    assemble(program_name)
    with open("binaries/"+program_name) as rf:
        progdata = loads(rf.read())
    primary_bytes = progdata["primary"]
    secondary_bytes = progdata["secondary"]
    while len(primary_bytes) < 128:
        primary_bytes.append(0)
    while len(secondary_bytes) < 128:
        secondary_bytes.append(0)

    dsp = pygame.display.set_mode((640, 720))

    root = rsrender.RSRootObject(dsp, (64, 72))
    renderpanel = rsrender.RSRenderPanel(root, (0, 0, 64, 72))
    renderpanel.set_tile(tiles.BLACK)
    screenpanel = rsrender.RSLampScreen(renderpanel, (0, 0, 64, 64))
    ctrlpanel = rsrender.RSIOPanel(renderpanel, (0, 64, 16, 2), 4)
    ctrlpanel.set_tile(tiles.RED)

    pr = ProgramRunner(primary_bytes, secondary_bytes, screenpanel)

    button_reset = rsrender.RSIOTile(ctrlpanel, (0, 0), tiles.BUTTON_TYPE)
    button_run = rsrender.RSIOTile(ctrlpanel, (8, 0), tiles.BUTTON_TYPE)
    button_reset.set_trigger(pr.reset, (), {})
    button_run.set_trigger(pr.run_program, (), {})

    while True:
        dsp.fill((0, 0, 0))
        root.draw_all()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == MOUSEBUTTONDOWN:
                root.handle_input()
        pygame.display.update()
        pygame.time.wait(10)
