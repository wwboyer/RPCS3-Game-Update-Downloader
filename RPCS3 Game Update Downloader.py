## This code is trash and will make your eyes bleed. You have been warned.

## This program requires you to install PyYAML and aiohttp (python -m pip pyyaml aiohttp[speedups])
## This program also requires Python 3.8 or higher due to using the walrus operator
import yaml
import asyncio
import aiohttp
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from xml.etree import ElementTree
from typing import Callable

## CONSTANTS
# Declare a constant for 1MiB, which is 2^20
ONE_MEBIBYTE = 2**20

## FUNCTIONS
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

# async_query_handler takes in an asyncio Event Loop. It then runs the async function load_game_info in the given Event loop until it completes, then terminates the loop.
def async_query_handler(loop: asyncio.AbstractEventLoop):
  loop.run_until_complete(load_game_info())
  loop.close()

# download_update is an async function that takes in a URL string, a string for the save path, an integer for the size of the file in bytes, and a tkinter Button.
# It then downloads the file specified by the URL to the specified save path and shows the progress of the download in a popup window.
async def download_update(url: str, save_path: str, size: int, button: tk.Button):
  # Splitting the given URL by the '/' character and taking the last string in the resulting array gives the name of the file on the server.
  # E.g., "playstation.com/files/example.pkg".split('/')[-1] results in the string "example.pkg".
  file_name = url.split('/')[-1]
  file_path = f"{save_path}/{file_name}"

  # Create a tkinter Toplevel window and give it a (kind of) descriptive title.
  downloading_window = tk.Toplevel()
  downloading_window.title("Downloader")

  # Create a tkinter Label, place it in downloading_window, and set the Label's text to inform the user that it's downloading the specified file.
  downloading_label = tk.Label(downloading_window, text=f"Downloading {file_name}...")
  downloading_label.pack()

  # Create a tkinter Progressbar, place it in downloading_window, and set the bar to be 100% full when the bar's amount is equal to the size of the specified file in bytes.
  downloading_progress_bar = ttk.Progressbar(downloading_window, mode="determinate", length=300, maximum=size)
  downloading_progress_bar.pack()

  # N.B.: As far as I know, the documentation for aiohttp discourages creating multiple ClientSessions in one project, preferring that users simply reuse one session throughout.
  # I don't do this, and I personally haven't had any issues in doing this, but I wanted to state this in case someone wanted to use this as an example of using aiohttp.
  # While I personally have had zero issues, you technically shouldn't do this as it's not best practice for this library.
  # Granted, you probably shouldn't be using this dumpster fire as an example of anything other than bad code.

  # Open an aiohttp ClientSession as session and:
  async with aiohttp.ClientSession() as session:
    # Get the contents of the given URL as resp and:
    async with session.get(url) as resp:
      # Create the file at file_path if it doesn't exist and open it as writeable binary with the name file and:
      with open(file_path, 'wb') as file:
        # While chunk is assigned to a truthy value:
        while (chunk := await resp.content.read(ONE_MEBIBYTE)):
          # Write the current chunk to file.
          file.write(chunk)
          # Increment the progress bar by the length of the current chunk (usually 1MiB unless near the end of file)
          downloading_progress_bar.step(amount=len(chunk))
    # Change the text of the tkinter Button and set its state to disabled
    button.configure(text="Downloaded!", state=tk.DISABLED)
  # Destroy the downloading window.
  downloading_window.destroy()

# load_game_info is an async function that takes in no arguments. It then retrieves any available updates for the titles specified in the "games.yml" file and shows the user a list of all available updates along with the option to download said updates.
async def load_game_info():
  # Tkinter doesn't have an easy way to make a scrollable frame and I didn't want to add another dependency for something so trivial.
  # After a bit of googling, I found an article by Jose Salvatierra (https://blog.tecladocode.com/tkinter-scrollable-frames/) that accomplishes exactly what I need.

  # Create a Tkinter frame that will act as a container for our canvas and scrollbar (hence the name 'container')
  container = tk.Frame(main_frame)
  # Create a Tkinter canvas that will contain the frame we want to be scrollable. While Tkinter frames cannot be scrollable, Tkinter canvases can.
  canvas = tk.Canvas(container)
  # Create a Tkinter scrollbar to scroll our canvas.
  scrollbar = tk.Scrollbar(container, command=canvas.yview)
  # Finally, create the Tkinter frame we want to be scrollable.
  header = tk.Frame(canvas)

  # Open an aiohttp ClientSession as session and:
  async with aiohttp.ClientSession() as session:
    # For each game in the games.yml file:
    for game in game_ids:
      # We need to specify no SSL because the PS3 update server uses a self-signed certificate.
      # I'm sure an actual PS3 has no issue with that, but aiohttp (and any remotely modern web browser) definitely does.
      # Get the contents of the specified URL as response and:
      async with session.get(f"https://a0.ww.np.dl.playstation.net/tpl/np/{game}/{game}-ver.xml", ssl=False) as response:
        # Check the text of the response.
        # This is important because a game with no updates will sometimes return a 200 code with zero text, while other games with no updates return a 404 error code.
        content = await response.text()
        # Inform the user no content was found for the specified game if the page 404s or has no content.
        if response.status == 404 or content == "":
          print(f"Nothing found for {game}!")
        else:
          # Convert the XML into a manipulable data structure using ElementTree
          base = ElementTree.fromstring(content)
          # Set updates to the list of updates
          updates = base[0]
          # Set updates_list to an empty list
          updates_list = []
          # For each update:
          for update in updates:
            # Add the current game to updates_list
            updates_list.append(update.attrib)
            try:
              # Set the title of the game. This will only work for the last listed update for a given title. All other updates for a given title will throw an IndexError because the TITLE attribute will not exist.
              title = update[0][0].text
              # Inform the user a new title was found.
              print(f"New title: {title}")
              # Add the title to updates_dict
              updates_dict[title] = updates_list
            except IndexError:
              # Inform the user that an IndexError was thrown and why it was thrown.
              print("IndexError thrown! No TITLE tag found, ignoring...")
          # Set updates_list back to an empty list
          # There is likely a much neater way to do this, but I'm bad at coding.
          updates_list = []
  # For a given title and its updates in updates_dict:
  for (title, updates) in updates_dict.items():
    # Create a Tkinter LabelFrame, set its parent to header, and set its title to the title of the current game.
    current_game = tk.LabelFrame(header, text=title)
    current_game.pack()
    # For each update for a given game:
    for update in updates:
      # Create a Tkinter Label and set its text to show the version of the update file.
      game_version = tk.Label(current_game, text=f"Version: {update['version']}")
      game_version.pack()
      # Create a Tkinter Label and set its text to show the size of the update file in MiB rounded to 1 decimal place.
      game_size = tk.Label(current_game, text=f"Update Size: {round(int(update['size']) / ONE_MEBIBYTE, 1)} MiB")
      game_size.pack()
      # Create a Tkinter Label and set its text to show the SHA1 Checksum of the update file.
      game_sha1_sum = tk.Label(current_game, text=f"SHA1 Checksum: {update['sha1sum']}")
      game_sha1_sum.pack()
      # Create a Tkinter Label and set its text to show the PS3 firmware version required by the update.
      game_system_version = tk.Label(current_game, text="Required Firmware: Version %.2f" % float(update.get('ps3_system_ver', 0) ))
      game_system_version.pack()
      # Create a Tkinter Button that will download the update to the previously specified save path on click.
      game_download = tk.Button(current_game, text="Download Update")
      # Set the Button's command to download the specified game update using the async_download_handler function.
      # The reason this looks like such a mess is because:
      # 1. I am bad at coding.
      # 2. Since Tkinter doesn't neatly support multi-threaded tasks, the download bar would not show any progress unless I specifically create a new asyncio Event Loop to run the download task asynchronously.
      game_download.config(command=lambda url=update['url'], button=game_download, size=int(update['size']): async_op(async_download_handler, [url, save_path, size, button]))
      game_download.pack()
  # Make the loading bar and label invisible since they are no longer needed.
  loading_bar.pack_forget()
  loading_label.pack_forget()

  # Change the size of canvas whenever header changes size (i.e. whenever we add a widget).
  header.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
  # Draw header starting at the top-left corner of canvas.
  canvas.create_window((0, 0), window=header, anchor=tk.NW)
  # Allow the scrollbar to actually scroll the canvas.
  canvas.configure(yscrollcommand=scrollbar.set)
  # Allow the user to scroll the list using their mouse's scroll wheel.
  canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/120), "units"))
  canvas.bind("<Configure>", lambda e: canvas.scale("all", 0, 0, e.width, e.height))

  # Set the container, canvas, and scrollbar to be visible.
  container.pack(fill=tk.BOTH, expand=True)
  canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
  scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Initialize tkinter and set the window title.
root = tk.Tk()
root.title("PS3 Game Update Downloader")

# Create a Tkinter Frame to act as our primary frame for all widgets.
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create a Tkinter Label to fill space while the program is retrieving updates.
loading_label = tk.Label(main_frame, text="Loading...")
loading_label.pack()

# Create an indeterminate Tkinter Progressbar to show the user that the program is retrieving updates and not frozen.
loading_bar = ttk.Progressbar(main_frame, mode="indeterminate", length=300)
loading_bar.start()
loading_bar.pack()

# Prompt the user to find their RPCS3 'games.yml' file.
file_path = filedialog.askopenfilename(title="Open Your RPCS3 'games.yml' File", filetypes=(("RPCS3 'games.yml' File", "games.yml"),))
# Prompt the user to select a folder to save their PS3 game updates in.
save_path = filedialog.askdirectory(title="Select a folder to save updates in")
# Load 'games.yml' at the specified path using PyYAML's safe_load function.
games = yaml.safe_load(open(file_path))
# Set game_ids to a list of the game IDs present in 'games.yml'
game_ids = list(games.keys())
# Set updates_dict to an empty dictionary
updates_dict = {}

# Asynchronously retrieve the PS3 game updates.
# As before, we need to do this because Tkinter likes to do things synchronously, which causes our loading bar to freeze.
async_op(async_query_handler)

root.mainloop()
