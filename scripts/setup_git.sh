#!/bin/bash
# Git setup script for STEM DREAM Aquaponics Control System

echo "🔧 Setting up Git repository for STEM DREAM Aquaponics System"
echo "============================================================="

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Copy project files to current directory if running from /home/claude
if [ -d "/mnt/project" ]; then
    echo "📋 Copying project files..."
    cp /mnt/project/*.py ./ 2>/dev/null
    cp /mnt/project/*.md ./ 2>/dev/null
    cp /mnt/project/*.txt ./ 2>/dev/null
    
    # Create templates directory if needed
    mkdir -p templates
    cp /mnt/project/*.html templates/ 2>/dev/null
    
    echo "✓ Project files copied"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Models (may be large - use Git LFS if needed)
models/*.tflite
models/*.h5
models/*.pb

# Temporary files
*.tmp
temp/

# Test outputs
test_*.jpg
test_*.png
test_output/

# Backup files
*_backup.*
backup/

# Configuration backups
config_backup.txt
EOF
    echo "✓ .gitignore created"
fi

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example..."
    cat > .env.example << 'EOF'
# STEM DREAM Aquaponics Control System - Environment Variables
# Copy this to .env and fill in your actual values

# LLM Settings (choose one)
LLM_BACKEND=mock  # Options: openai, anthropic, ollama, mock

# OpenAI Settings (if using OpenAI)
# LLM_API_KEY=sk-your-openai-api-key-here

# Anthropic Settings (if using Claude)
# LLM_API_KEY=sk-ant-your-anthropic-key-here

# Ollama Settings (if using local LLM)
# OLLAMA_URL=http://localhost:11434

# Email Alert Settings (optional)
# EMAIL_FROM=your-email@gmail.com
# EMAIL_PASSWORD=your-app-specific-password
# EMAIL_TO=recipient@email.com

# SMS Alert Settings via Twilio (optional)
# TWILIO_ACCOUNT_SID=your-account-sid
# TWILIO_AUTH_TOKEN=your-auth-token
# TWILIO_FROM=+1234567890
# SMS_TO=+1234567890

# Database Settings
# DATABASE_PATH=hydroponics.db
EOF
    echo "✓ .env.example created"
fi

# Create LICENSE if it doesn't exist
if [ ! -f "LICENSE" ]; then
    echo "📝 Creating MIT LICENSE..."
    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 STEM DREAM Aquaponics Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
    echo "✓ LICENSE created"
fi

# Create CONTRIBUTING.md
if [ ! -f "CONTRIBUTING.md" ]; then
    echo "📝 Creating CONTRIBUTING.md..."
    cat > CONTRIBUTING.md << 'EOF'
# Contributing to STEM DREAM Aquaponics Control System

Thank you for your interest in contributing! This project is designed for STEM education and we welcome contributions from educators, students, and aquaponics enthusiasts.

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs
- Include system details (Pi model, OS version, sensor types)
- Provide error messages and logs
- Describe expected vs actual behavior

### Suggesting Features
- Open an issue with the "enhancement" label
- Explain the use case and educational value
- Consider how it fits with the STEM learning goals

### Submitting Code
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test your changes thoroughly
4. Update documentation as needed
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints where practical
- Add docstrings to functions and classes
- Keep functions focused and testable

### Testing
- Run `python test_system.py` before committing
- Test in mock mode and with actual hardware if available
- Add tests for new features

### Documentation
- Update README.md for user-facing changes
- Update SETUP_GUIDE.md for hardware/setup changes
- Comment complex logic
- Include educational context where relevant

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aquaponics-control-system.git
cd aquaponics-control-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_system.py

# Run system
python main.py
```

## Educational Focus

This project is primarily for STEM education. When contributing:
- Consider how changes support learning objectives
- Maintain code readability for students
- Include comments explaining "why" not just "what"
- Think about classroom deployment scenarios

## Questions?

Open an issue or discussion on GitHub!

---

🌱 Thank you for helping make STEM education more accessible! 🐟
EOF
    echo "✓ CONTRIBUTING.md created"
fi

# Stage all files
echo "📦 Staging files for Git..."
git add .gitignore
git add README.md SETUP_GUIDE.md CONTRIBUTING.md LICENSE
git add *.py
git add requirements.txt
git add templates/ 2>/dev/null
git add test_system.py 2>/dev/null

echo ""
echo "✅ Git setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review staged files: git status"
echo "   2. Make initial commit: git commit -m 'Initial commit: STEM DREAM Aquaponics Control System'"
echo "   3. Create GitHub repository (if not done already)"
echo "   4. Add remote: git remote add origin https://github.com/YOUR_USERNAME/repo-name.git"
echo "   5. Push: git push -u origin main"
echo ""
echo "💡 Before pushing:"
echo "   - Review all files with: git status"
echo "   - Ensure .env file is NOT staged (should be in .gitignore)"
echo "   - Test the system: python test_system.py"
echo ""
