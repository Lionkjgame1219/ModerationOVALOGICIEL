# Discord Webhook Setup Guide

This guide explains how to set up Discord webhook notifications for the C2 Server Admin Tool.

## What is a Discord Webhook?

A Discord webhook allows the admin tool to send notifications directly to a Discord channel when administrative actions are performed (bans, kicks, admin messages, etc.).

## Dual Webhook Support

The admin tool supports **two webhook slots**:
- **Primary Webhook**: The main Discord server for notifications
- **Secondary Webhook**: An optional second Discord server for notifications

Both webhooks will receive the same notifications simultaneously, allowing you to send alerts to multiple Discord servers.

## Setting Up Discord Webhooks

### Step 1: Create Webhooks in Discord

For each Discord server where you want notifications:

1. Open Discord and navigate to the server where you want to receive notifications
2. Right-click on the channel where you want notifications to appear
3. Select "Edit Channel"
4. Go to the "Integrations" tab
5. Click "Create Webhook"
6. Give your webhook a name (e.g., "C2 Admin Bot Primary" or "C2 Admin Bot Secondary")
7. Optionally, set a custom avatar
8. Copy the webhook URL (it should start with `https://discord.com/api/webhooks/`)

Repeat this process for each Discord server you want to configure.

### Step 2: Configure the Admin Tool

When you first start the admin tool, you'll be prompted to enter your Discord webhook URLs:

1. **First Launch**:
   - A dialog will appear asking for your **primary** Discord webhook URL
   - Paste the URL you copied from Discord, or leave it empty to disable notifications
   - If you entered a primary URL, you'll be prompted for a **secondary** webhook URL (optional)
   - You can leave the secondary URL empty if you only want to use one webhook

2. **Reconfigure Later**: You can change the webhook URLs anytime by:
   - Clicking the "🔗 Configure Discord Webhook" button in the admin dashboard
   - Entering new URLs for both primary and secondary webhooks
   - Leaving either field empty to disable that specific webhook

### Step 3: Test the Configuration

After configuring the webhook:

1. The tool will attempt to initialize the webhook connection
2. You'll see a success or error message
3. Try performing an admin action (like sending an admin message) to test notifications

## Configuration File

The webhook URLs are stored in a file called `localconfig` in the same directory as the admin tool. This file contains:
- Line 1: Your primary Discord webhook URL (or "None" if disabled)
- Line 2: Your secondary Discord webhook URL (or "None" if disabled)

Example `localconfig` file:
```
https://discord.com/api/webhooks/123456789/abcdefghijklmnop
https://discord.com/api/webhooks/987654321/zyxwvutsrqponmlk
```

Or with only primary webhook:
```
https://discord.com/api/webhooks/123456789/abcdefghijklmnop
None
```

## Supported Notifications

The following admin actions will trigger Discord notifications:

- **Ban**: Player bans with duration and reason
- **Unban**: Player unbans
- **Kick**: Player kicks with reason
- **Admin Say**: Administrative messages sent to the server
- **Server Say**: Server messages
- **Add Time**: Time additions to the game

## Reason Presets

The admin tool includes a preset system for commonly used ban/kick reasons, making moderation more efficient.

### Using Presets

When banning or kicking a player:

1. **Loading Presets**: Click any "Load X" button (where X is 0-9) to load a saved reason
2. **Saving Presets**: Enter a reason in the text field, then click "Save X" to save it to slot X
3. **Visual Indicators**:
   - Filled preset slots have a light green background
   - Empty slots use the default button style
   - Hover over Load buttons to see preset contents in tooltips

### Preset Storage

- Presets are stored in `reason_presets.json` in the application directory
- 10 preset slots available (0-9)
- Presets persist between application restarts
- Can be shared between team members by copying the JSON file

### Example Presets

Common reasons you might want to save as presets:
- Slot 0: "Cheating/Hacking"
- Slot 1: "Toxic behavior in chat"
- Slot 2: "Team killing"
- Slot 3: "Griefing other players"
- Slot 4: "Inappropriate language"
- Slot 5: "Exploiting game bugs"
- Slot 6: "Spamming chat"
- Slot 7: "Disruptive gameplay"
- Slot 8: "Harassment"
- Slot 9: "General rule violation"

## Troubleshooting

### Common Issues

1. **"Invalid URL" Error**
   - Make sure the URL starts with `https://discord.com/api/webhooks/`
   - Verify you copied the complete URL from Discord

2. **"Unable to initialize Discord webhook" Error**
   - Check your internet connection
   - Verify the webhook URL is still valid in Discord
   - Make sure the webhook hasn't been deleted

3. **No Notifications Appearing**
   - Check that the webhook is pointing to the correct Discord channel
   - Verify the bot has permission to send messages in that channel
   - Look for error messages in the admin tool console

### Disabling Notifications

To disable Discord notifications:
1. Click "🔗 Configure Discord Webhook" in the admin dashboard
2. Clear both URL fields (leave them empty)
3. Click OK

To disable only one webhook:
1. Click "🔗 Configure Discord Webhook" in the admin dashboard
2. Clear the specific URL field you want to disable
3. Keep the other URL field if you want to maintain that webhook
4. Click OK

## Security Notes

- Keep your webhook URLs private - anyone with the URLs can send messages to your Discord channels
- If you suspect a URL has been compromised, delete the webhook in Discord and create a new one
- The webhook URLs are stored in plain text in the `localconfig` file
- Both primary and secondary webhooks receive the same notifications, so ensure both Discord servers should have access to this information
