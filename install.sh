#!/bin/bash

echo "This will install Desktop File Creator."
read -p "Do you want to continue? (y/n): " choice

if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo "Installing dependencies..."
pip install pyside6 --break-system-packages

echo "Creating directory..."
mkdir -p ~/Desktopfilecreator

echo "Moving Python file..."
mv desktop_file_creator.py ~/Desktopfilecreator/

echo "Making Python file executable..."
chmod +x ~/Desktopfilecreator/desktop_file_creator.py

echo "Creating .desktop file..."
mkdir -p ~/.local/share/applications

cat <<EOF > ~/.local/share/applications/desktopfilecreator.desktop
[Desktop Entry]
Name=Desktop file creator
Comment=Make .desktop files easily
Exec=$HOME/Desktopfilecreator/desktop_file_creator.py
Icon=terminal
Terminal=false
Type=Application
EOF

echo "Making .desktop file executable..."
chmod +x ~/.local/share/applications/desktopfilecreator.desktop

echo "Installation complete!"
