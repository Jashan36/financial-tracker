# Financial Tracker - Windows Setup Guide

This guide will help you set up and run the Financial Tracker application on Windows.

## 🚀 Quick Start (Recommended)

### Option 1: Use the Batch File (Easiest)
1. **Double-click** `start.bat`
2. Wait for dependencies to install
3. The application will start automatically
4. Open your browser and go to: `http://localhost:5000`

### Option 2: Use the Python Script
1. **Double-click** `start.py`
2. Follow the on-screen instructions
3. The script will check dependencies and start the app

## 📋 Prerequisites

### 1. Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify installation by opening Command Prompt and typing: `python --version`

### 2. Install Git (Optional)
- Download from [git-scm.com](https://git-scm.com/download/win)
- Useful for updating the application

## 🛠️ Manual Setup

### Step 1: Open Command Prompt
- Press `Win + R`, type `cmd`, press Enter
- Or search for "Command Prompt" in Start menu

### Step 2: Navigate to Project Directory
```cmd
cd C:\Users\YourUsername\Desktop\financial-tracker
```

### Step 3: Create Virtual Environment (Recommended)
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Run the Application
```cmd
python app.py
```

### Step 6: Open in Browser
- Open your web browser
- Go to: `http://localhost:5000`

## 🔧 Troubleshooting

### Common Issues

#### 1. "Python is not recognized"
- **Solution**: Reinstall Python and check "Add Python to PATH"
- **Alternative**: Use full path: `C:\Python39\python.exe app.py`

#### 2. "pip is not recognized"
- **Solution**: Install pip: `python -m ensurepip --upgrade`
- **Alternative**: Use: `python -m pip install -r requirements.txt`

#### 3. "Permission denied"
- **Solution**: Run Command Prompt as Administrator
- **Alternative**: Check antivirus software settings

#### 4. "Port 5000 already in use"
- **Solution**: Close other applications using port 5000
- **Alternative**: Modify `app.py` to use a different port

#### 5. "Module not found" errors
- **Solution**: Ensure all dependencies are installed
- **Command**: `pip install -r requirements.txt`

### Performance Issues

#### Slow Processing
- Close unnecessary applications
- Ensure sufficient RAM (4GB+ recommended)
- For large files, wait for processing to complete

#### Browser Issues
- Use modern browsers (Chrome, Firefox, Edge)
- Enable JavaScript
- Clear browser cache if needed

## 📁 File Structure
```
financial-tracker/
├── start.bat              # Windows startup script
├── start.py               # Python startup script
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── sample_data.csv        # Sample data for testing
├── README.md              # Main documentation
└── SETUP_WINDOWS.md       # This file
```

## 🧪 Testing the Application

### Run Test Suite
```cmd
python test_app.py
```

### Test with Sample Data
1. Start the application
2. Upload `sample_data.csv`
3. Verify transactions are processed correctly
4. Check charts and recommendations

## 🔄 Updating the Application

### Option 1: Git (if installed)
```cmd
git pull origin main
```

### Option 2: Manual Update
1. Download new version
2. Replace old files
3. Reinstall dependencies: `pip install -r requirements.txt`

## 📞 Getting Help

### Check Logs
- Application logs appear in Command Prompt
- Look for error messages and warnings

### Common Commands
```cmd
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Update pip
python -m pip install --upgrade pip

# Install specific package
pip install package_name
```

### Support Resources
1. Check the main README.md
2. Review error messages in Command Prompt
3. Ensure all prerequisites are met
4. Try running `test_app.py` for diagnostics

## 🎯 Next Steps

After successful setup:
1. **Test the application** with sample data
2. **Upload your own** bank statements
3. **Explore features** like charts and recommendations
4. **Customize categories** if needed
5. **Export data** for further analysis

---

**Need more help?** Check the main README.md file or run the test suite with `python test_app.py` 