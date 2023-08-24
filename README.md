# Copier
*Name is subject to change.*

## Summary
A file copying python script for ensuring that files are properly replicated.

## Disclaimer
This project is *very* much in development.  Some features are missing, and those that are currently implemented **may not work as intended**.

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

You can either set this up using standard Python3 (ver. 3.11+).
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
  - To install the requirements, use: `pip install -r requirements.txt`
6) When everything is installed properly, you can begin wrapping the GUI app into an EXE file:
  - This should allow the program to be usable across **most** Windows devices that do not have this program's dependencies pre-installed.
    - You can wrap to an external storage device for a portable version of this program.
  - The wrapper (`pyinstaller`) must point to the included `/versionData/` folder, as well as the installation paths for `customtkinter` and `tkfilebrowser`.
  - The command below is a template for you to modify to your system's needs.
  ```
  pyinstaller --noconfirm --onedir --add-data "./versionData;versionData/" --add-data "<Path to CustomTKinter>;customtkinter/" --add-data "<Path to TKFileBrowser>;tkfilebrowser/" .\main.pyw
  ```
  - If you are on Windows, you can use either of the following Batch scripts depending on how your environment has been set up up to this point:
    - If you used a virtual environment, use `_win_packager_venv.bat`.
    - If you did **not** use a virtual environment, use `_win_packager.bat`.

## Use
### CLI
Run the `copier.py` script within your terminal:
```python
python ./copier.py -s:["<source files/directories>"] -d:"<destination directories>" <additional flags>
```
The following is a list of the currently implemented flags.  Marked flags have a shortened version being one dash (-) followed by its first letter.
- `--sources:[<path(s)>] / -s` The sources that you want to copy.
  - The argument is an array containing the paths to each source file/directory.
- `--destination:<path> / -d` The destination in which you want to send your copied files to.
  - The argument is a single path string to the destination directory.
- `--job-type:<string> / -j` The process that you want to execute, such as a copy or move operation.
  - The argument is a single string that can be either `Copy` or `Move`.
- `--log-destination:<path> / -l` The path to the log file.  Automatically enables logging when called.
  - The argument is the path to the file where the log will be saved to.  Adding no argument defaults to the destination directory.
- `--hash-algorithm:<string> / -h` The hashing algorithm to be used in the logs.
  - The argument is the name of the hashing algorithm, being any one of the following: `None`, `MD5`, `SHA256`, `SHA512`, `SipHash`.
- `--thread-count:<int> / -t` The amount of threads that will be created for this job.
  - The argument is an integer number.  The GUI limit is 16, but __the CLI has no built-in limit__.
- `--conflict:<int> / -c` The response to encountering a file with the exact same filename in the destination directory.
  - The argument is an integer, with `0` doing nothing, `1` always replacing the file in the destination and `2` only replacing the file in the destination if the source file was modified at a later date.
- `--retry:int / -r` If a task fails, repeat for the given amount or until it succeeds.
  - The argument is an integer that is greater than 0.

### GUI
Work in progress.

## Project Developers
- [Robert (bryanrob)](https://github.com/bryanrob)
