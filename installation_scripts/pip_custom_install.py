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

class PackageProgress:
    def __init__(self, total_packages):
        self.progress_bar = str()
        self.installed = 0
        self.total_packages = total_packages
        self.SUCCESS_ASSOCIATED = "█"
        self.YET_ASSOCIATED = "-"
    
    def print_progress(self):
        percent = 100 * (self.installed / float(self.total_packages))
        self.progress_bar = self.SUCCESS_ASSOCIATED * int(percent/1.5) + self.YET_ASSOCIATED * (int(100/1.5) - int(percent/1.5))
        print(f"\r[{self.progress_bar}] {percent:.2f}%", end = "")
    
    def install_packages(self, package):
        """
        This handles each package manually and so we have a 
        total control of what the stdout and stderr messages should be.
        """
        result = subprocess.run(["pip", "install", package], capture_output = True, text = True)
        if result.returncode == 0:
            self.installed += 1
            write_to_log(f"Package {package} installed successfully!\n")
            self.print_progress()
        else:
            write_to_log(f"Failed to install {package} package!\n")
            self.print_progress()
            sys.exit(f"\nFailed to install {package} package!\n")

def write_to_log(message):
    """
    This function writes stdout and stderr to the slug so that 
    later users can keep track of their installation process. 
    All of this is to simplify the stderr and out messages!
    """
    with open(LOG_NAME, "a") as slug:
        slug.write(message)

try:
    packages = []
    with open(REQUIREMENTS, "r") as f:
        for pack in f:
            if pack.startswith(COMMENT_MARKER):
                continue
            comment_marker_index = pack.find(COMMENT_MARKER)
            if comment_marker_index != -1:
                pack = pack[:comment_marker_index]
            packages.append(pack.rstrip())
    progress_obj = PackageProgress(len(packages))
    [progress_obj.install_packages(package) for package in packages]
    print()
except IOError:
    write_to_log("Installing scripts - requirements.txt - not found")
    print("Installing scripts - requirements.txt - not found")
    sys.exit(1)
