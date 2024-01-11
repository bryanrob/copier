# Copier
*Name is subject to change.*

## Table of Contents
- [Summary](#summary)
- [Disclaimer](#disclaimer)
- [Setup](#setup)
- [Use](#use)
  - [CLI](#cli)
  - [GUI](#gui)
- [Project Developers](#project-developers)

## Summary
A file copying python script for ensuring that files are properly replicated.

## Disclaimer
This project is *very* much in development.  Some features are missing, and those that are currently implemented **may not work as intended**.

Furthermore, the GUI can only work with Windows for now.  The dependency for `tkfilebrowser` and `pywin32` is planned to be removed.

## Setup
If you want to build the program yourself, follow the steps below.

The program requires Python3 (version 3.11+).

The CLI (`copier.py`) depends on standard-issue Python packages.
  ```
  hashlib
  json
  os
  queue
  shutil
  sqlite3
  threading
  time
  ```

The GUI (`inteface.py`) requires the following dependencies (also listed within `requirements.txt`):
  ```
  customtkinter (ver. 5.1.3)
    - The interface backbone for the GUI.
  tkfilebrowser (ver. 2.3.2)
    - A robust file-exploration system.
    - A later update will remove this dependency for (hopefully) cross-OS support.
  pywin32 (ver. 306)
    - A a dependency of tkfilebrowser.
    - A later update will remove this dependency for (hopefully) cross-OS support.
  pyinstaller (ver. 5.13.0)
    - A Python wrapper.
  ```

You can either set this up using standard Python3 (ver. 3.11+).
1. Download & install Python.
   - If this is already fulfilled, you can skip to step 2.
   - On **Windows**, you can do either of the following:
     - In either `cmd` or `powershell` on Windows 10+, you can use the `winget` package manager.
       - Python3: `winget install -e --id Python.Python.3.11`
     - Download Python via their official website *or* through an alternative package manager.
   - On **MacOS**, you can:
     - Download Python via their official website or other Apple-approved means.
   - On (many) **Linux** distributions, you can do either of the following:
     - See your distributions' documentation for installing Python through your package manager.
     - Download Python via their official website.
2. Clone this repository to your computer; then (using the command line) access the directory in which the cloned repository exists.
3. **(Optional)** Create a virtual environment with `python -m venv copier_venv`.
   - To activate it on Windows, use `.\copier_venv\Scripts\activate`.
     - You may need to change your Powershell ExecutionPolicy beforehand.
   - You may need to update pip for the virtual environment.
     - While the virtual environment is active, run `python -m pip install --upgrade pip`.
   - To deactivate on Windows, use `deactivate`.
4. Install dependencies.
   - If you have created a virtual environment, make sure to activate it beforehand.
   - To install the requirements, use: `pip install -r requirements.txt`
5. When everything is installed properly, you can begin wrapping the GUI app into an EXE file:
   - This should allow the program to be usable across **most** Windows devices that do not have this program's dependencies pre-installed.
     - You can wrap to an external storage device for a portable version of this program.
   - The wrapper (`pyinstaller`) must point to the included `/versionData/` folder, as well as the installation paths for `customtkinter` and `tkfilebrowser`.
   - The command below is a template for you to modify to your needs.
  ```
  pyinstaller --noconfirm --onedir --add-data "./versionData;versionData/" --add-data "<Path to CustomTKinter>;customtkinter/" --add-data "<Path to TKFileBrowser>;tkfilebrowser/" .\main.pyw
  ```
   - If you are on Windows, you can use either of the following Batch scripts depending on how your environment has been set up up to this point:
     - If you used a virtual environment, use `_win_packager_venv.bat`.
     - If you did **not** use a virtual environment, use `_win_packager.bat`.

## Use
### CLI
Run the `copier.py` script within your terminal:
```
python ./copier.py -s:"<source file/folder>" -d:"<destination directories>" <additional flags>
```
If you want to copy multiple files/directories, you can specify multiple sources OR use the `--sources` flag with a Pythonese list as an argument.
```
python ./copier.py -s:"<source file/folder 1>" -s:"<source file/folder 2>" -d:"<destination directories>" <additional flags>
```
```
python ./copier.py --sources:["<source file(s)/folder(s)>"] -d:"<destination directories>" <additional flags>
```
The following is a list of the currently implemented flags.  Marked flags have a shortened version being one dash (-) followed by its first letter.
- `--source:<path> / -s` The source directory of the file that you want to target.
  - Must be a string to the source directory.
  - Can be called multiple times.
- `--sources:[<path(s)>]` The sources that you want to copy.
  - Must be a Python-formatted list containing the paths to each source file/directory.
  - Overrides any sources from the individual `--source` flag(s).
- `--destination:<path> / -d` The destination in which you want to send your copied files to.
  - Must be a single path string to the destination directory.
- `--job-type:<string> / -j` The process that you want to execute, such as a copy or move operation.
  - Must be a single string that can be either `Copy` or `Move`.
- `--log-destination:<path> / -l` The path to the log file.  Automatically enables logging when called.
  - Can be the path to the file where the log will be saved to.  Adding no argument defaults to the destination directory.
- `--hash-algorithm:<string> / -h` The hashing algorithm to be used in the logs.
  - Must be the name of the hashing algorithm, being any one of the following: `None`, `MD5`, `SHA256`, `SHA512`, `SipHash`.
- `--thread-count:<int> / -t` The amount of threads that will be created for this job.
  - Must be an integer number.  The GUI limit is 16, but __the CLI has no built-in limit__.
  - **Warning:** excessively high values can be dangerous and may yield unexpected results.
- `--conflict:<int> / -c` The response to encountering a file with the exact same filename in the destination directory.
  - Must be an integer, with `0` doing nothing, `1` always replacing the file in the destination and `2` only replacing the file in the destination if the source file was modified at a later date.
- `--retry:int / -r` If a task fails, repeat for the given amount or until it succeeds.
  - Must be an integer that is greater than 0.
- `--wait:int / -w` Works with `retry`.  If a task fails, wait the given amount of milliseconds until the next attempt is made.
  - Must be an integer that is equal to or greater than 0.
- `--ignore-old-job` If a job had been interrupted and its `job.db` file still exists in the selected destination, instruct the copier to restart the job from the beginning as if the job never ran initially.
  - Has **no** argument.

### GUI
Work in progress.

## Project Developers
- [Robert (bryanrob)](https://github.com/bryanrob)

[Top of README.md](#copier)