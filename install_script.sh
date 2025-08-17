#!/bin/bash

# Ultra-Fast Port Scanner - Quick Install Script
# Usage: curl -sSL https://raw.githubusercontent.com/yourusername/ultra-fast-port-scanner/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/ultra-fast-port-scanner"
INSTALL_DIR="$HOME/.local/bin"
SCANNER_NAME="ultra-scanner"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   Ultra-Fast Port Scanner                   ║"
echo "║                      Quick Installer                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python 3.7+ is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
    
    # Check if version is 3.7+
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)'; then
        echo -e "${GREEN}✓ Python version is compatible${NC}"
    else
        echo -e "${RED}✗ Python 3.7+ required, found $PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.7+ first.${NC}"
    exit 1
fi

# Create install directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Download the scanner
echo -e "${YELLOW}Downloading Ultra-Fast Port Scanner...${NC}"
if command -v curl &> /dev/null; then
    curl -sSL "$REPO_URL/raw/main/ultra_scanner.py" -o "$INSTALL_DIR/$SCANNER_NAME"
elif command -v wget &> /dev/null; then
    wget -q "$REPO_URL/raw/main/ultra_scanner.py" -O "$INSTALL_DIR/$SCANNER_NAME"
else
    echo -e "${RED}✗ Neither curl nor wget found. Please install one of them.${NC}"
    exit 1
fi

# Make executable
chmod +x "$INSTALL_DIR/$SCANNER_NAME"
echo -e "${GREEN}✓ Ultra-Fast Port Scanner installed to $INSTALL_DIR/$SCANNER_NAME${NC}"

# Check if install directory is in PATH
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    echo -e "${GREEN}✓ Installation directory is in PATH${NC}"
else
    echo -e "${YELLOW}⚠ Adding $INSTALL_DIR to PATH...${NC}"
    
    # Add to PATH in shell profile
    SHELL_PROFILE=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [[ -f "$HOME/.profile" ]]; then
        SHELL_PROFILE="$HOME/.profile"
    fi
    
    if [[ -n "$SHELL_PROFILE" ]]; then
        echo "export PATH=\"$PATH:$INSTALL_DIR\"" >> "$SHELL_PROFILE"
        echo -e "${GREEN}✓ Added to $SHELL_PROFILE${NC}"
        echo -e "${YELLOW}Please run: source $SHELL_PROFILE${NC}"
    else
        echo -e "${YELLOW}Please add $INSTALL_DIR to your PATH manually${NC}"
    fi
fi

# Test installation
echo -e "${YELLOW}Testing installation...${NC}"
if "$INSTALL_DIR/$SCANNER_NAME" --help &> /dev/null; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

# Success message
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Installation Complete!                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}Quick Start:${NC}"
echo -e "  ${SCANNER_NAME} scanme.nmap.org"
echo -e "  ${SCANNER_NAME} target.com -p 1-65535"
echo -e "  ${SCANNER_NAME} 192.168.1.1 -p 1-65535 --export json"
echo ""
echo -e "${BLUE}Documentation:${NC} $REPO_URL"
echo -e "${BLUE}Report Issues:${NC} $REPO_URL/issues"
echo ""
echo -e "${GREEN}Happy Scanning! 🚀${NC}"
