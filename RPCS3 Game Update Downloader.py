## This code is trash and will make your eyes bleed. You have been warned.

## This program requires you to install PyYAML and aiohttp (python -m pip pyyaml aiohttp[speedups])
## This program also requires Python 3.6 or higher due to using f-strings
import yaml
import asyncio
import aiohttp
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from xml.etree import ElementTree
from typing import Callable

# async_op takes in an async function and a list of arguments for said function. It then creates an Event Loop and runs the async function in a thread using said loop.
def async_op(func: Callable[[], None], args: list = []):
  loop = asyncio.new_event_loop()
  # We need to pass in the given args in addition to the actual loop, so we unpack the args list in a new tuple along with the loop. 
  threading.Thread(target=func, args=(*args, loop,)).start()

# async_download_handler takes in a URL string, a string for the save path, an integer for the size of the file in bytes, a tkinter Button, and an asyncio Event Loop.
# It then runs the async function download_update in the given Event Loop until it completes, then terminates the loop.
def async_download_handler(url: str, save_path: str, size:int, button: tk.Button, loop: asyncio.AbstractEventLoop):
  button.configure(text="Downloading...")
  loop.run_until_complete(download_update(url, save_path, size, button))
  loop.close()

def async_query_handler(loop: asyncio.AbstractEventLoop):
  loop.run_until_complete(load_game_info())
  loop.close()

async def download_update(url: str, save_path: str, size: int, button: tk.Button):
  file_name = url.split('/')[-1]
  file_path = f"{save_path}/{file_name}"

  downloading_window = tk.Toplevel()
  downloading_window.title("Downloader")

  downloading_label = tk.Label(downloading_window, text=f"Downloading {file_name}...")
  downloading_label.pack()

  downloading_progress_bar = ttk.Progressbar(downloading_window, mode="determinate", length=300, maximum=size)
  downloading_progress_bar.pack()

  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      with open(file_path, 'wb') as file:
        while True:
          chunk = await resp.content.read(2**20)
          if not chunk:
            break
          file.write(chunk)
          downloading_progress_bar.step(amount=len(chunk))
    button.configure(text="Downloaded!", state=tk.DISABLED)
  downloading_window.destroy()

async def load_game_info():
  async with aiohttp.ClientSession() as session:
    for game in game_ids:
      async with session.get(f"https://a0.ww.np.dl.playstation.net/tpl/np/{game}/{game}-ver.xml", ssl=False) as response:
        content = await response.text()
        if response.status == 404 or content == "":
          print(f"Nothing found for {game}!")
        else:
          base = ElementTree.fromstring(content)
          updates = base[0]
          updates_list = []
          for update in updates:
            updates_list.append(update.attrib)
            try:
              title = update[0][0].text
              print(f"New title: {title}")
              updates_dict[title] = updates_list
            except IndexError:
              print("IndexError thrown! No TITLE tag found, ignoring...")
          updates_list = []
  for (title, updates) in updates_dict.items():
    current_game = tk.LabelFrame(header, text=title)
    current_game.pack()
    for update in updates:
      game_version = tk.Label(current_game, text=f"Version: {update['version']}")
      game_version.pack()
      game_size = tk.Label(current_game, text=f"Update Size: {round(int(update['size']) / 2**20, 1)} MB")
      game_size.pack()
      game_sha1_sum = tk.Label(current_game, text=f"SHA1 Checksum: {update['sha1sum']}")
      game_sha1_sum.pack()
      game_system_version = tk.Label(current_game, text="Required Firmware: Version %.2f" % float(update['ps3_system_ver']))
      game_system_version.pack()
      game_download = tk.Button(current_game, text="Download Update")
      game_download.config(command=lambda url=update['url'], button=game_download, size=int(update['size']): async_op(async_download_handler, [url, save_path, size, button]))
      game_download.pack()
  loading_bar.pack_forget()
  loading_label.pack_forget()

  quit_button = tk.Button(main_frame, text="Quit", command=root.destroy)
  quit_button.pack()
      
# Initialize tkinter and set the window title
root = tk.Tk()
root.title("PS3 Game Update Downloader")

main_frame = tk.Frame(root)
main_frame.pack()

loading_label = tk.Label(main_frame, text="Loading...")
loading_label.pack()

loading_bar = ttk.Progressbar(main_frame, mode="indeterminate", length=300)
loading_bar.start()
loading_bar.pack()

header = tk.LabelFrame(main_frame, text="ebic gmaes lmaoooo")
header.pack()

file_path = filedialog.askopenfilename(title="Open Your RPCS3 'games.yml' File", filetypes=(("RPCS3 'games.yml' File", "games.yml"),))
save_path = filedialog.askdirectory(title="Select a folder to save updates in")
games = yaml.safe_load(open(file_path))
game_ids = list(games.keys())
updates_dict = {}

async_op(async_query_handler)

root.mainloop()
