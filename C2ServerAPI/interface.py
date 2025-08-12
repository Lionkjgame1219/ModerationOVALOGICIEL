import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QListWidget, QHBoxLayout, QGroupBox, QSpacerItem, QSizePolicy, QInputDialog, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import pyperclip
import time
import os
import sys
import win32gui

from core.C2ServerAPIExample import GameChivalry
from core.guiServer import Chivalry
import core.wehbooks as wehbooks 

def check_chivalry_window():
    """Check if Chivalry 2 window is available"""
    try:
        hwnd = win32gui.FindWindow(None, "Chivalry 2  ")  # Note the spaces after the 2
        return hwnd != 0
    except Exception:
        return False

class ChivalryWaitingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waiting for Chivalry 2")
        self.setFixedSize(500, 350)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Waiting for Chivalry 2")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        # Let global theme handle colors, reduce bottom margin
        title.setContentsMargins(0, 0, 0, 5)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel()
        instructions.setText(
            "Please launch your Chivalry 2 game.\n\n"
            "The admin tool will automatically continue once the game is detected."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        # Let global theme handle colors and styling, reduce margins
        instructions.setContentsMargins(10, 5, 10, 5)
        instructions.setMinimumHeight(80)
        instructions.setMaximumHeight(80)
        instructions.setSizePolicy(instructions.sizePolicy().horizontalPolicy(), instructions.sizePolicy().Fixed)
        layout.addWidget(instructions)

        # Status label - avoid CSS styling to prevent cramping
        self.status_label = QLabel("Searching for Chivalry 2 window...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Set font using Qt methods instead of CSS
        font = QFont("Segoe UI", 12)
        font.setBold(True)
        self.status_label.setFont(font)

        # Let the global theme handle colors - no manual color setting
        self.status_label.setContentsMargins(10, 5, 10, 5)

        layout.addWidget(self.status_label)

        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("margin: 10px 0px;")
        layout.addWidget(self.progress_bar)

        # Add some spacing before buttons
        layout.addSpacing(5)

        # Button layout
        button_layout = QHBoxLayout()

        # Theme toggle button
        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setMinimumHeight(35)
        # Let global theme handle styling
        button_layout.addWidget(self.theme_button)

        # Skip button
        skip_button = QPushButton("Skip Waiting (Continue Anyway)")
        skip_button.clicked.connect(self.accept)
        skip_button.setMinimumHeight(35)
        # Let global theme handle styling
        button_layout.addWidget(skip_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Force layout to be calculated immediately
        layout.activate()
        self.adjustSize()

        # Timer to check for Chivalry 2 window
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_window)
        self.timer.start(1000)  # Check every second

        # Update theme button text based on current theme
        self.update_theme_button()

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        app = QApplication.instance()
        current_is_dark = load_theme_preference()
        new_is_dark = not current_is_dark

        # Apply new theme
        if new_is_dark:
            apply_dark_theme(app)
        else:
            apply_light_theme(app)

        # Save preference
        save_theme_preference(new_is_dark)

        # Update button text
        self.update_theme_button()

        # Force refresh of this dialog's appearance
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_theme_button(self):
        """Update theme button text based on current theme"""
        is_dark = load_theme_preference()
        if is_dark:
            self.theme_button.setText("☀️ Light Mode")
        else:
            self.theme_button.setText("🌙 Dark Mode")

    def check_window(self):

        if check_chivalry_window():
            self.status_label.setText("✓ Chivalry 2 found! Starting admin tool...")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
            self.timer.stop()
            QTimer.singleShot(1500, self.accept)  # Wait 1.5 seconds then close
        else:
            self.status_label.setText(f"Searching for Chivalry 2 window...")

def parse_player_list_from_clipboard():
    text = pyperclip.paste()
    lines = text.strip().splitlines()
    data_lines = lines[2:]
    players = []
    for line in data_lines:
        parts = [p.strip() for p in line.split(" - ")]
        if len(parts) < 2:
            continue
        name = parts[0]
        playfab_id = parts[1]
        players.append((name, playfab_id))
    return players

class ActionForm(QDialog):
    def __init__(self, action_name, player_id, player_name):
        super().__init__()
        self.setWindowTitle(f"{action_name} Player")
        self.resize(450, 350)

        # Try to connect to game
        self.game = None
        try:
            self.game = GameChivalry()
        except Exception as e:
            print(f"[ACTION FORM] Could not connect to Chivalry 2: {e}")

        # Main layout
        main_layout = QVBoxLayout()

        # Form layout for player info and reason
        form_layout = QFormLayout()
        self.player_id_input = QLineEdit(player_id)
        self.player_id_input.setReadOnly(True)
        self.player_name = QLineEdit(player_name)
        self.player_name.setReadOnly(True)
        form_layout.addRow("Player ID:", self.player_id_input)
        form_layout.addRow("Player Name:", self.player_name)
        self.reason_input = QLineEdit()
        form_layout.addRow("Reason:", self.reason_input)

        if action_name.lower() == "ban":
            self.time_input = QLineEdit()
            self.time_input.setPlaceholderText("Duration in hours (e.g., 7)")
            form_layout.addRow("Time (hours):", self.time_input)
        else:
            self.time_input = None

        main_layout.addLayout(form_layout)

        # Preset buttons section
        preset_group = QGroupBox("Reason Presets")
        preset_layout = QVBoxLayout()

        # Load preset buttons (2 rows of 5 buttons each)
        load_layout1 = QHBoxLayout()
        load_layout2 = QHBoxLayout()

        self.load_buttons = []
        for i in range(10):
            btn = QPushButton(f"Slot {i}")
            btn.clicked.connect(lambda checked, slot=i: self.load_preset(slot))
            btn.setMaximumWidth(80)
            self.load_buttons.append(btn)
            if i < 5:
                load_layout1.addWidget(btn)
            else:
                load_layout2.addWidget(btn)

        preset_layout.addWidget(QLabel("Load Presets:"))
        preset_layout.addLayout(load_layout1)
        preset_layout.addLayout(load_layout2)

        # Save preset buttons (2 rows of 5 buttons each)
        save_layout1 = QHBoxLayout()
        save_layout2 = QHBoxLayout()

        self.save_buttons = []
        for i in range(10):
            btn = QPushButton(f"Slot {i}")
            btn.clicked.connect(lambda checked, slot=i: self.save_preset(slot))
            btn.setMaximumWidth(80)
            self.save_buttons.append(btn)
            if i < 5:
                save_layout1.addWidget(btn)
            else:
                save_layout2.addWidget(btn)

        preset_layout.addWidget(QLabel("Save Presets:"))
        preset_layout.addLayout(save_layout1)
        preset_layout.addLayout(save_layout2)

        preset_group.setLayout(preset_layout)
        main_layout.addWidget(preset_group)

        # Action buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.perform_action)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.action_name = action_name
        self.setLayout(main_layout)

        # Update button tooltips with preset contents
        self.update_preset_tooltips()

    def load_preset(self, slot):
        """Load a preset reason into the reason input field"""
        from core.guiServer import Chivalry
        chiv = Chivalry()
        preset_text = chiv.LoadPreset(slot)

        if preset_text:
            self.reason_input.setText(preset_text)
            QMessageBox.information(self, "Preset Loaded", f"Preset {slot} loaded successfully!")
        else:
            QMessageBox.warning(self, "No Preset", f"No preset found in slot {slot}.")

    def save_preset(self, slot):
        """Save the current reason text to a preset slot"""
        reason = self.reason_input.text().strip()
        if not reason:
            QMessageBox.warning(self, "Empty Reason", "Please enter a reason before saving to preset.")
            return

        from core.guiServer import Chivalry
        chiv = Chivalry()
        success = chiv.SavePreset(slot, reason)

        if success:
            QMessageBox.information(self, "Preset Saved", f"Reason saved to preset {slot} successfully!")
            self.update_preset_tooltips()
        else:
            QMessageBox.warning(self, "Save Failed", f"Failed to save preset {slot}.")

    def update_preset_tooltips(self):
        """Update tooltips for load buttons to show preset contents"""
        from core.guiServer import Chivalry
        chiv = Chivalry()
        presets = chiv.GetAllPresets()

        # Get current theme to use appropriate colors
        is_dark_theme = load_theme_preference()

        for i, btn in enumerate(self.load_buttons):
            preset_text = presets.get(str(i), "")
            if preset_text:
                # Truncate long text for tooltip
                display_text = preset_text[:50] + "..." if len(preset_text) > 50 else preset_text
                btn.setToolTip(f"Slot {i}: {display_text}")

                # Use theme-appropriate colors for filled slots
                if is_dark_theme:
                    btn.setStyleSheet("QPushButton { background-color: #2d5a2d; color: #ffffff; }")  # Dark green for dark theme
                else:
                    btn.setStyleSheet("QPushButton { background-color: #e6ffe6; color: #333333; }")  # Light green for light theme
            else:
                btn.setToolTip(f"Slot {i}: Empty")
                btn.setStyleSheet("")  # Default style for empty slots

    def perform_action(self):
        reason = self.reason_input.text().strip()
        if not reason:
            QMessageBox.warning(self, "Error", "Please enter a reason.")
            return
        player_id = self.player_id_input.text()
        player_name = self.player_name.text()
        if self.action_name.lower() == "ban":
            time_str = self.time_input.text().strip()
            if not time_str.isdigit():
                QMessageBox.warning(self, "Error", "Please enter a valid number for time.")
                return
            time_hour = int(time_str)
            print(f"[{self.action_name.upper()}] Player ID={player_id}, Reason={reason}, Time={time_hour} hours")

            # Try to execute the ban command if game is connected
            action_executed = False
            if hasattr(self.game, 'banbyid'):
                try:
                    self.game.banbyid(player_id, time_hour, reason)
                    action_executed = True
                    #QMessageBox.information(self, self.action_name, f"{self.action_name} executed for player {player_id}.\nReason: {reason}\nTime: {time_hour} hours")
                except Exception as e:
                    QMessageBox.warning(self, "Game Connection Error", f"Could not execute ban command:\n{str(e)}\n\nNo Discord notification will be sent.")
            else:
                QMessageBox.information(self, self.action_name, f"{self.action_name} not executed - Chivalry 2 not connected.\nReason: {reason}\nTime: {time_hour} hours\n\nNo Discord notification sent.")

            # Only send Discord notification if the action was actually executed
            if action_executed:
                wehbooks.MessageForAdmin(player_id, player_name, reason, time_hour, "ban")
        else:
            print(f"[{self.action_name.upper()}] Player ID={player_id}, Reason={reason}")

            # Try to execute the kick command if game is connected
            action_executed = False
            if hasattr(self.game, 'kickbyid'):
                try:
                    self.game.kickbyid(player_id, reason)
                    action_executed = True
                    #QMessageBox.information(self, self.action_name, f"{self.action_name} executed for player {player_id}.\nReason: {reason}")
                except Exception as e:
                    QMessageBox.warning(self, "Game Connection Error", f"Could not execute kick command:\n{str(e)}\n\nNo Discord notification will be sent.")
            else:
                QMessageBox.information(self, self.action_name, f"{self.action_name} not executed - Chivalry 2 not connected.\nReason: {reason}\n\nNo Discord notification sent.")

            # Only send Discord notification if the action was actually executed
            if action_executed:
                wehbooks.MessageForAdmin(player_id, player_name, reason, None, "kick")
        self.accept()

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        app = QApplication.instance()
        current_is_dark = load_theme_preference()
        new_is_dark = not current_is_dark

        # Apply new theme
        if new_is_dark:
            apply_dark_theme(app)
        else:
            apply_light_theme(app)

        # Save preference
        save_theme_preference(new_is_dark)

        # Update preset button colors
        self.update_preset_tooltips()

        # Force refresh of this dialog's appearance
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

class PlayerActionDialog(QDialog):
    def __init__(self, player_id, player_name):
        super().__init__()
        self.setWindowTitle(f"Actions for {player_name} (ID: {player_id})")
        self.resize(320, 140)
        self.player_id = player_id
        self.player_name = player_name
        layout = QVBoxLayout()
        label = QLabel(f"Choose an action for player <b>{player_name}</b> (ID: {player_id}):")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        btn_ban = QPushButton("⛔ Ban")
        btn_ban.setStyleSheet("background-color:#e74c3c; color: white; font-weight: bold;")
        btn_ban.clicked.connect(self.ban_player)
        layout.addWidget(btn_ban)
        btn_kick = QPushButton("🚪 Kick")
        btn_kick.setStyleSheet("background-color:#f39c12; color: white; font-weight: bold;")
        btn_kick.clicked.connect(self.kick_player)
        layout.addWidget(btn_kick)

        # Player profile button
        btn_profile = QPushButton("� Chivalry2Stats player profile")
        btn_profile.setStyleSheet("background-color:#3498db; color: white; font-weight: bold;")
        btn_profile.clicked.connect(self.open_player_profile)
        layout.addWidget(btn_profile)

        self.setLayout(layout)

    def ban_player(self):
        form = ActionForm("Ban", self.player_id, self.player_name)
        form.exec_()

    def kick_player(self):
        form = ActionForm("Kick", self.player_id, self.player_name)
        form.exec_()

    def open_player_profile(self):
        """Open the player's profile page on chivalry2stats.com"""
        profile_url = f"https://chivalry2stats.com/player?id={self.player_id}"

        # Import webbrowser to open the URL
        import webbrowser
        try:
            webbrowser.open(profile_url)
            print(f"[PROFILE] Opening player profile: {profile_url}")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to open player profile:\n{str(e)}"
            )

class PlayersWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connected Players")
        self.resize(420, 560)

        # Try to connect to game
        self.game = None
        try:
            self.game = GameChivalry()
        except Exception as e:
            print(f"[PLAYERS WINDOW] Could not connect to Chivalry 2: {e}")
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        title = QLabel("<h3>Connected Players List:</h3>")
        title.setAlignment(Qt.AlignLeft)
        top_layout.addWidget(title)
        refresh_btn = QPushButton("🔄 Refresh Player List")
        refresh_btn.clicked.connect(self.refresh_player_list)
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-weight: bold;
                background-color: #1976d2;
                color: white;
                border: 1px solid #1565c0;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
                border: 1px solid #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        top_layout.addWidget(refresh_btn)

        # Warning label about manual refresh
        warning_label = QLabel("⚠️ Manual refresh only - for now")
        warning_label.setStyleSheet("color: #ffb74d; font-size: 11px; margin: 5px; font-style: italic; background-color: transparent;")
        top_layout.addWidget(warning_label)
        main_layout.addLayout(top_layout)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher par ID ou pseudo...")
        self.search_bar.textChanged.connect(self.filter_players)
        main_layout.addWidget(self.search_bar)
        self.player_list = QListWidget()
        main_layout.addWidget(self.player_list)
        self.player_list.itemClicked.connect(self.open_player_actions)
        self.setLayout(main_layout)



    '''def refresh_player_list(self):
        if hasattr(self.game, 'ListPlayers'):
            try:
                self.game.ListPlayers()
                # ListPlayers handles timing internally (console auto-closes), minimal delay here
                time.sleep(0.1)
                self.players = parse_player_list_from_clipboard()
                self.filtered_players = self.players.copy()
                self.populate_list()
            except Exception as e:
                QMessageBox.warning(self, "Game Connection Error", f"Could not refresh player list:\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Game Connection", "Cannot refresh player list - Chivalry 2 not connected.\n\nPlease ensure Chivalry 2 is running and you are connected to a server.")'''
        
    def refresh_player_list(self):
        self.game.ListPlayers()
        time.sleep(5.0)
        self.players = parse_player_list_from_clipboard()
        self.filtered_players = self.players.copy()
        self.populate_list()

    def populate_list(self):
        self.player_list.clear()
        for name, pid in self.filtered_players:
            self.player_list.addItem(f"{name} - {pid}")

    def filter_players(self, text):
        text = text.lower()
        self.filtered_players = [
            (name, pid) for name, pid in self.players
            if text in name.lower() or text in pid.lower()
        ]
        self.populate_list()

    def open_player_actions(self, item):
        text = item.text()
        if " - " not in text:
            return
        name, pid = text.split(" - ", 1)
        dialog = PlayerActionDialog(pid, name)
        dialog.exec_()

class ActionDialog(QDialog):
    def __init__(self, title, fields):
        super().__init__()
        self.setWindowTitle(title)
        self.inputs = {}
        layout = QFormLayout()
        for field in fields:
            line_edit = QLineEdit()
            layout.addRow(field + ":", line_edit)
            self.inputs[field] = line_edit
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_inputs(self):
        return [line_edit.text().strip() for line_edit in self.inputs.values()]

class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()

        # Try to connect to Chivalry 2, but don't fail if it's not available
        self.game = None
        self.chivalry_connected = False
        self.server_connected = False
        self.last_player_count = 0

        self.setWindowTitle("Admin Dashboard")
        self.resize(600, 500)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        status_group = QGroupBox("Server Status")
        status_layout = QVBoxLayout()

        # Initialize status label (will be updated by update_connection_status)
        self.status_label = QLabel("Checking connection...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)

        # Add webhook status
        self.webhook_status_label = QLabel()
        self.webhook_status_label.setAlignment(Qt.AlignCenter)
        self.update_webhook_status()
        status_layout.addWidget(self.webhook_status_label)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        # Admin Message Section
        admin_message_group = QGroupBox("Admin Message")
        admin_message_layout = QVBoxLayout()
        self.admin_message_input = QLineEdit()
        self.admin_message_input.setPlaceholderText("Type the admin message to send...")
        admin_message_layout.addWidget(self.admin_message_input)
        btn_send_admin_message = QPushButton("Send Admin Message")
        btn_send_admin_message.clicked.connect(self.send_admin_message)
        admin_message_layout.addWidget(btn_send_admin_message)
        admin_message_group.setLayout(admin_message_layout)
        main_layout.addWidget(admin_message_group)

        # Server Message Section
        server_message_group = QGroupBox("Server Message")
        server_message_layout = QVBoxLayout()
        self.server_message_input = QLineEdit()
        self.server_message_input.setPlaceholderText("Type the server message to send...")
        server_message_layout.addWidget(self.server_message_input)
        btn_send_server_message = QPushButton("Send Server Message")
        btn_send_server_message.clicked.connect(self.send_server_message)
        server_message_layout.addWidget(btn_send_server_message)
        server_message_group.setLayout(server_message_layout)
        main_layout.addWidget(server_message_group)

        # Actions Section
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        btn_players = QPushButton("👥 Connected Players")
        btn_players.clicked.connect(self.open_players_window)
        actions_layout.addWidget(btn_players)
        btn_add_time = QPushButton("⏱️ Add Time")
        btn_add_time.clicked.connect(self.open_add_time_dialog)
        actions_layout.addWidget(btn_add_time)

        btn_webhook_config = QPushButton("🔗 Configure Discord Webhook")
        btn_webhook_config.clicked.connect(self.configure_discord_webhook)
        actions_layout.addWidget(btn_webhook_config)

        btn_discord_id_config = QPushButton("👤 Configure Discord User ID")
        btn_discord_id_config.clicked.connect(self.configure_discord_user_id)
        actions_layout.addWidget(btn_discord_id_config)

        # Theme toggle button
        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        actions_layout.addWidget(self.theme_button)

        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main_layout)

        # Now that UI is initialized, set up connection monitoring
        self.check_game_connection()

        # Set up periodic connection checking timer
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_game_connection)
        self.connection_timer.start(5000)  # Check every 5 seconds

        # Update theme button text based on current theme
        self.update_theme_button()

        # Keep track of player window instance
        self.players_window = None

    def check_game_connection(self):
        """Check game and server connection status"""
        # Check if Chivalry 2 window exists
        game_window_exists = check_chivalry_window()

        # Try to connect to game if window exists but we're not connected
        if game_window_exists and not self.chivalry_connected:
            try:
                self.game = GameChivalry()
                self.chivalry_connected = True
                print("[CONNECTION] Successfully connected to Chivalry 2")
            except Exception as e:
                print(f"[CONNECTION] Could not connect to Chivalry 2: {e}")
                self.chivalry_connected = False
                self.game = None

        # If window doesn't exist, mark as disconnected
        elif not game_window_exists and self.chivalry_connected:
            print("[CONNECTION] Chivalry 2 window no longer found - disconnecting")
            self.chivalry_connected = False
            self.server_connected = False
            self.game = None

        # Note: We don't automatically check server connection to avoid disrupting gameplay
        # Server connection status will be determined only when user manually refreshes player list

        # Update status display
        self.update_connection_status()

    def update_connection_status(self):
        """Update the connection status display"""
        if self.chivalry_connected:
            self.status_label.setText("✅ Chivalry 2 Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("⚠️ Chivalry 2 Not Connected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")



    def update_webhook_status(self):
        """Update the webhook status display"""
        status = wehbooks.get_webhook_status()

        if status['primary_active'] and status['secondary_active']:
            self.webhook_status_label.setText("🔗 Discord: Primary + Secondary Active")
            self.webhook_status_label.setStyleSheet("color: green;")
        elif status['primary_active']:
            self.webhook_status_label.setText("🔗 Discord: Primary Active")
            self.webhook_status_label.setStyleSheet("color: green;")
        elif status['secondary_active']:
            self.webhook_status_label.setText("🔗 Discord: Secondary Active")
            self.webhook_status_label.setStyleSheet("color: green;")
        else:
            self.webhook_status_label.setText("🔗 Discord: Not Configured")
            self.webhook_status_label.setStyleSheet("color: orange;")

    def send_admin_message(self):
        msg = self.admin_message_input.text().strip()

        if not msg:
            QMessageBox.warning(self, "Error", "Please enter a message to send.")
            return
        print(f"[ADMIN MESSAGE] {msg}")

        # Try to send to game if connected
        message_sent = False
        if self.chivalry_connected and hasattr(self.game, 'AdminSay'):
            try:
                self.game.AdminSay(msg)
                message_sent = True
                #QMessageBox.information(self, "Message Sent", "Admin message sent successfully to game and Discord!")
            except Exception as e:
                QMessageBox.warning(self, "Game Error", f"Failed to send message to game:\n{str(e)}\n\nNo Discord notification sent.")
        else:
            QMessageBox.information(self, "Message Not Sent", "Admin message not sent - Chivalry 2 not connected.\n\nNo Discord notification sent.")

        # Only send Discord notification if the message was actually sent to game
        if message_sent:
            wehbooks.MessageForAdmin("N/A", "N/A", msg, None, "adminsay")

        self.admin_message_input.clear()

    def send_server_message(self):
        msg = self.server_message_input.text().strip()

        if not msg:
            QMessageBox.warning(self, "Error", "Please enter a message to send.")
            return
        print(f"[SERVER MESSAGE] {msg}")

        # Try to send to game if connected
        message_sent = False
        if self.chivalry_connected and hasattr(self.game, 'ServerSay'):
            try:
                self.game.ServerSay(msg)
                message_sent = True
                #QMessageBox.information(self, "Message Sent", "Server message sent successfully to game and Discord!")
            except Exception as e:
                QMessageBox.warning(self, "Game Error", f"Failed to send message to game:\n{str(e)}\n\nNo Discord notification sent.")
        else:
            QMessageBox.information(self, "Message Not Sent", "Server message not sent - Chivalry 2 not connected.\n\nNo Discord notification sent.")

        # Only send Discord notification if the message was actually sent to game
        if message_sent:
            wehbooks.MessageForAdmin("N/A", "N/A", msg, None, "serversay")

        self.server_message_input.clear()

    def open_players_window(self):
        # Check if player window already exists and is visible
        if self.players_window is not None and self.players_window.isVisible():
            # Window already exists, just bring it to front (no auto-refresh)
            self.players_window.raise_()
            self.players_window.activateWindow()
        else:
            # Create new window or reuse closed one
            if self.players_window is None:
                self.players_window = PlayersWindow()
                # Connect the finished signal to clean up reference when window is closed
                self.players_window.finished.connect(lambda: setattr(self, 'players_window', None))

            # Set focus to the dialog and bring it to front (no auto-refresh)
            self.players_window.show()
            self.players_window.raise_()
            self.players_window.activateWindow()
            self.players_window.exec_()

    def open_add_time_dialog(self):
        dialog = ActionDialog("Add Time", ["Time to add (minutes)"])
        if dialog.exec_() == QDialog.Accepted:
            added_time = dialog.get_inputs()[0]
            print(f" +{added_time}min")

            # Try to add time to game if connected
            time_added = False
            if self.chivalry_connected and hasattr(self.game, 'AddTime'):
                try:
                    self.game.AddTime(added_time)
                    time_added = True
                    # Delay the success message to avoid stealing focus from game during console operations
                    QTimer.singleShot(2000, lambda: QMessageBox.information(self, "Time Added", f"Successfully added {added_time} minutes to the game!"))
                except Exception as e:
                    QMessageBox.warning(self, "Game Error", f"Failed to add time to game:\n{str(e)}\n\nNo Discord notification sent.")
            else:
                QMessageBox.information(self, "Time Not Added", f"Time not added - Chivalry 2 not connected.\n\nNo Discord notification sent.")

            # Only send Discord notification if time was actually added to game
            if time_added:
                wehbooks.MessageForAdmin("N/A", "N/A", f"Added {added_time} minutes", added_time, "time")

    def configure_discord_webhook(self):
        """Allow user to reconfigure Discord webhooks"""
        import os

        # Get current webhook URLs if they exist
        current_primary_url = ""
        current_secondary_url = ""
        localconfig = "localconfig"
        if os.path.exists(localconfig):
            try:
                with open(localconfig, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 1 and lines[0] != "None":
                        current_primary_url = lines[0]
                    if len(lines) >= 2 and lines[1] != "None":
                        current_secondary_url = lines[1]
            except Exception:
                pass

        # Prompt for primary webhook URL
        primary_url, ok = QInputDialog.getText(
            self,
            "Primary Discord Webhook Configuration",
            "Enter your primary Discord Webhook URL:\n"
            "(Leave empty to disable Discord notifications)",
            text=current_primary_url
        )

        if not ok:
            return

        primary_url = primary_url.strip()
        if primary_url and not primary_url.startswith("https://discord.com/api/webhooks/"):
            QMessageBox.warning(
                self,
                "Invalid Primary URL",
                "Primary Discord webhook URL must start with:\n"
                "https://discord.com/api/webhooks/"
            )
            return

        # Prompt for secondary webhook URL (only if primary is configured)
        secondary_url = ""
        if primary_url:
            secondary_url, ok2 = QInputDialog.getText(
                self,
                "Secondary Discord Webhook Configuration",
                "Enter your secondary Discord Webhook URL (optional):\n"
                "(Leave empty to use only the primary webhook)",
                text=current_secondary_url
            )

            if ok2 and secondary_url.strip():
                secondary_url = secondary_url.strip()
                if not secondary_url.startswith("https://discord.com/api/webhooks/"):
                    QMessageBox.warning(
                        self,
                        "Invalid Secondary URL",
                        "Secondary Discord webhook URL must start with:\n"
                        "https://discord.com/api/webhooks/"
                    )
                    return
            else:
                secondary_url = ""

        # Save the URLs to file, preserving existing Discord user ID and presets
        try:
            # Read existing Discord user ID and presets
            existing_discord_user_id = "None"
            existing_presets = []
            if os.path.exists(localconfig):
                with open(localconfig, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    # Preserve Discord user ID from line 3
                    if len(lines) >= 3:
                        existing_discord_user_id = lines[2]
                    # Preserve presets from line 4 onwards
                    if len(lines) > 3:
                        existing_presets = lines[3:]

            # Write webhooks, Discord user ID, and presets
            with open(localconfig, 'w', encoding='utf-8') as f:
                f.write(f"{primary_url if primary_url else 'None'}\n")
                f.write(f"{secondary_url if secondary_url else 'None'}\n")
                f.write(f"{existing_discord_user_id}\n")
                # Write existing presets or empty lines for 10 slots
                for i in range(10):
                    if i < len(existing_presets):
                        f.write(f"{existing_presets[i]}\n")
                    else:
                        f.write("\n")

            # Reinitialize webhooks
            webhook_initialized = wehbooks.initialize_webhook()

            # Update the status display
            self.update_webhook_status()

            if primary_url or secondary_url:
                if webhook_initialized:
                    message = "Discord webhook(s) have been configured successfully!"
                    if primary_url and secondary_url:
                        message = "Both primary and secondary Discord webhooks have been configured successfully!"
                    elif primary_url:
                        message = "Primary Discord webhook has been configured successfully!"
                    elif secondary_url:
                        message = "Secondary Discord webhook has been configured successfully!"

                    QMessageBox.information(
                        self,
                        "Configuration Successful",
                        message
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Configuration Error",
                        "Unable to initialize Discord webhook(s).\n"
                        "Please check that the URL(s) are correct."
                    )
            else:
                QMessageBox.information(
                    self,
                    "Webhooks Disabled",
                    "Discord notifications have been disabled."
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Error",
                f"Unable to save configuration:\n{str(e)}"
            )

    def configure_discord_user_id(self):
        """Allow user to configure Discord User ID"""
        import os

        # Get current Discord user ID if it exists
        current_discord_user_id = ""
        localconfig = "localconfig"
        if os.path.exists(localconfig):
            try:
                with open(localconfig, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 3 and lines[2] != "None":
                        current_discord_user_id = lines[2]
            except Exception:
                pass

        # Prompt for new Discord user ID
        discord_user_id, ok = QInputDialog.getText(
            self,
            "Discord User ID Configuration",
            "Enter your Discord User ID:\n"
            "(This will be used for @mentions in notifications)\n"
            "(Leave empty to disable mentions)",
            text=current_discord_user_id
        )

        if not ok:
            return

        discord_user_id = discord_user_id.strip()

        # Save the Discord user ID to file, preserving existing webhooks and presets
        try:
            # Read existing configuration
            webhook_primary = "None"
            webhook_secondary = "None"
            existing_presets = []
            if os.path.exists(localconfig):
                with open(localconfig, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 1:
                        webhook_primary = lines[0]
                    if len(lines) >= 2:
                        webhook_secondary = lines[1]
                    # Preserve presets from line 4 onwards
                    if len(lines) > 3:
                        existing_presets = lines[3:]

            # Write configuration with updated Discord user ID
            with open(localconfig, 'w', encoding='utf-8') as f:
                f.write(f"{webhook_primary}\n")
                f.write(f"{webhook_secondary}\n")
                f.write(f"{discord_user_id if discord_user_id else 'None'}\n")
                # Write existing presets or empty lines for 10 slots
                for i in range(10):
                    if i < len(existing_presets):
                        f.write(f"{existing_presets[i]}\n")
                    else:
                        f.write("\n")

            if discord_user_id:
                QMessageBox.information(
                    self,
                    "Configuration Successful",
                    f"Discord User ID has been set to: {discord_user_id}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Configuration Successful",
                    "Discord User ID has been cleared. Mentions will be disabled."
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Error",
                f"Unable to save Discord User ID:\n{str(e)}"
            )

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        app = QApplication.instance()
        current_is_dark = load_theme_preference()
        new_is_dark = not current_is_dark

        # Apply new theme
        if new_is_dark:
            apply_dark_theme(app)
        else:
            apply_light_theme(app)

        # Save preference
        save_theme_preference(new_is_dark)

        # Update button text
        self.update_theme_button()

        # Update preset button colors if this is an action dialog
        if hasattr(self, 'update_preset_tooltips'):
            self.update_preset_tooltips()

        # Force refresh of this window's appearance
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_theme_button(self):
        """Update theme button text based on current theme"""
        is_dark = load_theme_preference()
        if is_dark:
            self.theme_button.setText("☀️ Light Mode")
        else:
            self.theme_button.setText("🌙 Dark Mode")

def load_theme_preference():
    """Load theme preference from localconfig file"""
    import os
    localconfig = "localconfig"
    if os.path.exists(localconfig):
        try:
            with open(localconfig, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                # Theme preference is stored on line 14 (index 13)
                if len(lines) >= 14 and lines[13].strip():
                    return lines[13].strip().lower() == 'dark'
        except Exception:
            pass
    return True  # Default to dark theme

def save_theme_preference(is_dark_theme):
    """Save theme preference to localconfig file"""
    import os
    localconfig = "localconfig"

    # Read existing configuration
    lines = ['None'] * 14  # Initialize with 14 lines
    if os.path.exists(localconfig):
        try:
            with open(localconfig, 'r', encoding='utf-8') as f:
                existing_lines = f.read().strip().split('\n')
                for i, line in enumerate(existing_lines):
                    if i < 14:
                        lines[i] = line
        except Exception:
            pass

    # Set theme preference on line 14 (index 13)
    lines[13] = 'dark' if is_dark_theme else 'light'

    # Write back to file
    try:
        with open(localconfig, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
    except Exception as e:
        print(f"[THEME] Failed to save theme preference: {e}")

def apply_dark_theme(app):
    """Apply a dark theme to the entire application"""
    dark_stylesheet = """
    /* Main application styling */
    QApplication {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    /* Main windows and dialogs */
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        selection-background-color: #3d5afe;
    }

    /* Group boxes */
    QGroupBox {
        background-color: #353535;
        border: 2px solid #555555;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 10px;
        font-weight: bold;
        color: #ffffff;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: #ffffff;
        background-color: #353535;
    }

    /* Buttons */
    QPushButton {
        background-color: #404040;
        border: 1px solid #606060;
        border-radius: 4px;
        padding: 8px 16px;
        color: #ffffff;
        font-weight: bold;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #505050;
        border: 1px solid #707070;
    }

    QPushButton:pressed {
        background-color: #303030;
        border: 1px solid #505050;
    }

    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666666;
        border: 1px solid #404040;
    }

    /* Input fields */
    QLineEdit {
        background-color: #404040;
        border: 2px solid #606060;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        selection-background-color: #3d5afe;
    }

    QLineEdit:focus {
        border: 2px solid #3d5afe;
    }

    /* Labels */
    QLabel {
        color: #ffffff;
        background-color: transparent;
    }

    /* List widgets */
    QListWidget {
        background-color: #353535;
        border: 1px solid #606060;
        border-radius: 4px;
        color: #ffffff;
        selection-background-color: #3d5afe;
        alternate-background-color: #404040;
    }

    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #505050;
    }

    QListWidget::item:selected {
        background-color: #3d5afe;
        color: #ffffff;
    }

    QListWidget::item:hover {
        background-color: #454545;
    }

    /* Progress bars */
    QProgressBar {
        background-color: #404040;
        border: 1px solid #606060;
        border-radius: 4px;
        text-align: center;
        color: #ffffff;
    }

    QProgressBar::chunk {
        background-color: #3d5afe;
        border-radius: 3px;
    }

    /* Dialogs */
    QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    /* Message boxes */
    QMessageBox {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    QMessageBox QPushButton {
        min-width: 80px;
        min-height: 25px;
    }

    /* Input dialogs */
    QInputDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    /* Scroll bars */
    QScrollBar:vertical {
        background-color: #404040;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #606060;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #707070;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    """

    app.setStyleSheet(dark_stylesheet)

def apply_light_theme(app):
    """Apply a light theme to the entire application"""
    light_stylesheet = """
    /* Main application styling */
    QApplication {
        background-color: #f5f5f5;
        color: #333333;
    }

    /* Main windows and dialogs */
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
        selection-background-color: #3d5afe;
    }

    /* Group boxes */
    QGroupBox {
        background-color: #ffffff;
        border: 2px solid #cccccc;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 10px;
        font-weight: bold;
        color: #333333;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: #333333;
        background-color: #ffffff;
    }

    /* Buttons */
    QPushButton {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 8px 16px;
        color: #333333;
        font-weight: bold;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #f0f0f0;
        border: 1px solid #999999;
    }

    QPushButton:pressed {
        background-color: #e0e0e0;
        border: 1px solid #888888;
    }

    QPushButton:disabled {
        background-color: #f8f8f8;
        color: #999999;
        border: 1px solid #dddddd;
    }

    /* Input fields */
    QLineEdit {
        background-color: #ffffff;
        border: 2px solid #cccccc;
        border-radius: 4px;
        padding: 8px;
        color: #333333;
        selection-background-color: #3d5afe;
    }

    QLineEdit:focus {
        border: 2px solid #3d5afe;
    }

    /* Labels */
    QLabel {
        color: #333333;
        background-color: transparent;
    }

    /* List widgets */
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        color: #333333;
        selection-background-color: #3d5afe;
        alternate-background-color: #f8f8f8;
    }

    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #eeeeee;
    }

    QListWidget::item:selected {
        background-color: #3d5afe;
        color: #ffffff;
    }

    QListWidget::item:hover {
        background-color: #f0f0f0;
    }

    /* Progress bars */
    QProgressBar {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        text-align: center;
        color: #333333;
    }

    QProgressBar::chunk {
        background-color: #3d5afe;
        border-radius: 3px;
    }

    /* Dialogs */
    QDialog {
        background-color: #f5f5f5;
        color: #333333;
    }

    /* Message boxes */
    QMessageBox {
        background-color: #f5f5f5;
        color: #333333;
    }

    QMessageBox QPushButton {
        min-width: 80px;
        min-height: 25px;
    }

    /* Input dialogs */
    QInputDialog {
        background-color: #f5f5f5;
        color: #333333;
    }

    /* Scroll bars */
    QScrollBar:vertical {
        background-color: #f0f0f0;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #cccccc;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #999999;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    """

    app.setStyleSheet(light_stylesheet)

def main():
    app = QApplication(sys.argv)

    # Load and apply saved theme preference
    is_dark_theme = load_theme_preference()
    if is_dark_theme:
        apply_dark_theme(app)
    else:
        apply_light_theme(app)

    # Check if we should wait for Chivalry 2
    if "--no-wait" not in sys.argv and not check_chivalry_window():
        waiting_dialog = ChivalryWaitingDialog()
        waiting_dialog.exec_()

    # Initialize Discord webhooks at startup
    import core.wehbooks as wehbooks
    webhook_initialized = wehbooks.initialize_webhook()
    if webhook_initialized:
        print("[STARTUP] Discord webhook(s) initialized successfully")
    else:
        print("[STARTUP] Discord webhooks not configured or failed to initialize")

    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
