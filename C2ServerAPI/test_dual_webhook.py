#!/usr/bin/env python3
"""
Test script for dual Discord webhook configuration
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

import wehbooks

def test_dual_webhook_configuration():
    """Test the dual webhook configuration and functionality"""
    print("Testing dual Discord webhook configuration...")
    
    # Create a QApplication for the dialogs
    app = QApplication(sys.argv)
    
    # Test webhook initialization
    result = wehbooks.initialize_webhook()
    
    print(f"Webhook initialization result: {result}")
    
    # Check individual webhook status
    primary_active = wehbooks.webhook_primary is not None
    secondary_active = wehbooks.webhook_secondary is not None
    
    print(f"Primary webhook active: {primary_active}")
    print(f"Secondary webhook active: {secondary_active}")
    
    if result:
        print("✅ At least one webhook initialized successfully!")
        
        # Test sending different types of messages
        test_messages = [
            ("ban", "TEST_BAN_ID", "TestBanUser", "Testing ban notification", "24"),
            ("kick", "TEST_KICK_ID", "TestKickUser", "Testing kick notification", None),
            ("adminsay", "N/A", "N/A", "Testing admin message", None),
            ("serversay", "N/A", "N/A", "Testing server message", None),
            ("time", "N/A", "N/A", "Testing time addition", "30")
        ]
        
        for msg_type, user_id, username, reason, duration in test_messages:
            try:
                print(f"Sending test {msg_type} message...")
                wehbooks.MessageForAdmin(user_id, username, reason, duration, msg_type)
                print(f"✅ {msg_type} message sent successfully!")
            except Exception as e:
                print(f"❌ Failed to send {msg_type} message: {e}")
    else:
        print("ℹ️ No webhooks configured or initialization failed")
    
    # Display configuration file contents
    if os.path.exists("localconfig"):
        print("\n📄 Configuration file contents:")
        with open("localconfig", 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            for i, line in enumerate(lines, 1):
                webhook_type = "Primary" if i == 1 else "Secondary"
                if line != "None":
                    print(f"  {webhook_type}: {line[:50]}...")
                else:
                    print(f"  {webhook_type}: Disabled")
    else:
        print("ℹ️ No configuration file found")
    
    app.quit()

def create_test_config():
    """Create a test configuration file for testing purposes"""
    print("Creating test configuration...")
    
    # This creates a test config with placeholder URLs
    # Replace these with actual webhook URLs for testing
    test_config = """None
None"""
    
    with open("localconfig", 'w', encoding='utf-8') as f:
        f.write(test_config)
    
    print("✅ Test configuration created. Edit 'localconfig' file with real webhook URLs for testing.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-test-config":
        create_test_config()
    else:
        test_dual_webhook_configuration()
