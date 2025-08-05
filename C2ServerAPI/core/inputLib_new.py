"""Clean, reliable input system for Chivalry 2 console operations.
Completely refactored for reliability and layout independence."""

from time import sleep
import win32api, win32con

# Timing constants - optimized for reliability
KEY_PRESS_DURATION = 0.05      # Time between key down and key up
KEY_SEQUENCE_DELAY = 0.02      # Delay between individual key presses
COMMAND_COMPLETION_DELAY = 0.1 # Delay after typing complete command

def sendKeyPress(vk_code):
    """Send a single key press with reliable timing.
    
    @param vk_code: Virtual key code to press
    """
    print(f"[INPUT] Pressing VK 0x{vk_code:02X}")
    
    # Key down
    win32api.keybd_event(vk_code, 0, 0)
    sleep(KEY_PRESS_DURATION)
    
    # Key up  
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP)
    sleep(KEY_SEQUENCE_DELAY)

def sendShiftedKeyPress(vk_code):
    """Send a key press with shift modifier.
    
    @param vk_code: Virtual key code to press with shift
    """
    print(f"[INPUT] Pressing Shift+VK 0x{vk_code:02X}")
    
    # Shift down
    win32api.keybd_event(win32con.VK_LSHIFT, 0, 0)
    sleep(KEY_PRESS_DURATION / 2)
    
    # Key down
    win32api.keybd_event(vk_code, 0, 0)
    sleep(KEY_PRESS_DURATION)
    
    # Key up
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP)
    sleep(KEY_PRESS_DURATION / 2)
    
    # Shift up
    win32api.keybd_event(win32con.VK_LSHIFT, 0, win32con.KEYEVENTF_KEYUP)
    sleep(KEY_SEQUENCE_DELAY)

def sendCharacter(char):
    """Send a single character using layout-aware mapping.
    
    @param char: Single character to send
    """
    print(f"[INPUT] Sending character: '{char}'")
    
    try:
        # Use VkKeyScan for layout-independent character mapping
        vk_result = win32api.VkKeyScan(char)
        
        if vk_result == -1:
            print(f"[INPUT] ERROR: Character '{char}' not found on current layout")
            return False
            
        vk_code = vk_result & 0xFF
        shift_state = (vk_result >> 8) & 0xFF
        
        print(f"[INPUT] VkKeyScan result: VK=0x{vk_code:02X}, Shift={shift_state}")
        
        if shift_state & 1:  # Shift required
            sendShiftedKeyPress(vk_code)
        else:
            sendKeyPress(vk_code)
            
        return True
        
    except Exception as e:
        print(f"[INPUT] ERROR sending character '{char}': {e}")
        return False

def sendString(text):
    """Send a string of characters reliably.
    
    @param text: String to type
    """
    print(f"[INPUT] Sending string: '{text}'")
    
    success = True
    for char in text:
        if not sendCharacter(char):
            success = False
            
    # Send Enter key to execute command
    print("[INPUT] Sending Enter key")
    sendKeyPress(win32con.VK_RETURN)
    
    # Wait for command completion
    sleep(COMMAND_COMPLETION_DELAY)
    
    return success

def getConsoleKey():
    """Detect the appropriate console key for current keyboard layout."""
    try:
        layout_id = win32api.GetKeyboardLayout(0)
        lang_id = layout_id & 0xFFFF
        
        # French layouts use ²
        french_layouts = [0x040C, 0x080C, 0x0C0C, 0x100C, 0x140C, 0x180C]
        
        if lang_id in french_layouts:
            print(f"[CONSOLE] Detected French layout (0x{lang_id:04X}), using '²'")
            return '²'
        else:
            print(f"[CONSOLE] Detected layout (0x{lang_id:04X}), using '`'")
            return '`'
            
    except Exception as e:
        print(f"[CONSOLE] Layout detection failed: {e}, using '`'")
        return '`'

def sendConsoleKey():
    """Send the appropriate console key for current layout."""
    console_char = getConsoleKey()
    print(f"[CONSOLE] Sending console key: '{console_char}'")
    return sendCharacter(console_char)

# Legacy compatibility functions (deprecated - use new functions above)
def sendLetterPress(letter):
    """Legacy function - use sendCharacter() instead."""
    return sendCharacter(letter)

def typeString(string):
    """Legacy function - use sendString() instead.""" 
    return sendString(string)
