from typing import Optional
from collections.abc import Iterable
from boards import Daq, Clamp

class ReadTest:
    def __init__(self):
        self.board_list : dict[str, Optional[Daq | Clamp]] = dict()
        self.log : str = ""
    
    def add_board(self, board : Optional[Daq | Clamp], name=None, TCA_write=0b000, DAC_write=0b000):
        self.board_list = self.board_list | {name : board}
        if isinstance(board.DAC, Iterable):
            for dac in board.DAC:
                dac.write(DAC_write)
        else:
            board.DAC.write(DAC_write)
        if isinstance(board.TCA, Iterable):
            for tca in board.TCA:
                tca.write(TCA_write)
        else:
            board.TCA.write(TCA_write)
    
    def get_log(self):
        self.log = ""
        for key, value in self.board_list.items():
            self.log += (f"Reads for {key}".center(35, "-") + "\n")
            DAC_reads = [value.DAC] if not isinstance(value.DAC, Iterable) else value.DAC
            TCA_reads = [value.TCA] if not isinstance(value.TCA, Iterable) else value.TCA
            for i, dac in enumerate(DAC_reads):
                self.log += (f"\tDAC {i} read = {dac.read()}\n")
            for i, tca in enumerate(TCA_reads):
                self.log += (f"\tTCA {i} read = {tca.read()}\n")
        print(self.log)
