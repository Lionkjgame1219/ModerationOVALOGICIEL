#!/usr/bin/env python3
"""
Test script for reason preset functionality
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.guiServer import Chivalry

def test_preset_functionality():
    """Test the preset save/load functionality"""
    print("Testing reason preset functionality...")
    
    # Create Chivalry instance
    try:
        chiv = Chivalry()
        print("✅ Chivalry instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create Chivalry instance: {e}")
        print("Note: This is expected if Chivalry 2 is not running")
        # Create a mock instance for testing presets only
        chiv = MockChivalry()
        print("✅ Using mock Chivalry instance for preset testing")
    
    # Test data
    test_presets = {
        0: "Cheating/Hacking",
        1: "Toxic behavior",
        2: "Team killing",
        3: "Griefing",
        4: "Inappropriate language",
        5: "Exploiting bugs",
        6: "Spamming chat",
        7: "Disruptive gameplay",
        8: "Harassment",
        9: "Rule violation"
    }
    
    print("\n📝 Testing preset saving...")
    for slot, reason in test_presets.items():
        success = chiv.SavePreset(slot, reason)
        if success:
            print(f"✅ Saved preset {slot}: '{reason}'")
        else:
            print(f"❌ Failed to save preset {slot}")
    
    print("\n📖 Testing preset loading...")
    for slot in range(10):
        loaded_reason = chiv.LoadPreset(slot)
        expected_reason = test_presets.get(slot)
        if loaded_reason == expected_reason:
            print(f"✅ Loaded preset {slot}: '{loaded_reason}'")
        else:
            print(f"❌ Preset {slot} mismatch. Expected: '{expected_reason}', Got: '{loaded_reason}'")
    
    print("\n📋 Testing GetAllPresets...")
    all_presets = chiv.GetAllPresets()
    print(f"All presets: {all_presets}")
    
    # Test loading non-existent preset
    print("\n🔍 Testing non-existent preset...")
    non_existent = chiv.LoadPreset(99)
    if non_existent is None:
        print("✅ Non-existent preset correctly returns None")
    else:
        print(f"❌ Non-existent preset returned: '{non_existent}'")
    
    # Test overwriting preset
    print("\n🔄 Testing preset overwriting...")
    original = chiv.LoadPreset(0)
    new_reason = "Updated reason for testing"
    chiv.SavePreset(0, new_reason)
    updated = chiv.LoadPreset(0)
    if updated == new_reason:
        print(f"✅ Preset 0 successfully updated to: '{updated}'")
    else:
        print(f"❌ Preset 0 update failed. Expected: '{new_reason}', Got: '{updated}'")
    
    # Restore original
    chiv.SavePreset(0, original)
    
    print("\n✅ Preset functionality testing completed!")

class MockChivalry:
    """Mock Chivalry class for testing presets without game running"""
    
    def SavePreset(self, slot, reason_text):
        """Save the kick/ban reason sentence to a preset slot."""
        import os
        import json
        
        presets_file = "reason_presets.json"
        
        # Load existing presets or create new dict
        presets = {}
        if os.path.exists(presets_file):
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
            except Exception:
                presets = {}
        
        # Save the preset
        presets[str(slot)] = reason_text
        
        # Write back to file
        try:
            with open(presets_file, 'w', encoding='utf-8') as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def LoadPreset(self, slot):
        """Load the kick/ban reason sentence from a preset slot."""
        import os
        import json
        
        presets_file = "reason_presets.json"
        
        if not os.path.exists(presets_file):
            return None
        
        try:
            with open(presets_file, 'r', encoding='utf-8') as f:
                presets = json.load(f)
            return presets.get(str(slot), None)
        except Exception:
            return None

    def GetAllPresets(self):
        """Get all saved presets as a dictionary."""
        import os
        import json
        
        presets_file = "reason_presets.json"
        
        if not os.path.exists(presets_file):
            return {}
        
        try:
            with open(presets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

def cleanup_test_files():
    """Clean up test files"""
    if os.path.exists("reason_presets.json"):
        os.remove("reason_presets.json")
        print("🧹 Cleaned up test files")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_files()
    else:
        test_preset_functionality()
