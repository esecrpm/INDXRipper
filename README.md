# INDXRipper
INDXRipper is a tool for carving file metadata from NTFS $I30 indexes. It's fast, and the output is easy to integrate into a timeline!

![screenshot](https://user-images.githubusercontent.com/84273110/118458300-42e4ae00-b703-11eb-8e59-bcb9de00ca89.png)

A timeline created using mactime.pl on the combined output of INDXRipper and fls.  
See: [sleuthkit](https://github.com/sleuthkit/sleuthkit)

## Motivation
In NTFS, directories store entries for every file they contain in a special attribute, called $INDEX_ALLOCATION. These entries are called index entries, and they contain some of the file's metadata:

* File name
* File size
* Allocated size of file (size on disk)
* A set of MACB timestamps

The slack space of the $INDEX_ALLOCATION attributes may contain index entries of deleted files. Such entries may last long after the file's MFT record is lost. Finding these index entries may help you prove a file existed on a system.

## Installation 
Python 3.9 or above is required.  
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install construct.

```bash
pip install construct==2.10.67
```
Alternatively, you can use the Windows packaged release. 

## Usage Examples

```bash
# process the partition in sector 1026048, get all index entries
python INDXRipper.py -o 1026048 raw_disk.dd output.csv

# process a partition image, get all index entries
python INDXRipper.py ntfs.001 output.csv

# process the D: drive, --invalid-only mode, bodyfile output, append "D:" to all the paths
python INDXRipper.py -m D: -w bodyfile --invalid-only  \\.\D: output.bodyfile
```
### Creating a super timeline

INDXRipper is best used in combination with other tools to create a super timeline. For this purpose, the **--invalid-only** switch, the **--dedup** switch, and the bodyfile output option are particularly useful.

```bash
# fls from the sleuthkit
fls -o 128 -m C: -r image.raw > temp.bodyfile

# INDXRipper will append its output to the end of temp.bodyfile
python INDXRipper.py -o 128 -m C: -w bodyfile --invalid-only --dedup image.raw temp.bodyfile

mactime -z UTC -b temp.bodyfile > image.timeline
```

https://www.youtube.com/watch?v=0HT1uiP-BRg



#### Bodyfile output

Note that the bodyfile format is specific to The Sleuth Kit and is not fully documented. INDXRipper's bodyfile output is not entirely compatible with it.

## Features and Details

### Basic Features
* Applies fixups for index records and MFT records
* Handles $INDEX_ALLOCATION and $FILE_NAME attributes in extension records
* Full paths are reconstructed using the parent directory references from the MFT records.
* Orphan directories are listed under "/$Orphan"
* Directories with no $FILE_NAME attributes in their MFT records are listed under "/$NoName"
* Works on live Windows NTFS drives, using device paths
* All times outputted are in UTC

### Carving Method

INDXRipper scans the MFT for records of directories that have an $INDEX_ALLOCATION attribute. If it finds such a record, it searches the attribute for the directory's file reference. The index entries in the attribute should contain this file reference.

### Invalid Entries

INDXRipper will comment on invalid entries. These are the possible comments, their meanings, and some analysis tips:

* **invalid file reference**  
  This entry doesn't reference a valid MFT record.

  * If the file number and sequence number seem reasonable, The file was deleted, and its MFT record was reused.
  * If the file number is 0, or some absurdly high number - like 8589934608, it says nothing about the file. Its MFT record might or might not have been reused. The file may be deleted, or active.

* **old path**  
  This entry references a valid MFT record, but the MFT record doesn't reference the directory the entry is in as a parent directory.
  * The file has been moved from this directory to another directory. It may be deleted or active
  * If the file is deleted, it has a $ATTRIBUTE_LIST attribute, and it had a $FILE_NAME attribute in an extension record, it might or might not have been moved to another directory.



## Limitations
* The tool may give false results.
* Entries that are partially overwritten may not be found. If they are found, though, the tool may give you false information.
* The tool currently supports NTFS version 3.1 only

### What this tool doesn't do
* This tool doesn't process $INDEX_ROOT attributes.
* This tool doesn't carve $INDEX_ALLOCATION attributes from unallocated space.


## License
[MIT](https://choosealicense.com/licenses/mit/)
