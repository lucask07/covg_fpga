@echo off
setlocal enabledelayedexpansion

:: Make the log file to keep track of the installation process
type nul > "..\log.txt"

:: Check for python version and ensure that it should be 3.9 or above
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
:: %variable:~start,length%: This syntax extracts a substring from variable
set PYVERONE=%PYVER:~0,1%
set PYVERTWO=%PYVER:~2,1%
if "!PYVERONE!" geq "3" (
	if "!PYVERTWO" geq "9" (
		echo Python verification SUCCESS! -- python version 3.9 or above
		echo SUCCESS: Python verification SUCCESS! -- python version 3.9 or above >> "..\log.txt"
	) else (
		echo Users need a version of python compiler of 3.9 or above
		echo FAILURE: Users need a version of python compiler of 3.9 or above >> "..\log.txt"
		exit /b
	)
) else (
	echo Users need a version of python compiler of 3.9 or above
	echo FAILURE: Users need a version of python compiler of 3.9 or above >> "..\log.txt"
	exit /b
)

:: Install required Python packages
echo Start installing pip from requirements.txt >> "..\log.txt"
echo Start installing pip from requirements.txt
:: pip install -r python\requirements.txt :: This line is to be used if we don't want to simplify the stdoutput and stderr
python pip_custom_install.py "../python/requirements.txt" "../log.txt" || goto :error
echo Finished installing pip
echo Finished installing pip >> "..\log.txt"

:: Install Registers.xlsx
echo Start installing Registers.xlsx >> "..\log.txt"
echo Start installing Registers.xlsx
curl https://github.com/Ajstros/pyripherals/blob/main/python/Registers.xlsx -o ..\python\Registers.xlsx || goto :error
echo Finished installing Registers.xlsx >> "..\log.txt"
echo Finished installing Registers.xlsx

echo Writing ~\.pyripherals\config.yml >> "..\log.txt"
echo Writing ~\.pyripherals\config.yml
:: Make .pyripherals directories inside the user's home directory
:: The command `mkdir` will not give an error if the directories already exist
mkdir "%USERPROFILE%\.pyripherals" >nul 2>&1
set PYRI="%USERPROFILE%\.pyripherals"
:: Take the path to the current directory
for /f "delims=" %%a in ('cd .. ^& cd') do set ROOT_DIR=%%a

:: Modify the config.yaml
type nul > %PYRI%\config.yaml || goto :error
echo endpoint_max_width: 32 > %PYRI%\config.yaml
echo ep_defines_path: %ROOT_DIR%\fpga_XEM7310\fpga_XEM7310.srcs\sources_1\ep_defines.v >> %PYRI%\config.yaml
echo fpga_bitfile_path: %ROOT_DIR%\fpga_XEM7310\fpga_XEM7310.runs\impl_1\top_level_module.bit >> %PYRI%\config.yaml
echo registers_path: %ROOT_DIR%\python\Registers.xlsx >> %PYRI%\config.yaml

:: Find FrontPanelUSB directory (equivalent to "find / -name FrontPanelUSB") - only take the first line of the standard output
set OPAL_FOUND=false
echo Finding the path of the Opal Kelly API >> "..\log.txt"
echo Finding the path of the Opal Kelly API
for /f "delims=" %%b in ('dir /s /b C:\FrontPanelUSB 2^>nul') do (
	if "!OPAL_FOUND!"=="false" (
		set WHERE_OPAL=%%b
		set OPAL_FOUND=true
	)
) || goto :error

echo Done finding the path to Opal Kelly - The path is: %WHERE_OPAL% >> "..\log.txt"
echo Done finding the path to Opal Kelly - The path is: %WHERE_OPAL%

echo frontpanel_path: %WHERE_OPAL% >> %PYRI%\config.yaml
echo Finished writing .pyripherals\config.yml >> "..\log.txt"
echo Finished writing .pyripherals\config.yml

:: Create config_yaml for instrbuilder
echo Initiate the config_yaml for the instrbuilder module >> "..\log.txt"
echo Initiate the config_yaml for the instrbuilder module
python create_yaml_instrbuilder.py || goto :error
echo Done initiating instrbuilder's config_yaml >> "..\log.txt"
echo Done initiating instrbuilder's config_yaml

::Inform users that configuration has finished
echo Configuration finished!
echo Configuration finished! >> "..\log.txt"

:error
if %ERRORLEVEL% NEQ 0 (
	echo This installation script has been terminated due to a failed operation 1>&2
)
exit /b %ERRORLEVEL%

endlocal
:: Done
exit /b
