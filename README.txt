DDsiggen - Tierparkzone's Forum Signature Generator
ver.0.17

A python-based program/script that takes multiple individual image
files and outputs composite images that can be used as a user signature
on web forums.

The parameters of the generated output images are designed according to
the signature requirements of the DollDreaming forum at
"https://www.dolldreaming.com/".
Depending on your settings in the software, the generated output images
may not actually fulfill the signature requirements of the DollDreaming
forum (or any other forum). Please confirm the parameters of the output
images yourself.
The author of this software is a user of the DollDreaming forum but in
no other way affiliated with DollDreaming.



How to use:

- Place the image files you wish to use in your signature into the same
  folder as this executable (.py or .exe file).

- Launch the executable.

- A terminal window will open. (Unless the executable was launched via
  terminal.)

- Shortly afterward, your browser will open a new tab displaying the
  application.
  NOTE: On first launch, you may get a firewall alert. The current
        version of this application should work without impairment,
        even if the communication request is denied.

- Follow the instructions in the browser tab to generate your signature
  images. Currently, only the "Quick Sig" functionality is available.

- Exported signature images can be found in the "signatures" subfolder.



Closing the application:

- If you use any of the "Exit Application" buttons in the browser tab,
  the terminal window will close automatically. (If the executable was
  launched from terminal, it will return to your default input prompt.)
  You may now close the browser tab.

- Closing the terminal window will terminate the application and the
  your browser tab will display a "Connection lost" message. You may
  now close the browser tab.

  NOTE: Simply closing your browser tab will not terminate the
        application! By reopening the tab (e.g. by using your browser's
        reopen recently closed tab functionality) you may continue
        where you left off. To terminate the appllication use either of
        the two methods described above.



Known issues:

- If many images are imported with the "Scan Folder" function, the
  application may appear to hang during the "Importing..." notice. In
  such a case, check the output in the terminal window: If the most
  recent message there is "Quick Import Completed!", refresh your
  browser tab. Your imported images should now be displayed.
  If the most recent message in the terminal window is "Importing...",
  the image import is just taking a lot of time. You may want to remove
  any unnecessary images from the folder of the executable to speed up
  future imports.

- The packaged (.exe) version of this software may get flagged by
  overzealous anti-virus programs. This appears to be relatively common
  among packaged python applications. If you are uncomfortable running
  the packaged version, you can directly run the script (.py) version
  instead (available on the Github page below). The script version will
  require you to have a working installation of Python, including the
  additional packages "nicegui" and "pillow". Please refer to the
  Python documentation regarding the setup of Python and any of its
  additional packages.



Copyright and License Information:

DDsiggen Copyright (c) 2025 Tierparkzone
See the LICENSE for terms and conditions for usage
and a DISCLAIMER OF ALL WARRANTIES.

The project for this software can be found at:
https://github.com/Tierparkzone/DDsiggen
