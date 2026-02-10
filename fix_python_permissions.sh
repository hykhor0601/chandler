#!/bin/bash
# Fix Python.app Info.plist to include Speech Recognition permissions
# Works with both official Python.org and Homebrew installations

echo "🔍 Detecting Python installation..."

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "   Python version: $PYTHON_VERSION"

# Try to find Info.plist in common locations
PYTHON_INFO_PLIST=""

# Option 1: Official Python.org installation
OFFICIAL_PLIST="/Library/Frameworks/Python.framework/Versions/${PYTHON_VERSION}/Resources/Python.app/Contents/Info.plist"
if [ -f "$OFFICIAL_PLIST" ]; then
    PYTHON_INFO_PLIST="$OFFICIAL_PLIST"
    echo "   Found: Official Python.org installation"
fi

# Option 2: Homebrew installation (current version)
if [ -z "$PYTHON_INFO_PLIST" ]; then
    HOMEBREW_PLIST=$(find /opt/homebrew/Cellar/python@${PYTHON_VERSION} -name "Info.plist" -path "*/Python.app/Contents/Info.plist" 2>/dev/null | head -1)
    if [ -n "$HOMEBREW_PLIST" ]; then
        PYTHON_INFO_PLIST="$HOMEBREW_PLIST"
        echo "   Found: Homebrew installation"
    fi
fi

# Option 3: Intel Homebrew
if [ -z "$PYTHON_INFO_PLIST" ]; then
    INTEL_HOMEBREW_PLIST=$(find /usr/local/Cellar/python@${PYTHON_VERSION} -name "Info.plist" -path "*/Python.app/Contents/Info.plist" 2>/dev/null | head -1)
    if [ -n "$INTEL_HOMEBREW_PLIST" ]; then
        PYTHON_INFO_PLIST="$INTEL_HOMEBREW_PLIST"
        echo "   Found: Homebrew (Intel) installation"
    fi
fi

# Check if we found it
if [ -z "$PYTHON_INFO_PLIST" ]; then
    echo "❌ Error: Could not find Python.app Info.plist"
    echo ""
    echo "Searching all Python installations..."
    find /Library/Frameworks/Python.framework -name "Info.plist" 2>/dev/null
    find /opt/homebrew/Cellar -name "Info.plist" -path "*Python.app*" 2>/dev/null
    find /usr/local/Cellar -name "Info.plist" -path "*Python.app*" 2>/dev/null
    exit 1
fi

echo "   Location: $PYTHON_INFO_PLIST"
echo ""

# Backup original
echo "📦 Creating backup..."
if [ ! -f "$PYTHON_INFO_PLIST.backup" ]; then
    sudo cp "$PYTHON_INFO_PLIST" "$PYTHON_INFO_PLIST.backup"
    echo "   ✓ Backup created: $PYTHON_INFO_PLIST.backup"
else
    echo "   ⚠️  Backup already exists, skipping"
fi

echo ""
echo "✏️  Adding permissions to Info.plist..."

# Add Speech Recognition permission
sudo /usr/libexec/PlistBuddy -c "Add :NSSpeechRecognitionUsageDescription string 'Chandler uses speech recognition to detect the wake word (hey chandler) and transcribe your voice commands.'" "$PYTHON_INFO_PLIST" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Added NSSpeechRecognitionUsageDescription"
else
    # Already exists, update it
    sudo /usr/libexec/PlistBuddy -c "Set :NSSpeechRecognitionUsageDescription 'Chandler uses speech recognition to detect the wake word (hey chandler) and transcribe your voice commands.'" "$PYTHON_INFO_PLIST"
    echo "   ✓ Updated NSSpeechRecognitionUsageDescription"
fi

# Add Microphone permission
sudo /usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string 'Chandler needs microphone access to listen for the wake word and record your voice commands.'" "$PYTHON_INFO_PLIST" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Added NSMicrophoneUsageDescription"
else
    # Already exists, update it
    sudo /usr/libexec/PlistBuddy -c "Set :NSMicrophoneUsageDescription 'Chandler needs microphone access to listen for the wake word and record your voice commands.'" "$PYTHON_INFO_PLIST"
    echo "   ✓ Updated NSMicrophoneUsageDescription"
fi

echo ""
echo "🎉 Permissions successfully added!"
echo ""
echo "📋 Next steps:"
echo "   1. Reset TCC cache:"
echo "      tccutil reset All org.python.python"
echo ""
echo "   2. Launch Chandler:"
echo "      chandler-voice"
echo ""
echo "   3. Grant permissions when prompted"
echo ""
