#!/bin/bash
# EMERGENCY: Restore Python immediately

echo "🚨 RESTORING PYTHON..."

BACKUP="/Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist.backup"
TARGET="/Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/Info.plist"

if [ ! -f "$BACKUP" ]; then
    echo "❌ Backup not found at $BACKUP"
    exit 1
fi

echo "Restoring from: $BACKUP"
echo "To: $TARGET"

sudo cp "$BACKUP" "$TARGET"

if [ $? -eq 0 ]; then
    echo "✅ RESTORED"
    echo ""
    echo "Testing..."
    python3 --version
    echo ""
    echo "If python3 works now, the fix was successful."
else
    echo "❌ FAILED - try manually:"
    echo "sudo cp \"$BACKUP\" \"$TARGET\""
fi
