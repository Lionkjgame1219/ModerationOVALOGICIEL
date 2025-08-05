# Reason Presets Guide

This guide explains how to use the reason preset system in the C2 Server Admin Tool for efficient player moderation.

## Overview

The reason preset system allows administrators to save commonly used ban/kick reasons and quickly apply them when moderating players. This feature significantly speeds up the moderation process and ensures consistency in reason formatting.

## Features

- **10 Preset Slots**: Save up to 10 different reasons (slots 0-9)
- **Quick Loading**: One-click loading of saved reasons
- **Visual Indicators**: See which slots contain presets at a glance
- **Tooltips**: Hover over load buttons to preview preset contents
- **Persistent Storage**: Presets are saved between application restarts

## How to Use Presets

### Accessing the Preset Interface

1. Open the admin dashboard
2. Click "👥 Connected Players" to view the player list
3. Click on any player to open the action dialog
4. Choose "Ban" or "Kick" to open the moderation dialog
5. The preset buttons are located below the reason input field

### Saving a Preset

1. Enter your desired reason in the "Reason" text field
2. Click one of the "Save X" buttons (where X is 0-9)
3. A confirmation message will appear
4. The preset is now saved and ready for future use

### Loading a Preset

1. Click one of the "Load X" buttons to load a saved preset
2. The reason text field will be populated with the preset content
3. You can modify the loaded text if needed before applying the action

### Visual Indicators

- **Green Background**: Load buttons with a light green background contain saved presets
- **Default Background**: Empty preset slots use the default button style
- **Tooltips**: Hover over any Load button to see a preview of the preset content

## Preset Management

### File Location

Presets are stored in `reason_presets.json` in the same directory as the admin tool. This file contains:

```json
{
  "0": "Cheating/Hacking",
  "1": "Toxic behavior in chat",
  "2": "Team killing repeatedly",
  "3": "Griefing other players",
  "4": "Inappropriate language"
}
```

### Sharing Presets

To share presets with other administrators:

1. Copy the `reason_presets.json` file
2. Place it in the admin tool directory on other machines
3. Restart the admin tool to load the shared presets

### Backup and Restore

- **Backup**: Copy `reason_presets.json` to a safe location
- **Restore**: Replace the current file with your backup
- **Reset**: Delete `reason_presets.json` to clear all presets

## Best Practices

### Organizing Your Presets

Consider organizing presets by severity or category:

- **Slots 0-2**: Severe violations (cheating, harassment, etc.)
- **Slots 3-5**: Moderate violations (toxic behavior, griefing, etc.)
- **Slots 6-9**: Minor violations (chat spam, minor rule breaks, etc.)

### Recommended Preset Examples

Here are some commonly used presets you might want to save:

1. **Slot 0**: "Cheating/Hacking - Use of unauthorized software"
2. **Slot 1**: "Toxic behavior - Harassment and inappropriate conduct"
3. **Slot 2**: "Team killing - Intentionally killing teammates"
4. **Slot 3**: "Griefing - Deliberately disrupting gameplay"
5. **Slot 4**: "Inappropriate language - Offensive or discriminatory speech"
6. **Slot 5**: "Exploiting - Abuse of game mechanics or bugs"
7. **Slot 6**: "Chat spam - Excessive or disruptive messaging"
8. **Slot 7**: "Disruptive gameplay - Interfering with normal play"
9. **Slot 8**: "AFK/Idle - Extended inactivity affecting team"
10. **Slot 9**: "General rule violation - Breaking server rules"

### Consistency Tips

- Use consistent formatting across all presets
- Include specific details when helpful
- Keep reasons concise but descriptive
- Review and update presets regularly

## Troubleshooting

### Presets Not Saving

- Check that the application has write permissions in its directory
- Ensure the `reason_presets.json` file isn't read-only
- Verify there's sufficient disk space

### Presets Not Loading

- Check that `reason_presets.json` exists and is valid JSON
- Restart the admin tool if presets seem outdated
- Verify file encoding is UTF-8

### Lost Presets

- Check for backup copies of `reason_presets.json`
- Look for the file in the correct application directory
- Recreate commonly used presets if necessary

## Technical Details

### File Format

The preset file uses JSON format with string keys (slot numbers) and string values (reason text):

```json
{
  "0": "First preset reason",
  "1": "Second preset reason",
  "9": "Tenth preset reason"
}
```

### Character Encoding

- File encoding: UTF-8
- Supports international characters and emojis
- Automatic escaping of special JSON characters

### Storage Limitations

- Maximum 10 preset slots (0-9)
- No practical limit on reason text length
- File size typically under 1KB for normal usage

## Integration with Discord Webhooks

When using presets with Discord webhook notifications:

- Preset reasons appear in Discord notifications exactly as saved
- Formatting (including special characters) is preserved
- Consider Discord's message length limits when creating long presets

This preset system streamlines the moderation process while maintaining consistency and professionalism in administrative actions.
