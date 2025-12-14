# 🔍 Duplicate File Finder

A Python application with a graphical interface for identifying and deleting duplicate files on your computer or external drives.

## 📥 Quick Download

**[⬇️ Download Application for Immediate Use](https://drive.google.com/file/d/1Yn7oB7ABQNgMY7VTPKSa3uWCyRp6qJcz/view?usp=drive_link)**

Click the link above to download the ready-to-use application. No installation required!

## ✨ Features

- ✅ **Free Folder Selection** - Any folder on your computer or external drive
- ✅ **Identical File Detection** - Using Hash (MD5) - 100% accuracy
- ✅ **Similar Names Detection** - Find files with similar names (image_1.jpg, image 1.jpg)
- ✅ **Stop Scan Anytime** - Stop button to halt scanning mid-process
- ✅ **Auto Delete Duplicates** - One-click automatic deletion of all identical files (keeps one copy)
- ✅ **User-Friendly Interface** - Modern design with large checkboxes (Hebrew RTL support)
- ✅ **Safe Deletion** - Manual file selection + confirmation
- ✅ **Recursive Scanning** - Scans subfolders as well
- ✅ **Group Display** - Shows duplicate files in organized cards
- ✅ **Folder Navigation** - Button to open file location

## 🚀 How to Use?

### Using the Executable (Recommended)

**No installation required!** Just download and run:

1. Download `SHOSHI_Duplicate_Finder.exe` from the `dist/` folder
2. Double-click to run
3. No Python or additional software needed

### Running from Source

1. Ensure Python is installed (version 3.7+)
2. Download `duplicate_finder.py`
3. Run:
```bash
python duplicate_finder.py
```

**No additional libraries needed!** Everything is built into Python.

### Usage Instructions

1. **Select Folder** - Click "Select Folder" and choose the folder to scan
2. **Choose Options**:
   - ✓ Identify identical files (Hash) - Always recommended
   - ✓ Identify similar names - Useful for finding nearly identical names
   - Set minimum similarity percentage (85% recommended)
3. **Click "Start Scan"** - The system will start scanning (Click ⏹ Stop to halt anytime)
4. **Select Files to Delete** - Mark the files you want to delete (large checkboxes)
5. **Delete Options**:
   - **Delete Selected** - Delete only the files you marked
   - **Delete All Duplicates** - Auto-delete all identical files (keeps one from each group)

## 🔧 Technologies

- **Python 3.12+**
- **tkinter** - Graphical interface
- **hashlib** - File hash calculation
- **difflib** - Name similarity comparison
- **threading** - Background scanning
- **PyInstaller** - Executable packaging

## 📊 Performance

- **Small files** (< 1GB): Very fast
- **Large files** (> 1GB): May take time to calculate hash
- **Optimized**: Processes up to 100 groups, limits name matching to 1000 files
- **Recommendation**: Start with a small folder for testing

## ⚠️ Important Warnings

- ⚠️ **Permanent Deletion** - Files are deleted permanently (not to recycle bin)
- ⚠️ **Backup Important Data** - Before first use
- ⚠️ **Check Before Deleting** - Make sure you're selecting the correct files

## 🎯 Use Cases

### Case 1: Duplicate Photos
Have a photo folder with copies? The app will find all identical images.

### Case 2: Music Files
Songs downloaded twice? The app will identify them by hash or name.

### Case 3: Documents
document_final.docx, document_final_1.docx - The app will find similar names.

More advanced interface - `PyQt5`

## 📦 Building the Executable

To build the standalone EXE file with the custom icon:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "SHOSHI_Duplicate_Finder" --icon="icon.png" duplicate_finder.py --clean
```

The executable will be created in the `dist/` folder.

## 💡 Tips

1. **Start with a small folder** - To get familiar with the tool
2. **Use both modes** - Hash + similar names together
3. **Open folders** - Use the 📁 button to view the file before deletion
4. **Backup before mass deletion** - Especially if you're not sure

---

**Created with ❤️ in israel**
