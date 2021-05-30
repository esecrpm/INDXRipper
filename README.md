# INDXRipper
Find index entries in $INDEX_ALLOCATION attributes

![screenshot](https://user-images.githubusercontent.com/84273110/118458300-42e4ae00-b703-11eb-8e59-bcb9de00ca89.png)

Timeline created using mactime.pl on the combined output of INDXRipper and fls.  
See: [sleuthkit](https://github.com/sleuthkit/sleuthkit)
## Motivation
$INDEX_ALLOCATION attributes are used by NTFS directories to store index entries for files in the directory.

A file's index entry contains the following information:

* File name
* File size
* Allocated size of file (size on disk)
* A set of MACB timestamps

The slack space of these attributes may contain index entries of deleted files, even after thier MFT record was recycled. Finding these index entries may help you prove a file existed on a system.

## How it works
INDXRipper scans the MFT for records of directories that have an $INDEX_ALLOCATION attribute. If it finds such a record, it searches the attribute for file references to this record. Since the index entries in the attribute are of the directory's children, the $FILE_NAME attributes in them must contain this file reference.

## Features and Details
### Basic Features
* Applies fixups for index records and MFT records.
* Supports $INDEX_ALLOCATION and $FILE_NAME attributes in extension records
* Supports Unicode filenames
* The full paths of directories are determined using the parent directory references from the MFT records.
* Index entries from orphan directories are listed under "/$Orphan"
* Works on live Windows NTFS drives, using the "\\\\.\\\" notation
* All times outputted are UTC times

### The --bodyfile Switch
If the --bodyfile switch is given, INDXRipper will output a bodyfile for supertimeline creation.  
When creating a supertimeline, it is recommended to use the --deleted-only switch as well.

### The --deleted-only Switch
In addition to the parent file reference, index entries contain a file reference to their own file's MFT record.  
If the --deleted-only switch is given, INDXRipper follows this file reference. If it succeeds, the index entry is not outputted.  

This reduces noise in case you combine the output with the output of fls or MFTECmd.  
The combined output won't contain duplicate lines for files that still have their MFT records.

Well, almost. These duplicate lines cannot be eliminated entirely without potential information loss.  
Deleted entries may have their file reference overitten. The overitten reference will probably be invalid and the entry will be outputted, despite the file having an MFT record.
It's not possible to know if the MFT record the entry pointed to was recycled since.

**Note:** Index entries of deleted files that their MFT record **wasn't** recycled will **not** be outputted! These files' MFT records will be outputted by fls and MFTECmd.

## Installation 
Python 3.8 or above is required.  
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install construct.
```bash
pip install construct==2.10.56
```
Alternatively, you can use the Windows standalone executable. 

## Usage
```bash
# process a dead partition image, get all index entries
python INDXRipper.py ntfs.part.001 output.csv

# process the D: drive, --deleted-only mode, bodyfile output, append "D:" to all the paths
python INDXRipper.py -m D: --deleted-only --bodyfile \\.\D: output.bodyfile
```

## Limitations
* The tool may give false results.
* Entries that are partially overitten may not be found. If they are found, though, the tool may give you false information.

### What this tool doesn't do
* This tool doesn't process $INDEX_ROOT attributes. You won't see an output for every file on the volume
* This tool doesn't carve $INDEX_ALLOCATION attributes. It won't find attributes that thier MFT entry was recycled.


## License
[MIT](https://choosealicense.com/licenses/mit/)
