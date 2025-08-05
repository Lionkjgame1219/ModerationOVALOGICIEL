"""Provides a class encapsulating a chivalry 2 instance"""

from PIL import ImageGrab, Image, ImageDraw, ImageFont
import pytesseract
import win32gui, win32con, win32process, win32api
from time import sleep
from . import inputLib

class Chivalry:
    """Class representing a running instance of the Chivalry 2 game.

    This class provides numerous methods for interacting with the Chivalry 2 game programatically.
        Functionality is implemented using a combination of OCR and windows input emulation. Using
        this class may cause difficulties using the computer for anything other than chivalry, and may even
        make it difficult for the user to close it depending on how it's used. USE WITH CAUTION!
    """
    def __init__(self):
        if self.getChivalryWindowHandle() == 0:
            raise RuntimeError("The Chivalry 2 window could not be found. Ensure that chivalry 2 is running\
                               on this machine.")


    __windowHandle = -1
    def getChivalryWindowHandle(self):
        """Obtains and returns the win32 window handle of a chivalry 2 process running on this computer.
        
        This function will only make the associated syscalls once. After that, the cached window handle from the
            first call will be returned instead, regardless of it's validity.
        """
        if self.__windowHandle != -1:
            return self.__windowHandle
        else:
            hwnd = win32gui.FindWindow(None, "Chivalry 2  ") #note the spaces after the 2 here. They're important.
            self.__windowHandle = hwnd
            sleep(0.1) #window handle doesn't seem to be valid until after a warmup period
            return hwnd

    def getFocus(self, hwnd):
        """Give the chivalry 2 window user focus. This visually brings the window in front of all other windows and
            directs user input to it. This is a precondition to many interactions with the chivalry 2 process, especially
            ocr-related operations. Most functions that internally require this will call it themselves unless stated
            otherwise.
        """
        remote_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        win32process.AttachThreadInput(win32api.GetCurrentThreadId(), remote_thread, True)
        prev_handle = win32gui.SetFocus(hwnd)
        # Also bring window to foreground to ensure it receives input
        win32gui.SetForegroundWindow(hwnd)

    def checkInGameConsoleOpen(self):
        """Returns true or false, indicating if the in-game console is currently open in extended mode.

        TODO: NOTE: this function currenly does not work.
        """
        screenshot = self.getChivScreenshot() #get a screenshot of the chiv game
        width, height = screenshot.size
        screenshot = screenshot.crop((0, height*(47/64)+2, width*0.02, height*(49/64)-2))
        #process to isolate console text, and convert back to RGB
        #TODO: also try to make mode="L" work
        screenshot = screenshot.quantize(colors=256).convert(mode="1").convert(mode="RGB")
        screenshot.show() #DEBUG
        print(pytesseract.image_to_string(screenshot))
        
    def getChivScreenshot(self, tabDown=False):
        """Returns a PIL image of the entire chivalry 2 window, as it appears on-screen to a human user.
        """
        hwnd = self.getChivalryWindowHandle()
        self.getFocus(hwnd)
        #win32gui.SetForegroundWindow(hwnd)
        sleep(0.1)
        if tabDown:
            inputLib.tabDown()
            sleep(0.1)
        
        windowRect = win32gui.GetWindowRect(hwnd)
        #clientRect = win32gui.GetClientRect(hwnd)
        #print(windowRect)
        #print(clientRect)
        image = ImageGrab.grab(windowRect)
        if tabDown:
            inputLib.tabUp()
            sleep(0.1)

        return image

    #precondition: the extended view of the console is open in chivalry
    def getConsoleOutput(self):
        """Returns the currently displayed output of the chivalry console window as a string using OCR.

        PRECONDITIONS:
            The chivalry console must be opened and visible in extended mode in the chivalry 2 process. See
                the checkInGameConsoleOpen(), openConsole() and closeConsole() functions.
        """
        screenshot = self.getChivScreenshot() #get a screenshot of the chiv game
        #get screenshot dimensions
        width, height = screenshot.size
        #crop to console only. 
        #height*(47/64)-2 is a magic number measured empirically.
        #It gets everything up to the horizontal line separating the command line input
        screenshot = screenshot.crop((0, 0, width, height*(47/64)-2))
        #process to isolate console text, and convert back to RGB
        #TODO: also try to make mode="L" work
        screenshot = screenshot.quantize(colors=256).convert(mode="1").convert(mode="RGB")
        #screenshot.show() #DEBUG
        #TODO: improve recognition with custom training
        #https://ironsoftware.com/csharp/ocr/how-to/ocr-custom-font-training/
        text = pytesseract.image_to_string(screenshot)
        #strip empty lines and return them
        return [s for s in text.splitlines() if s]

    def getTimeRemaining(self):
        """Return the time remaining in the game as a string, as displayed in the in-game timer.

        This function internally uses OCR, and does not do cleanup on the string returned. It is the
            responsibility of the caller to ensure that this string is valid, clean, and interpretable
            before using it.

        TODO: add cleanup here?

        NOTE: The in-game console should not be open in extended mode when this function is called.
            It may still work, however, it will be less reliable.
        """
        #get screenshot
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of timer on screen
        screenshot = screenshot.crop((0.45*width, 0.08*height, 0.55*width, 0.13*height))
        
        #process and isolate text

        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")
        return pytesseract.image_to_string(screenshot)
    
    def getPlayerCount(self):
        return 0
        #this will eventually return an actual number from the game...
        #the OCR for this is surprisingly difficult
        screenshot = self.getChivScreenshot(tabDown=True)
        width, height = screenshot.size
        
        #crop to location of timer on screen
        screenshot = screenshot.crop((0.47*width, height*0.18, 0.53*width, height*0.22))

        #process and isolate text
        
        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")

        

        screenshot.show()
        return pytesseract.image_to_string(screenshot)
    def getPlayerList(self):
        screenshot = self.getChivScreenshot(tabDown=True)
        width, height = screenshot.size
        
        # Hypothèse : la liste des joueurs est affichée en haut à droite
        # Ajuste ces valeurs en fonction de ta capture d'écran
        left = int(width * 0.75)
        top = int(height * 0.15)
        right = int(width * 0.95)
        bottom = int(height * 0.70)
        
        player_list_img = screenshot.crop((left, top, right, bottom))
        
        # Pré-traitement : augmenter contraste, binariser, etc.
        player_list_img = player_list_img.convert("L")  # niveaux de gris
        player_list_img = player_list_img.point(lambda x: 0 if x < 128 else 255, '1')  # binarisation
        
        # player_list_img.show()  # pour debug
        
        # OCR
        text = pytesseract.image_to_string(player_list_img)
        
        # Nettoyage du texte et découpage en lignes
        lines = text.splitlines()
        players = [line.strip() for line in lines if line.strip() != ""]
        
        return players

    def isGameEnd(self):
        """Returns true or false, indicating whether or not the game is currently in a game-end state.

        PRECONDITION: The game client is in spectator mode

        NOTE: The UI elements used to detect this are the "GAME END" and "VICTOR" in-game overlays.
            These assume that the client is in spectator mode at game end to get these specific messages.
        """
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of game end notification on screen
        screenshot = screenshot.crop((0.3*width, 0.75*height, 0.7*width, 0.9*height))

        screenshot = screenshot.quantize(colors=128).convert(mode="1").convert(mode="RGB")
        #screenshot.show()
        result = pytesseract.image_to_string(screenshot)
        if "GAME END" in result or "VICTOR" in result:
            return True
        else:
            return False
        
    def isMainMenu(self):
        """Returns true or false, indicating if the client is currently at the chivalry main menu.
        """
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of exit game button on main menu on screen
        screenshot = screenshot.crop((0.072*width, 0.94*height, 0.13*width, 0.97*height))

        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")
        #screenshot.show()
        result = pytesseract.image_to_string(screenshot)
        #print(result)
        if "EXIT GAME" in result:
            return True
        else:
            return False

    def getRecentCommandOutput(self, command, lines):
        """Returns the output of a command that was recently run.

        PRECONDITION: the extended view of the console is open in chivalry

        @param command: A string containing the command that was run, exactly as it was entered
        @param lines: How many lines of it's output to return. (this depends on the specific command)
        @returns The output of the run command as a string, or None
        """
        console = self.getConsoleOutput()
        #get a view of the console containing only command run lines and no spaces what-so-ever
        #command run lines take the form `>>> command <<<` in the output. We strip spaces because
        #we can't rely on them being detected by OCR. We also cant rely on ALL of the >>> / <<< characters to
        #be correctly OCR'd. Here, we rely on at least two consecutive of both
        #StrippedConsole elements include their index in the actual console output array
        strippedConsole = [
            (index, s.replace(" ", "")) 
            for index,s in enumerate(console) 
            if ">>" in s and "<<" in s
        ]
        index = -1 #sentinel -1 value
        for i, s in reversed(strippedConsole): #searching backwards through all commands run
            if command.replace(" ", "") in s: #if this line is the running of the requested command
                if i < len(console)-1: #if this is not the last line of the console output
                    n = lines+1
                    #return some number of lines, n, output after the command run, or the rest of the
                    #output of the console if there are less than n lines left
                    #this is more general than it needs to be, but this is intended to
                    return console[i+1:i+n] if i+n < len(console) else console[i+1:]
                else:
                    return None
        return None

    def consoleSend(self, message):
        """Send a command to the chivalry console.

        @param message: Command string to send to console
        """
        hwnd = self.getChivalryWindowHandle()
        print(f"[CONSOLESEND] Game window handle: {hwnd}")
        self.getFocus(hwnd)

        # Wait for game to be ready for input after focus
        sleep(0.3)

        print(f"[CONSOLESEND] Sending command: '{message}'")
        success = inputLib.sendString(message)

        if success:
            print("[CONSOLESEND] Command sent successfully")
        else:
            print("[CONSOLESEND] ERROR: Command sending failed")

    def openConsole(self):
        """Open the chivalry console into extended mode.

        PRECONDITION: The chivalry console is currently closed
        """
        print("[OPENCONSOLE] Opening console...")
        hwnd = self.getChivalryWindowHandle()
        print(f"[OPENCONSOLE] Game window handle: {hwnd}")
        self.getFocus(hwnd)

        # Wait for game to be ready for input after focus
        sleep(1.0)

        print("[OPENCONSOLE] Sending console key...")
        success = inputLib.sendConsoleKey()

        if success:
            print("[OPENCONSOLE] Console opened successfully")
            sleep(0.2)  # Brief wait for console to be ready
        else:
            print("[OPENCONSOLE] ERROR: Console opening failed")

    # closeConsole() removed - console auto-closes after Enter

    # def walk(self):
    #     """Cause the chivalry client to walk forward in-game for several seconds.

    #     NOTE: this function shouldn't really be called, and is mostly here for testing inputs.
    #         It MAY be useful for tinkering with OCR by moving to a more oportune position.
        
    #     """
    #     hwnd = self.getChivalryWindowHandle()
    #     self.getFocus(hwnd)
    #     win32api.keybd_event(0x57, 0x0, 0)
    #     sleep(4)
    #     win32api.keybd_event(0x57, 0x0, 0x0002)

    def SavePreset(self, slot, reason_text):
        """Save the kick/ban reason sentence to a preset slot.

        @param slot: The slot to save to. This is a number between 0 and 9.
        @param reason_text: The reason text to save to the preset slot.
        """
        import os

        localconfig = "localconfig"

        # Read existing config
        webhook_primary = "None"
        webhook_secondary = "None"
        discord_user_id = "None"
        presets = {}

        if os.path.exists(localconfig):
            try:
                with open(localconfig, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 1:
                        webhook_primary = lines[0]
                    if len(lines) >= 2:
                        webhook_secondary = lines[1]
                    if len(lines) >= 3:
                        discord_user_id = lines[2]
                    # Load existing presets from line 4 onwards
                    if len(lines) >= 4:
                        for i, line in enumerate(lines[3:]):
                            if line.strip():
                                presets[str(i)] = line
            except Exception:
                pass

        # Update the preset
        presets[str(slot)] = reason_text

        # Write back to file
        try:
            with open(localconfig, 'w', encoding='utf-8') as f:
                f.write(f"{webhook_primary}\n")
                f.write(f"{webhook_secondary}\n")
                f.write(f"{discord_user_id}\n")
                # Write presets (slots 0-9)
                for i in range(10):
                    preset_text = presets.get(str(i), "")
                    f.write(f"{preset_text}\n")
            return True
        except Exception:
            return False

    def LoadPreset(self, slot):
        """Load the kick/ban reason sentence from a preset slot.

        @param slot: The slot to load from. This is a number between 0 and 9.
        @returns: The reason text from the preset slot, or None if not found.
        """
        import os

        localconfig = "localconfig"

        if not os.path.exists(localconfig):
            return None

        try:
            with open(localconfig, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                # Presets start from line 4 (index 3)
                preset_line_index = 3 + slot
                if len(lines) > preset_line_index and lines[preset_line_index].strip():
                    return lines[preset_line_index]
                return None
        except Exception:
            return None

    def GetAllPresets(self):
        """Get all saved presets as a dictionary.

        @returns: Dictionary with slot numbers as keys and reason texts as values.
        """
        import os

        localconfig = "localconfig"
        presets = {}

        if not os.path.exists(localconfig):
            return presets

        try:
            with open(localconfig, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                # Presets start from line 4 (index 3)
                for i in range(10):
                    preset_line_index = 3 + i
                    if len(lines) > preset_line_index and lines[preset_line_index].strip():
                        presets[str(i)] = lines[preset_line_index]
        except Exception:
            pass

        return presets

#Chiv win32gui window class: "UnrealWindow"