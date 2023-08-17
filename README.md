# Copier
## Summary
A file copying python script for ensuring that files are properly replicated.

## Setup
If you want to build the program yourself, follow the steps below.

The program requires Python3 and the following dependencies:
  ```
  customtkinter (ver. 5.1.3)
    - The interface backbone for the GUI.
  tkfilebrowser (ver. 2.3.2)
    - A robust file-exploration system.
  pywin32 (ver. 306)
    - A a dependency of customtkinter & tkfilebrowser.
  pyinstaller (ver. 5.13.0)
    - A Python wrapper.
  ```

You can either set this up using standard Python3 (ver. 3.12+).
1) Download & install Python.
  - If this is already fulfilled, you can skip to step 2.
  - On **Windows**, you can do either of the following:
    - In either `cmd` or `powershell`, you can use the any of these `winget` command:
      - Python3: `winget install -e --id Python.Python.3.11`
    - Download Python via their official website.
  - On **MacOS**:
    - Download Python via their official website or other Apple-approved means.
  - On **Linux** systems, you can do either of the following:
    - See your distributions' documentation for installing Python through your package manager.
    - Download Python via their official website.
2) Clone this repository to your computer.  
3) In your command line, access the directory in which the cloned repository exists.
4) If you want to, create a virtual environment with `python -m venv copier_venv`.
  - To activate it on Windows, use `.\copier_venv\Scripts\activate`.
  - You may need to update pip for the virtual environment.
    - While the virtual environment is activeated, use: `python -m pip install --upgrade pip`.
  - To deactivate on Windows, use `deactivate`.
5) Install dependencies.
  - If you have created a virtual environment, make sure to activate it beforehand.
  - `pip install -r requirements.txt`
6) When everything is installed properly, you can begin wrapping:
  - 

## Project Developers
- [Robert (bryanrob)](https://github.com/bryanrob)
