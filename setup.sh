#!/bin/bash

# Maghrib News Aggregator - Quick Start Script

echo "==================================="
echo "Maghrib News Aggregator Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
required_version="3.10"

if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Create necessary directories
mkdir -p data logs

echo "==================================="
echo "✅ Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the scraper:"
echo "   python main.py"
echo ""
echo "3. Start the API server:"
echo "   python api.py"
echo ""
echo "4. Access the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "Happy scraping! 🇲🇦"
