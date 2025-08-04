import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QListWidget, QHBoxLayout, QGroupBox, QSpacerItem, QSizePolicy, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pyperclip
import time
import os
import sys

from core.C2ServerAPIExample import GameChivalry
from core.guiServer import Chivalry
import core.wehbooks as wehbooks 

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
        self.setWindowTitle(f"{action_name} joueur")
        self.resize(380, 200)
        self.game = GameChivalry()
        layout = QFormLayout()
        self.player_id_input = QLineEdit(player_id)
        self.player_id_input.setReadOnly(True)
        self.player_name = QLineEdit(player_name)
        self.player_name.setReadOnly(True)
        layout.addRow("ID joueur :", self.player_id_input)
        layout.addRow("Nom joueur :", self.player_name)
        self.reason_input = QLineEdit()
        layout.addRow("Raison :", self.reason_input)

        if action_name.lower() == "bannir":
            self.time_input = QLineEdit()
            self.time_input.setPlaceholderText("Durée en heures (ex : 7)")
            layout.addRow("Temps (heures) :", self.time_input)
        else:
            self.time_input = None
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.perform_action)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.action_name = action_name
        self.setLayout(layout)

    def perform_action(self):
        reason = self.reason_input.text().strip()
        if not reason:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une raison.")
            return
        player_id = self.player_id_input.text()
        player_name = self.player_name.text()
        if self.action_name.lower() == "bannir":
            time_str = self.time_input.text().strip()
            if not time_str.isdigit():
                QMessageBox.warning(self, "Erreur", "Veuillez entrer un nombre valide pour le temps.")
                return
            time_hour = int(time_str)
            print(f"[{self.action_name.upper()}] Joueur ID={player_id}, Raison={reason}, Temps={time_hour} jours")
            QMessageBox.information(self, self.action_name, f"{self.action_name} effectué pour le joueur {player_id}.\nRaison : {reason}\nTemps : {time_hour} hour")
            self.game.banbyid(player_id, time_hour, reason)
            wehbooks.MessageForAdmin(player_id, player_name, reason, time_hour, "ban")
        else:
            print(f"[{self.action_name.upper()}] Joueur ID={player_id}, Raison={reason}")
            QMessageBox.information(self, self.action_name, f"{self.action_name} effectué pour le joueur {player_id}.\nRaison : {reason}")
            self.game.kickbyid(player_id, reason)

            wehbooks.MessageForAdmin(player_id, player_name, reason, None, "kick")
        self.accept()

class PlayerActionDialog(QDialog):
    def __init__(self, player_id, player_name):
        super().__init__()
        self.setWindowTitle(f"Actions pour {player_name} (ID: {player_id})")
        self.resize(320, 140)
        self.player_id = player_id
        self.player_name = player_name
        layout = QVBoxLayout()
        label = QLabel(f"Choisissez une action pour le joueur <b>{player_name}</b> (ID: {player_id}) :")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        btn_ban = QPushButton("⛔ Bannir")
        btn_ban.setStyleSheet("background-color:#e74c3c; color: white; font-weight: bold;")
        btn_ban.clicked.connect(self.ban_player)
        layout.addWidget(btn_ban)
        btn_kick = QPushButton("🚪 Expulser")
        btn_kick.setStyleSheet("background-color:#f39c12; color: white; font-weight: bold;")
        btn_kick.clicked.connect(self.kick_player)
        layout.addWidget(btn_kick)
        self.setLayout(layout)

    def ban_player(self):
        form = ActionForm("Bannir", self.player_id, self.player_name)
        form.exec_()

    def kick_player(self):
        form = ActionForm("Expulser", self.player_id, self.player_name)
        form.exec_()

class PlayersWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Joueurs Connectés")
        self.resize(420, 560)
        self.game = GameChivalry()
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        title = QLabel("<h3>Liste des joueurs connectés :</h3>")
        title.setAlignment(Qt.AlignLeft)
        top_layout.addWidget(title)
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.refresh_player_list)
        top_layout.addWidget(refresh_btn)
        main_layout.addLayout(top_layout)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher par ID ou pseudo...")
        self.search_bar.textChanged.connect(self.filter_players)
        main_layout.addWidget(self.search_bar)
        self.player_list = QListWidget()
        main_layout.addWidget(self.player_list)
        self.player_list.itemClicked.connect(self.open_player_actions)
        self.setLayout(main_layout)

    def refresh_player_list(self):
        self.game.ListPlayers()
        time.sleep(0.5)
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
        self.game = GameChivalry()
        self.setWindowTitle("Interface d'administration")
        self.resize(600, 500)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        self.game.ListPlayers()
        title = QLabel("Dashboard Administrateur")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        self.admin_pseudo = QLineEdit()
        self.admin_pseudo.setPlaceholderText("Entrez votre ID discord")
        self.admin_pseudo.textChanged.connect(self.save_admin_pseudo)
        main_layout.addWidget(self.admin_pseudo)
        self.load_admin_pseudo()
        status_group = QGroupBox("Statut du serveur")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("✅ En ligne")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        btn_admin_msg = QPushButton("📢 Envoyer un message administrateur")
        btn_admin_msg.clicked.connect(self.send_admin_message)
        actions_layout.addWidget(btn_admin_msg)
        btn_players = QPushButton("👥 Joueurs connectés")
        btn_players.clicked.connect(self.open_players_window)
        actions_layout.addWidget(btn_players)
        btn_add_time = QPushButton("⏱️ Ajouter du temps")
        btn_add_time.clicked.connect(self.open_add_time_dialog)
        actions_layout.addWidget(btn_add_time)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)
        message_group = QGroupBox("Message serveur")
        message_layout = QVBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Tapez le message à envoyer au serveur...")
        message_layout.addWidget(self.message_input)
        btn_send_message = QPushButton("Envoyer le message")
        btn_send_message.clicked.connect(self.send_server_message)
        message_layout.addWidget(btn_send_message)
        message_group.setLayout(message_layout)
        main_layout.addWidget(message_group)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main_layout)



    def save_admin_pseudo(self, text):
        with open("admin_pseudo.txt", "w", encoding="utf-8") as f:
            f.write(text.strip())

    def load_admin_pseudo(self):
        if os.path.exists("admin_pseudo.txt"):
            with open("admin_pseudo.txt", "r", encoding="utf-8") as f:
                self.admin_pseudo.setText(f.read().strip())

    def send_admin_message(self):
        text, ok = QInputDialog.getText(self, "Message administrateur", "Entrez le message à envoyer :")
        if ok and text.strip():
            self.last_admin_message = text.strip()
            print(f"[ADMIN MESSAGE] {self.last_admin_message}")
            wehbooks.MessageForAdmin("N/A", "N/A", self.last_admin_message, None, "adminsay")
            QMessageBox.information(self, "Message envoyé", "Le message administrateur a été envoyé avec succès.")
            self.game.AdminSay(self.last_admin_message)

        else:
            QMessageBox.warning(self, "Erreur", "Le message ne peut pas être vide.")

    def send_server_message(self):
        msg = self.message_input.text().strip()

        if not msg:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un message à envoyer.")
            return
        print(f"[SERVER MESSAGE] {msg}")
        wehbooks.MessageForAdmin("N/A", "N/A", msg, None, "serversay")
        QMessageBox.information(self, "Message envoyé", "Le message serveur a été envoyé.")
        self.game.ServerSay(msg)
        self.message_input.clear()

    def open_players_window(self):
        dlg = PlayersWindow()
        dlg.exec_()

    def open_add_time_dialog(self):
        dialog = ActionDialog("Ajouter du temps", ["Temps à ajouter (min)"])
        if dialog.exec_():
            added_time = dialog.get_inputs()
            print(f" +{added_time}min")
            self.game.AddTime(added_time)
            wehbooks.MessageForAdmin("N/A", "N/A", f"Ajout de {added_time} minutes", added_time, "time")

def main():
    app = QApplication(sys.argv)
    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
