#!/bin/bash

set -e

BIN="love-pm"
URL="https://raw.githubusercontent.com/TRC-Loop/love-pm/main/src/love-pm.py"
DEST="/usr/local/bin/$BIN"

echo "[*] Installing love-pm..."

if [ ! -w "/usr/local/bin" ]; then
    echo "[!] Need sudo permissions."
    sudo bash "$0" "$@"
    exit 0
fi

curl -fsSL "$URL" -o "$DEST" || { echo "[X] Download failed."; exit 1; }
chmod +x "$DEST"

echo "[✔] Installed at $DEST"
echo "[i] Run with: $BIN"
