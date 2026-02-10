#!/bin/bash
# Verify installation after Python restoration

echo "🔍 Checking Python installation..."
echo ""

# Test python3
echo "Testing python3..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ python3 not working"
    exit 1
fi
echo "✓ python3 works"
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "⚠️  .venv doesn't exist - creating it..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create .venv"
        exit 1
    fi
    echo "✓ .venv created"
fi

# Activate and test
echo "Testing virtual environment..."
source .venv/bin/activate

echo "Python in venv: $(which python)"
python --version
echo ""

# Check if chandler is installed
echo "Checking if chandler is installed..."
pip list | grep chandler
if [ $? -ne 0 ]; then
    echo "⚠️  chandler not installed - installing..."
    pip install -e .
    echo "✓ chandler installed"
else
    echo "✓ chandler already installed"
fi
echo ""

# Test CLI mode
echo "Testing CLI mode..."
which chandler
if [ $? -eq 0 ]; then
    echo "✓ 'chandler' command available"
else
    echo "❌ 'chandler' command not found"
fi

echo ""
echo "✅ Installation check complete!"
echo ""
echo "To use Chandler CLI mode:"
echo "  source .venv/bin/activate"
echo "  chandler"
echo ""
echo "Note: Voice mode (chandler-voice) will still crash due to the"
echo "      Info.plist issue. DO NOT run fix_python_permissions.sh again."
