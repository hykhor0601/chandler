#!/bin/bash
# Restore Python from backup (undo fix_python_permissions.sh damage)

echo "🔍 Finding Python installation..."

# Get Python version (if python3 still works at all)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2 2>/dev/null || echo "3.13")
echo "   Detected version: $PYTHON_VERSION"

# Find the modified Info.plist
PYTHON_INFO_PLIST=""

# Check common locations
OFFICIAL_PLIST="/Library/Frameworks/Python.framework/Versions/${PYTHON_VERSION}/Resources/Python.app/Contents/Info.plist"
if [ -f "$OFFICIAL_PLIST.backup" ]; then
    PYTHON_INFO_PLIST="$OFFICIAL_PLIST"
    echo "   Found: Official Python.org installation"
fi

if [ -z "$PYTHON_INFO_PLIST" ]; then
    HOMEBREW_PLIST=$(find /opt/homebrew/Cellar/python@${PYTHON_VERSION} -name "Info.plist.backup" -path "*/Python.app/Contents/*" 2>/dev/null | head -1 | sed 's/.backup$//')
    if [ -n "$HOMEBREW_PLIST" ]; then
        PYTHON_INFO_PLIST="$HOMEBREW_PLIST"
        echo "   Found: Homebrew installation"
    fi
fi

if [ -z "$PYTHON_INFO_PLIST" ]; then
    INTEL_HOMEBREW_PLIST=$(find /usr/local/Cellar/python@${PYTHON_VERSION} -name "Info.plist.backup" -path "*/Python.app/Contents/*" 2>/dev/null | head -1 | sed 's/.backup$//')
    if [ -n "$INTEL_HOMEBREW_PLIST" ]; then
        PYTHON_INFO_PLIST="$INTEL_HOMEBREW_PLIST"
        echo "   Found: Homebrew (Intel) installation"
    fi
fi

# Check if backup exists
if [ -z "$PYTHON_INFO_PLIST" ]; then
    echo "❌ Error: Could not find Info.plist backup"
    echo ""
    echo "Searching for backups..."
    find /Library/Frameworks/Python.framework -name "Info.plist.backup" 2>/dev/null
    find /opt/homebrew/Cellar -name "Info.plist.backup" -path "*Python.app*" 2>/dev/null
    find /usr/local/Cellar -name "Info.plist.backup" -path "*Python.app*" 2>/dev/null
    echo ""
    echo "If no backup found, you need to reinstall Python:"
    echo "  brew reinstall python@${PYTHON_VERSION}"
    echo "  or download from python.org"
    exit 1
fi

echo "   Location: $PYTHON_INFO_PLIST"
echo ""

# Check if backup exists
if [ ! -f "$PYTHON_INFO_PLIST.backup" ]; then
    echo "❌ Error: Backup not found at $PYTHON_INFO_PLIST.backup"
    echo ""
    echo "Python needs to be reinstalled:"
    echo "  brew reinstall python@${PYTHON_VERSION}"
    exit 1
fi

echo "📦 Restoring from backup..."
sudo cp "$PYTHON_INFO_PLIST.backup" "$PYTHON_INFO_PLIST"

if [ $? -eq 0 ]; then
    echo "   ✓ Python.app Info.plist restored"
else
    echo "   ✗ Failed to restore (permission denied?)"
    echo "   Try: sudo cp \"$PYTHON_INFO_PLIST.backup\" \"$PYTHON_INFO_PLIST\""
    exit 1
fi

echo ""
echo "🔄 Resetting TCC cache..."
tccutil reset All org.python.python 2>/dev/null

echo ""
echo "✅ Python restored!"
echo ""
echo "Test it:"
echo "  python3 --version"
echo ""
