import os, sys, copy, math, io, time, setup_paths, logging
from logging import getLogger
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from itertools import permutations
from contextlib import contextmanager
from bath_clamp_headstage import Headstage, experiment
from bath_clamp_setup_steps import *
from bathclamp_vclamp_utils import HardwareSetup
from boards import Vsense2

# vsense_img_path = os.path.join(os.getcwd(), "vsense_tf_function")

vsense_img_path = os.path.join(os.getcwd(), "vsense_tf_function_fixed_gains")

directory = setup_paths.data_dir

if not os.path.exists(vsense_img_path):
    os.makedirs(vsense_img_path)

hardware : HardwareSetup = device_setup(allfour=True)

gain_dict = copy.deepcopy(Vsense2.gain_dict)
del gain_dict[None]

gain_perms = permutations(gain_dict.keys(), 2)
n_gains = math.factorial(len(gain_dict)) // math.factorial(len(gain_dict) - 2)
n_gains = 6

@contextmanager
def suppress_output():
    """
    Context manager to suppress stdout and stderr output.
    This is useful for running tests or experiments without cluttering the console.
    It temporarily redirects stdout and stderr to a StringIO object.
    After the block of code is executed, it restores the original stdout and stderr.
    """
    temp_stdout = sys.stdout
    temp_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = temp_stdout
        sys.stderr = temp_stderr

def cleanse():
    """
    Cleans up the vsense_img_path directory by removing all files.
    This function iterates through the directory and deletes each file.
    It handles any exceptions that may occur during file deletion, such as permission errors.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                pass
            except Exception as e:
                print(f"Error deleting {file_path}: {e}", file=sys.stderr)

def headstage_experiment(lowergain_clamp, uppergain_clamp):
    """
    Conducts an experiment with the specified lower and upper gain clamps.
    This function sets up the hardware, runs the experiment, and saves the results.
    Parameters
    ----------
    lowergain_clamp : int
        The gain value for the lower gain clamp.
    uppergain_clamp : int
        The gain value for the upper gain clamp.
    Returns
    -------
    headstage_obj : Headstage
        The headstage object containing the results of the experiment.
    """
    headstage_obj = experiment(hardware=hardware, lowergain_clamp=lowergain_clamp, uppergain_clamp=uppergain_clamp)
    cleanse()
    return headstage_obj
    

def learn():
    """
    Main function to run the experiment with different gain combinations.
    This function iterates through all possible gain combinations, runs the experiment,
    and saves the results as images in the specified directory.
    """
    # Logger for overall process
    logger = getLogger("Overall Process Logger")
    logger.setLevel(logging.INFO)
    logger.info('Starting the gain combination experiments...')

    total_time = 0
    for i in range(n_gains):
        
        # gains = next(gain_perms)
        gain_1 = 74 # gains[0]
        gain_2 = 36 # gains[1]
        logger.info(f"[IN PROGRESS]: Iter {i+1}, lowergain = {gain_1}, uppergain={gain_2}")
        start = time.perf_counter()
        with suppress_output():
            headstage : Headstage = experiment(
                hardware=hardware, 
                lowergain_clamp=gain_1, 
                uppergain_clamp=gain_2
            )
            experiment_dict = headstage.EXPERIMENTS['Transfer functions fit for clamp'][0]
            figure : Figure = experiment_dict['Comparative gain for voltage_clamp']
            figure_file_name = f"iter_{i+1}_gain1_{gain_1}_and_gain2_{gain_2}.png"
            figure.savefig(os.path.join(vsense_img_path, figure_file_name))
            plt.close('all')
        stop = time.perf_counter()
        duration = (stop - start) * 1000
        total_time += duration
        logger.info(f"[FINISHED]: In {duration : .2f} milliseconds ----")
        cleanse()
        

        
        
    logger.info(f"------------------------\nJob finished in a total of {total_time / (1000 * 60) : .2f} minutes")
