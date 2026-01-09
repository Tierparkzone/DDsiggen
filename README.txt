DDsiggen - Tierparkzone's Forum Signature Generator
ver.2.08

A python-based program/script that takes multiple individual image files and text inputs to create composite images for use as a signature on web forums. The generated output images by default are set up to meet the signature requirements of the DollDreaming forum at "https://www.dolldreaming.com/". Depending on your settings in the software, the generated output images may not actually fulfill the signature requirements of the DollDreaming forum (or any other forum). Please confirm the properties of the output images yourself before using them as signatures.
The author of this software is a user of the DollDreaming forum but in no other way affiliated with DollDreaming.

NOTE: To avoid confusion between input and output images, from here on, this readme and the program itself will refer to input images as "photos" and output images as "signature images". Regardless of this naming, you can use any type of image as the input and are not limited to photos.



Features:

Two modes are currently available.

Quick Sig:
Generate a signature from multiple photos with only a few clicks.
- Batch import photos from the working directory and reorder them
- Arrange photos into one or two signature images, while keeping their size as large as possible
- Select one of the provided alpha masks
- Export the final signature image(s)

Create new:
Generate a signature with custom text and additional options.
- Set the preferred aspect ratio for your photos
- Batch import photos from the working directory
- Import photos one by one from anywhere on your computer or from the web
- Batch import photos from your DollDreaming doll directory
- Manually adjust the crop for individual photos or for groups of photos at once
- Add or import up to two text layers ("name" and "epithet") that will get applied to the photos
- Reorder photos and text as desired
- Select one of the provided alpha masks
- Customize text font, colors and positions for each text layer (you can also use your own font files)
- Apply shadow and/or glow effects to the text layers
- Choose how the photos will be arranged in the signature image(s) or leave it to the program
- Export the final signature image(s) in multiple resolutions



Package contents:

The packaged program will provide the below file structure.

DDsiggen_<version No.>_<OS type>        (Working directory)
|
|--fonts                    (Place any font files you wish to use in here)
|  |
|  |--851CHIKARA-DZUYOKU_kanaA_004.ttf
|  |
|  |--851CHIKARA-YOWAKU_002.ttf
|  |
|  |--851Gkktt_005.ttf
|  |
|  |--851H-kktt_004.ttf
|  |
|  |--GenEiPOPle-Bk.ttf
|  |
|  |--HachiMaruPop-Regular.ttf
|
|--signatures               (Exported signature images will appear in here)
|  |
|  |--<empty>
|
|--DDsiggen_<version No.><file type>    (The executable itself - File type is .py, .exe  or none)
|
|--doll_directory.txt       (Enter the links to your doll directory entries here)
|
|--epithets.txt             (Text you enter here can be applied to the "epithet" text layer of a photo)
|
|--LICENSE.txt              (License information)
|
|--names.txt                (Text you enter here can be applied to the "name" text layer of a photo)
|
|--README.txt               (This readme file)



How to use:

Preparing photos for batch import:
- Copy any photo files that you wish to use in your signature into the working directory (the same folder as this executable).
- Supported file formats are .jpg, .jpeg, .png, .JPG, .JPEG and .PNG.
- If you skip this step, you will only be able to import images one by one through the "Add photo" buttons in the "Create New" mode.

Preparing doll directory links for import:
- Copy the links to your dolls' doll directory entries into the "doll_directory.txt" file.
- Paste each link on a new line.
- If you skip this step, you will not be able to use the "Directory Import" function
- The directory import is comparatively slow. If you have your photos available locally, the batch import described above will be substantially faster.

Preparing custom text for import:
- Enter the text you wish to import into the "names.txt" and "epithets.txt" files. The contents of these files can then be applied to their respective text layers.
- Each new line in the text file will be applied to the next photo.
- Save the text files in Unicode (UTF-8) format if possible.
- If you skip this step, you will have to enter all text manually inside the program.

Preparing custom fonts:
- The packaged program alredy provides a few default fonts inside the "fonts" subfolder.
- Users are free to copy any of their own font files into the "fonts" subfolder, to use inside the program.
- Supported file formats are .ttf, .otf, .TTF and .OTF.
- If you would like to use non-alphanumeric scripts in your signature (e.g. Chinese, Japanese, Korean), please provide a font that supports that script.
- The default fonts packaged with this program mostly support Japanese script, but may lack some special Kanji.
- If the generated text appears garbled or as rectangles inside the program, the selected font does not support the script of the current text. Select a different font.

Running the executable/script:
- The packaged executable (.exe on Windows, no file extension on Linux) can be launched via double click, right click -> Run, or right click -> Run in terminal.
- The bare python script is best run from terminal with $<your python environment> DDsiggen.py
- First execution of the packaged executable on Windows will likely trigger SmartScreen, since the program is not digitally signed. Select "More information -> Run anyway" to start the program.
- A terminal window will open. (Unless the executable/script was already launched via terminal.)
- Shortly afterward, your browser will open a new tab displaying the program's UI.
- On first launch, you may get a firewall alert. Denying the communication request will at most impact your ability to import images from the web. Everything else will function regardless.
- Select either "Quick Sig" or "Create New" and follow the instructions in the program to generate your signature images.
- Exported signature images will be placed into the "signatures" subfolder.
- Newly exported signature images may overwrite older ones. Copy and/or rename older signature images that you wish to keep.

Exiting the program:
- If you use any of the "Exit Application" buttons in program's UI, the terminal window will close automatically. (If the executable/script was launched from terminal, it will return to your default input prompt.) You may now close the browser tab.
- Closing the terminal window will terminate the program and your browser tab will eventually display a "Connection lost" message. You may now close the browser tab.
- Simply closing your browser tab will not terminate the program! (By reopening the tab, you may continue where you left off.) Close the terminal window to fully terminate the program.
- If you terminate the program in any other way than using the "Exit Application" buttons in the program's UI, some temporary files may remain in a "tmp" subfolder inside the working directory. These will get overwritten/cleared the next time you run the program.

Running/packing the Python script:
- The packing command for PyInstaller / NiceGUI-pack can be found at the bottom of the "DDsiggen.py" script file.
- Before packing, comment/uncomment the lines in the script that are marked as such.
- Simply running the script should not require commenting/uncommenting any lines.
- To run the script, you will require the Python packages nicegui, pillow and requests.
- To pack the script you will also require the Python package pyinstaller.
- If you encounter any issues when running or packing the script, try again with the Python and package versions listed below.
- The script is known to work with:
   Python        3.13.7
   nicegui       2.24.2
   pillow        11.3.0
   requests      2.23.5
   pyinstaller   6.16.0



Known issues:

Original transparency of photos is discarded:
If any of the imported photos are PNGs with transparent areas, their original transparency information will be ignored during signature generation. Instead the transparency of the selected alpha mask is applied.

Text outline may appear garbled or spotty:
Some combinations of font, font size and outline thickness may cause the outline of text to appear garbled or have holes. This may be caused by the font file itself or by how Pillow draws text outlines. Try some different text/outline setting combinations.



Copyright and License Information:

DDsiggen Copyright (c) 2025-2026 Tierparkzone
See the LICENSE for terms and conditions for usage and a DISCLAIMER OF ALL WARRANTIES.

The project for this software can be found at:
https://github.com/Tierparkzone/DDsiggen



Special thanks for testing and feedback:
ragnamuffin
Amapola
PolitelyNefarious
313C7
