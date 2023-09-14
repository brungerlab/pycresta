

## PyCrESTA Installation
-> Make sure that you don't execute the SBGrid shell script otherwise some python programs get installed in the SBGrid path!

----------------------------------------------------------------------------------------------------------------------------
There are two installation methods: method A uses Homebrew and only works on Mac OS and method B uses conda and works on both Mac OS and linux computers

----------------------------------------------------------------------------------------------------------------------------
Method A: Installation on Mac OS via Homebrew:

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
Install sdl2 packages:

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

	pip3 install scikit-spatial

	pip3 install mrcfile

	pip3 install starfile

	pip3 install matplotlib

----------------------------------------------------------------------------------------------------------------------------
Method B: Installation via conda. Install conda, see https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

	conda create -n pycresta
	
	conda activate pycresta
	
	pip install ffpyplayer kivy kivy-examples kiwisolver
	
	pip install pandas scipy scikit-image scikit-spatial mrcfile starfile matplotlib
 
 Note: when using this installation method, the 
 
    conda activate pycresta
 
 command needs to be executed each time a new terminal window is opened.    
----------------------------------------------------------------------------------------------------------------------------

After installation, then 'cd' to the pycresta directory, run:

	cc -fPIC -shared -o rot3d.so rot3d.c 

enter `python3 cresta.py` to start CrESTA

----------------------------------------------------------------------------------------------------------------------------
See the [Google Drive Files](https://drive.google.com/drive/folders/1_1u66QeEMyWK0kxrFrkLmuDgQMvQY5Np?usp=sharing) for test data and tomograms.


------------------------------------------------------------------------------------------------------------------------------------------------------
### Creating CrESTA in Python:

This software is translated from [John Jacob Peters' repository](https://github.com/johnjacobpeters/tom_cryoET) (in Matlab) with new features added. The "Tom_Toolbox" folder in John's repository contains functions for performing different calculations, and some of these functions are translated and implemented in tom.py. 

When converting code from Matlab to Python, be aware that Python uses 0-based indexing and Matlab uses 1-based indexing. Also make sure that variable datatypes are equivalent (e.g. Matlab's "single" corresponds to "float32" in Python). If you see Matlab code that uses "tom_mrcread()" or "tom_starread()", there is no need to translate these two helper functions: simply import the mrcfile and starfile module in Python and use mrcfile.read() and starfile.read() instead. It is also important to note that some functions used for matrix rotations/translations uses the ZY axis instead of the XY axis, so flipping X and Z values may resolve issues if no other problems are found. For testing, use your IDE's debugger and compare results with the Matlab version of the software. 

Use [NumPy Cheat Sheet](https://mathesaurus.sourceforge.net/matlab-numpy.html) to help with converting Matlab code into Python NumPy.

[The Matlab to Python Converter](https://translate.mat2py.org/) also proved useful, but required testing and editing after.

Files In This Repository:
- cresta.py contains the functions that respond to user input on the GUI (pressing buttons).
- tom.py contains helper functions for the cresta.py functions, and is the python version of the TOM Toolbox Matlab functions used in the old repository.
- gui.kv builds the user interface, and gives text inputs/buttons unique id's that can be accessed in cresta.py.
- The old Matlab repository called one C function, rot3d.c, which has been kept in this repository for runtime optimization.

[This paper](https://www.sciencedirect.com/science/article/pii/S1047847722000211) contains the conceptual background for the functions and calculations.

The pycresta repository history can be found [here](https://github.com/psliz05/pycrest); before it was transitioned to this current repo.
