

## PyCrESTA Installation
-> Make sure that you don't execute the SBGrid shell script otherwise some python programs get installed in the SBGrid path!

----------------------------------------------------------------------------------------------------------------------------
Install Homebrew:

	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Note: on Apple Silicon, insert the following line in the .bash_profile file: 

	eval "$(/opt/homebrew/bin/brew shellenv)"
----------------------------------------------------------------------------------------------------------------------------
Make sure that the installation is OK:

	brew doctor

If it says that command line tools are outdated, run:
```
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install
```
----------------------------------------------------------------------------------------------------------------------------
Install sld2 packages:

	brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer 
----------------------------------------------------------------------------------------------------------------------------
Install python:

	brew install python
----------------------------------------------------------------------------------------------------------------------------
Install virtualenv:

	python3 -m pip install --upgrade pip setuptools virtualenv

Note: some machines may need to add '--users' to end of above command

----------------------------------------------------------------------------------------------------------------------------
Install kivy:

	python3 -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"
----------------------------------------------------------------------------------------------------------------------------
Pip installs:

	pip3 install pandas
 
	pip3 install scipy
 
	pip3 install scikit-image
 
	pip3 install mrcfile
 
	pip3 install starfile
 
	pip3 install matplotlib

----------------------------------------------------------------------------------------------------------------------------
then 'cd' to the pycresta directory, run:

	cc -fPIC -shared -o rot3d.so rot3d.c 

enter `python3 cresta.py` to start CrESTA

----------------------------------------------------------------------------------------------------------------------------
Use Test_Data and TestExamples folders to confirm that everything works.


------------------------------------------------------------------------------------------------------------------------------------------------------
### Creating CrESTA in Python:

This software is translated from https://github.com/johnjacobpeters/tom_cryoET (in Matlab) with new features added.
Use of https://mathesaurus.sourceforge.net/matlab-numpy.html to convert Matlab code into Python NumPy.

cresta.py contains the functions that respond to user input on the GUI (pressing buttons).
tom.py contains helper functions for the cresta.py functions, and is the python version of the TOM Toolbox Matlab functions used in the old repository.
gui.kv builds the user interface, and gives text inputs/buttons unique id's that can be accessed in cresta.py.
The old Matlab repository called one C function, rot3d.c, which has been kept in this repository for runtime optimization.

This paper contains the conceptual background for the functions and calculations: https://www.sciencedirect.com/science/article/pii/S1047847722000211

Repository history can be found at: https://github.com/psliz05/pycrest
