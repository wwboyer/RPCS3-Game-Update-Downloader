RPCS3 Update Downloader
=======================

This program is a simple Python script that parses RPCS3's `games.yml` file and allows the user to download updates for any games in their RPCS3 library using a simple tkinter GUI.

This program requires:
* Python 3.8 or higher (due to using the amazing walrus operator that caused no controversy and everybody loved)
* PyYAML (to parse the `games.yml` file)
* AIOHTTP (to make HTTP requests without locking up the GUI)  
  * Recommended: install AIOHTTP using `pip install aiohttp[speedups]` for faster DNS resolving and character encoding detection

The program uses an MIT License, so just give me credit if you want to do stuff with it, although quite frankly the code is so bad you probably won't want to use it anyway.

THANKS TO
=========

In addition to the aforementioned libraries and their authors and contributors, I'd like to thank:
* Jose Salvatierra of The Teclado Blog (https://blog.tecladocode.com/tkinter-scrollable-frames/) for his easy to follow demonstration of how to create a scrollable frame in Tkinter