#!/bin/bash
# Script to create a Desktop Shortcut for GhostWire on Ubuntu/Linux

# Get the absolute path of the current directory (repo root)
REPO_DIR=$(pwd)
ICON_PATH="$REPO_DIR/static/images/cyberpunk_app_icon.png"
DESKTOP_FILE="$HOME/Desktop/GhostWire.desktop"

echo ">> Creating Shortcut at $DESKTOP_FILE..."

# Create the .desktop file content
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GhostWire Node
Comment=Launch Secure SaaS Satellite
Exec=gnome-terminal -- bash -c "cd '$REPO_DIR'; python3 deploy.py; exec bash"
Icon=$ICON_PATH
Terminal=false
Categories=Network;Utility;
StartupNotify=true
EOF

# Make it executable (Trusted)
chmod +x "$DESKTOP_FILE"

echo ">> SHORTCUT DEPLOYED."
echo ">> You should see the 'GhostWire Node' icon on your desktop."
echo ">> Double-click it to launch the server anytime."
