# Fixing Speech Recognition Permission Crash

## The Problem

macOS requires all apps that access privacy-sensitive features (like Speech Recognition and Microphone) to declare **why** they need access in their Info.plist file.

When you run `chandler-voice` as a Python script, macOS checks the **Python.app's Info.plist** instead of Chandler's. Since Python.app doesn't have the required permission descriptions, it crashes immediately.

**Error from crash report:**
```
This app has crashed because it attempted to access privacy-sensitive data
without a usage description. The app's Info.plist must contain an
NSSpeechRecognitionUsageDescription key with a string value explaining
to the user how the app uses this data.
```

## Solution 1: Add Permissions to Python.app (Quick Fix)

### Step 1: Run the Fix Script

```bash
cd /Users/zhaopin/HY/chanlder
./fix_python_permissions.sh
```

This will:
1. Backup Python.app's original Info.plist
2. Add `NSSpeechRecognitionUsageDescription`
3. Add `NSMicrophoneUsageDescription`

### Step 2: Reset Permissions (Important!)

After modifying Info.plist, you need to reset the app's permissions cache:

```bash
# Kill any running Python processes
pkill Python

# Reset TCC database for Python.app
tccutil reset All org.python.python

# Or reset system-wide (if above doesn't work)
sudo tccutil reset All
```

### Step 3: Launch Chandler

```bash
source .venv/bin/activate
chandler-voice
```

You should now see the permission dialogs instead of crashes!

## Solution 2: Manual Fix (If Script Doesn't Work)

### Edit Info.plist Manually

```bash
# Open Info.plist in your editor
sudo nano /Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist
```

Add these keys before the closing `</dict></plist>`:

```xml
<key>NSSpeechRecognitionUsageDescription</key>
<string>Chandler uses speech recognition to detect the wake word (hey chandler) and transcribe your voice commands.</string>

<key>NSMicrophoneUsageDescription</key>
<string>Chandler needs microphone access to listen for the wake word and record your voice commands.</string>
```

Save and reset permissions as in Step 2 above.

## Solution 3: Create a Proper .app Bundle (Best Long-Term)

For production use, create a standalone .app bundle:

### Using py2app

1. **Install py2app:**
   ```bash
   source .venv/bin/activate
   pip install py2app
   ```

2. **Create setup.py for app:**
   ```bash
   cd /Users/zhaopin/HY/chanlder
   py2applet --make-setup chandler/menu_bar_app.py
   ```

3. **Edit setup.py to add permissions:**
   ```python
   OPTIONS = {
       'argv_emulation': False,
       'plist': {
           'CFBundleName': 'Chandler',
           'CFBundleDisplayName': 'Chandler Voice Assistant',
           'CFBundleIdentifier': 'com.chandler.voiceassistant',
           'CFBundleVersion': '1.0.0',
           'CFBundleShortVersionString': '1.0.0',
           'NSMicrophoneUsageDescription': 'Chandler needs microphone access to listen for the wake word and record your voice commands.',
           'NSSpeechRecognitionUsageDescription': 'Chandler uses speech recognition to detect the wake word (hey chandler) and transcribe your voice commands.',
           'LSUIElement': True,  # Makes it a menu bar-only app
       },
   }
   ```

4. **Build the app:**
   ```bash
   python setup.py py2app
   ```

5. **Run the standalone app:**
   ```bash
   open dist/Chandler.app
   ```

## Verification

After applying the fix:

1. **Check permissions were added:**
   ```bash
   /usr/libexec/PlistBuddy -c "Print :NSSpeechRecognitionUsageDescription" \
     /Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist
   ```

   Should output: `Chandler uses speech recognition...`

2. **Launch and grant permissions:**
   ```bash
   source .venv/bin/activate
   chandler-voice
   ```

3. **You should see:**
   - Dialog: "Python.app would like to access Speech Recognition"
   - Click "OK"
   - Dialog: "Python.app would like to access the Microphone"
   - Click "OK"
   - Chandler icon appears in menu bar ✓

## Troubleshooting

### Still crashing after fix?

1. **Make sure you reset TCC:**
   ```bash
   tccutil reset All org.python.python
   ```

2. **Reboot (nuclear option):**
   ```bash
   sudo reboot
   ```

### Permission dialogs not appearing?

Check if permissions are already denied:
```bash
# Open System Settings
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
```

Look for "Python" in the list and enable it.

### Restore original Info.plist?

```bash
sudo cp /Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist.backup \
       /Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist
```

## Why This Happens

**macOS Privacy Model:**
- Any app accessing privacy-sensitive APIs must declare usage in Info.plist
- Required keys:
  - `NSMicrophoneUsageDescription` - Why you need mic
  - `NSSpeechRecognitionUsageDescription` - Why you need speech recognition
- Without these keys → **instant crash** (not just denied permission)

**Python Script Limitation:**
- Python scripts inherit Python.app's Info.plist
- Python.app doesn't have speech/mic descriptions by default
- Our script can't provide its own Info.plist when run directly

**Solutions:**
1. ✅ **Quick**: Modify Python.app's Info.plist (affects all Python scripts)
2. ✅ **Better**: Bundle as standalone .app (isolated permissions)
3. ❌ **Won't work**: Runtime permission requests (Info.plist is required)

## Recommended Approach

**For Development:**
- Use Solution 1 (modify Python.app's Info.plist)
- Quick and works for testing

**For Distribution:**
- Use Solution 3 (create .app bundle with py2app)
- Professional, standalone app
- Each user gets clean permission dialogs
- No need to modify system Python

---

**Ready to fix?** Run:
```bash
./fix_python_permissions.sh
source .venv/bin/activate
chandler-voice
```
