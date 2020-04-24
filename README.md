RPCS3 Update Downloader
=======================

This program is a simple Python script that parses RPCS3's `games.yml` file and allows the user to download updates for any games in their RPCS3 library using a simple tkinter GUI.

This program requires:
* Python 3.6 or higher (to utilize f-strings for string formatting)
* PyYAML (to parse the `games.yml` file)
* AIOHTTP (to make HTTP requests without locking up the GUI)  
  * Recommended: install AIOHTTP using `pip install aiohttp[speedups]` for faster DNS resolving and character encoding detection

The program uses an MIT License, so just give me credit if you want to do stuff with it, although quite frankly the code is so bad you probably won't want to use it anyway.

I can't think of anything else to write here, so I'll probably do that later if I think of anything.