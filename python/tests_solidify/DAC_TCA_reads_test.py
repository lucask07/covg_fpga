from typing import Optional, Union
from collections.abc import Iterable
from boards import Daq, Clamp

class ReadTest:
    """
    Class to read and log data from DAC and TCA boards.
    This class is designed to handle multiple boards and their respective reads.
    Attributes
    ----------
    board_list : dict[str, Optional[Union[Daq, Clamp]]]
        Dictionary mapping board names to their respective Daq or Clamp objects.
    log : str
        String to store the log of reads from each board.
    Methods
    -------
    add_board(board, name=None, allow_DAC_write=False, allow_TCA_write=False
                TCA_write=0b000, DAC_write=0b000)
        Adds a board to the board_list and optionally writes to its DAC and TCA.
    get_log()
        Collects and prints the read values from all boards in the board_list.
    """
    def __init__(self):
        """ Initializes the ReadTest class with an empty board list and log.
        """
        self.board_list : dict[str, Optional[Union[Daq, Clamp]]] = dict()
        self.log : str = ""
    
    def add_board(self, board : Optional[Union[Daq, Clamp]], name=None, allow_DAC_write=False, allow_TCA_write=False, TCA_write=0b000, DAC_write=0b000):
        """
        Adds a board to the board_list and optionally writes to its DAC and TCA.
        Parameters
        ----------
        board : Optional[Union[Daq, Clamp]]
            The board object to be added.
        name : str, optional
            The name of the board. If None, the class will use the board's class name.
        allow_DAC_write : bool, optional
            If True, writes to the board's DAC.
        allow_TCA_write : bool, optional
            If True, writes to the board's TCA.
        TCA_write : int, optional
            The value to write to the TCA. Default is 0b000.
        DAC_write : int, optional
            The value to write to the DAC. Default is 0b000.
        """
        self.board_list = self.board_list | {name : board}
        if allow_DAC_write:
            if isinstance(board.DAC, Iterable):
                for dac in board.DAC:
                    dac.write(DAC_write)
            else:
                board.DAC.write(DAC_write)
        if allow_TCA_write:
            if isinstance(board.TCA, Iterable):
                for tca in board.TCA:
                    tca.write(TCA_write)
            else:
                board.TCA.write(TCA_write)
    
    def get_log(self):
        """
        Collects and prints the read values from all boards in the board_list.
        This method iterates through each board, retrieves the DAC and TCA reads,
        and formats them into a readable log string.
        """
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
