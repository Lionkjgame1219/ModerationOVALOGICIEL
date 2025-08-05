#!/usr/bin/env python3
"""
GUI test for reason preset functionality
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from interface import ActionForm

class PresetTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preset Functionality Test")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Reason Preset Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Click the buttons below to test the preset functionality.\n"
            "This will open the Ban/Kick dialog with preset save/load buttons."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; color: #666;")
        layout.addWidget(instructions)
        
        # Test buttons
        btn_test_ban = QPushButton("🔨 Test Ban Dialog with Presets")
        btn_test_ban.clicked.connect(self.test_ban_dialog)
        btn_test_ban.setStyleSheet("padding: 10px; margin: 5px; background-color: #e74c3c; color: white; font-weight: bold;")
        layout.addWidget(btn_test_ban)
        
        btn_test_kick = QPushButton("👢 Test Kick Dialog with Presets")
        btn_test_kick.clicked.connect(self.test_kick_dialog)
        btn_test_kick.setStyleSheet("padding: 10px; margin: 5px; background-color: #f39c12; color: white; font-weight: bold;")
        layout.addWidget(btn_test_kick)
        
        # Info
        info = QLabel(
            "Features to test:\n"
            "• Save reasons to preset slots (0-9)\n"
            "• Load reasons from preset slots\n"
            "• Tooltips showing preset contents\n"
            "• Visual indicators for filled slots"
        )
        info.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)
        
        central_widget.setLayout(layout)
    
    def test_ban_dialog(self):
        """Open ban dialog for testing"""
        dialog = ActionForm("Ban", "TEST_PLAYER_ID", "TestPlayer")
        dialog.exec_()
    
    def test_kick_dialog(self):
        """Open kick dialog for testing"""
        dialog = ActionForm("Kick", "TEST_PLAYER_ID", "TestPlayer")
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    
    # Create some sample presets for testing
    create_sample_presets()
    
    window = PresetTestWindow()
    window.show()
    
    sys.exit(app.exec_())

def create_sample_presets():
    """Create some sample presets for testing"""
    import json
    
    sample_presets = {
        "0": "Cheating/Hacking",
        "1": "Toxic behavior in chat",
        "2": "Team killing repeatedly",
        "3": "Griefing other players",
        "4": "Inappropriate language"
    }
    
    try:
        with open("reason_presets.json", 'w', encoding='utf-8') as f:
            json.dump(sample_presets, f, ensure_ascii=False, indent=2)
        print("✅ Sample presets created for testing")
    except Exception as e:
        print(f"❌ Failed to create sample presets: {e}")

if __name__ == "__main__":
    main()
