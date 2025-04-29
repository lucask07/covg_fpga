import subprocess, sys

# Name of the installing scripts will be passed in as the program's argument.
# Failure to pass that in would result in an error
if len(sys.argv) < 3:
    print("Usage: python pip_custom_install.py <where_requirements.txt> <where_slug>")
    sys.exit(1)

# Name of the slug file
LOG_NAME = sys.argv[2]
REQUIREMENTS = sys.argv[1]
COMMENT_MARKER = "#"

def install_packages(package):
    """
    This handles each package manually and so we have a 
    total control of what the stdout and stderr messages should be.
    """
    result = subprocess.run(["pip", "install", package], capture_output = True, text = True)
    if result.returncode == 0:
        write_to_log(f"Package {package} installed successfully!\n")
    else:
        write_to_log(f"Failed to install {package} package!\n")

def write_to_log(message):
    """
    This function writes stdout and stderr to the slug so that 
    later users can keep track of their installation process. 
    All of this is to simplify the stderr and out messages!
    """
    with open(LOG_NAME, "a") as slug:
        slug.write(message)

try:
    with open(REQUIREMENTS, "r") as f:
        for pack in f:
            if pack.startswith(COMMENT_MARKER):
                continue
            comment_marker_index = pack.find(COMMENT_MARKER)
            if comment_marker_index != -1:
                pack = pack[:comment_marker_index]
            install_packages(pack.strip())
except IOError:
    write_to_log("Installing scripts - requirements.txt - not found")
    print("Installing scripts - requirements.txt - not found")
