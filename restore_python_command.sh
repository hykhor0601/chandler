#!/bin/bash
# Restore the 'python' command by creating symlink to python3

echo "Creating 'python' symlink..."

# Check if python symlink already exists
if [ -L "/opt/homebrew/bin/python" ]; then
    echo "✓ 'python' symlink already exists"
    ls -la /opt/homebrew/bin/python
    exit 0
fi

# Create symlink
ln -s /opt/homebrew/bin/python3 /opt/homebrew/bin/python

if [ $? -eq 0 ]; then
    echo "✅ 'python' command restored!"
    echo ""
    python --version
else
    echo "❌ Failed to create symlink (permission issue)"
    echo "Try manually:"
    echo "  ln -s /opt/homebrew/bin/python3 /opt/homebrew/bin/python"
fi
