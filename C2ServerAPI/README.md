# Chivalry 2 GUI Server Moderation Panel

## **This program is only meant to work on Windows systems for now, future Linux support _might_ come someday**_, or not..._

### Setup

**This section is only of interest if you plan to work with the source files directly. If you plan to use the compiled version from the [releases page](https://github.com/Lionkjgame1219/ModerationOVALOGICIEL/releases), you can skip this part.**

Make sure to have all of the required Python libraries. Here is the list of all of pip commands, ready to paste (pip will automatically download any library that is missing) :
```
pip install a2s
pip install discord.py
pip install Pillow
pip install PyQt5
pip install pyperclip
pip install pytesseract
pip install pywin32
pip install requests
pip install windows-curses
```

If you wish to make your script a compiled executable later :
```
pip install pyinstaller
```

You will also need to manually install [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract/releases), and then add it in your system "**PATH**" variable environment.

Normally, everything should be working from there.

To run the script, you can run this command into a terminal, either using **cmd** or **powershell**, **within the "C2ServerAPI" folder**:
```
python interface.py
```

If you want to compile the script to a .exe file, here is a template command, also to be ran in your terminal, and from the same location :
```
pyinstaller --onefile --noconsole --icon=[PathToA".ico"Image] --name=[NameOfTheCompiledProgram] --add-data "core;core" --hidden-import a2s --hidden-import requests --hidden-import windows-curses --hidden-import pywin32 --hidden-import PIL --hidden-import PIL.ImageGrab --hidden-import PIL.ImageDraw --hidden-import PIL.ImageFont --hidden-import pyperclip --hidden-import PyQt5.QtWidgets --hidden-import PyQt5.QtGui --hidden-import PyQt5.QtCore --hidden-import pytesseract --hidden-import=win32gui --hidden-import=win32con --hidden-import=win32process --hidden-import=win32api --hidden-import=discord interface.py
```

### First launch

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

***Disclaimer : Due to how Chivalry 2 API is *(inexisting)*, the program is working by directly simulating keyboard pressed into your game to type commands in your console.***

***By using this method, and probably not the most optimised code for this job, the program will sort of "block" your inputs until the command processing is done.***

***It should be pretty quick (between one and 5 seconds at most), but still noticeable.***

***Sending inputs on your side (pressing keys on your keyboard) will either, do nothing, or just introduce bugs, so please let the program be done with the command processing before trying to do anything in the game.***

***A more reliable system is gonna be implemented in future releases, but for now, that's how it is.***

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

- As soon as you will open up the program, you will be prompted to add a Discord Webhook link, so that the script can send a message in the channel of your Webhook for every action you made.

  Useful for keeping a per server history of bans, allowing anyone to review the name of the person who did the action, the duration and the reason of a kick / ban, and the PlayFabID, in case you want to undo a ban.

  If you don't have a link, either create one in the server settings (for the server that will be notified), and create a Webhook in "**Server settings** -> **Integrations** -> **Webhooks** -> **New webhook**".

  Be sure to select the proper channel in which the notifications will be sent to.

  Note that it is possible to set a second Webhook link. Can be used to send the same notifications to another server, in case you want to have a discord server with a ban history shared to another clan or in-game server owner.

- Then, you will be prompted to enter your Discord ID (only if you're using Webhooks). Necessary to let the bot know that **you** did the command. Here's how to find it :

  Get into your discord window, go to "**User settings**", then scroll down to find "**Advanced**", and then, **enable** "**Developer mode*".

  With that done, get out of the settings menu, right click on your name **within any chat or server member list**, and click on the last option, which should be something like "**Copy user ID**".

  This ID is the one you need to enter.

### Once everything is done

You will now have access to the dashboard. Everything should be pretty straightforward.

- **"Admin Message"** is going to be sending an "adminsay" command, along with the text you provided.

- **"Server Message"** is basically the same as the admin one, but using the "serversay" command instead.

- **"Connected Players"** is going to open up a new window, in which you are gonna have an empty board and a button to refresh the list of all the players connected to the server you are currently playing on.

     The board is gonna be populated after the first list refresh attempt.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   This feature can, sometimes, not work at every refreshes.
   
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

  After the board is populated, you can click on a player to have access to three buttons :

   1. One for banning him, which will ask you for every informations needed for the ban.

      Required informations are :

         a - Ban duration **(in hours)**

         b - Ban reason **(e.g. "This is a duel server, FFA / RDM is prohibited.")**

   2. Another one to simply kick him. Only a reason is gonna be required, not a duration (kicking has a fixed duration of 15 or 30 minutes).

   3. The third button is gonna be a redirect link to the player's tracker profile on the website **"chivalry2stats.com"**, the most visited site for this matter. Useful to find any old username associated to the player's account.

Now, let's get back to the main dashboard.

- **"Add Time"** is just a button to add time to the map. Note that you can provide a negative value to substract time to the map.
(e.g. "-10" to substract 10 minutes)

- **"Configure Discord Webhook"** is here if need to update or remove a webhook link you provided previously. You can also add one if you never provided it.

- **"Configure Discord User ID"** is also made to add, update, or remove your Discord User ID.

- **"Light / Dark Mode"** is just here for your visual comfort, so if, for some reason, you desire to get flashbanged, all of a sudden, you are free to.

   Can also be used to enlighten your bedroom, since Chiv server mods are known to live in darkness and loneliness.

### Additional feature

For kick and ban reasons, you can use preset slots to save and load a text. 

Let's say that you want to save the sentence "This is a duel server, FFA / RDM is prohibited.".

You can type this sentence as the reason of a kick or ban, and press the button "Slot 1" in the "Save Preset" section below the prompts. You have 10 different slots available, which should be more than enough.

If you want to load a preset, then click on the slot number in the "Load Preset" section that contains the text you want to load. 

Assuming you saved the sentence used above in the slot 1, you will then want to load the preset in the slot 1 in order to retrieve the text you saved in this slot.

### Features planned for future releases

1. Toggleable automated player list refreshes (would also act as an anti-idle bot, bonus feature)

2. Presets for Admin and Server messages.

3. More robust and reliable input simulation for sending commands to the console.

4. ???