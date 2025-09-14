# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. Prepare Your Repository
- Ensure all files are committed to your GitHub repository
- Make sure `requirements_cloud.txt` is in the root directory

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set the following:
   - **Main file path**: `streamlit_app.py`
   - **Requirements file**: `requirements_cloud.txt`
   - **Python version**: 3.9 (recommended)

### 3. Common Issues & Solutions

#### Budget Recommendations Not Showing
- **Cause**: Missing income data or data processing errors
- **Solution**: Ensure your CSV has both income (positive amounts) and expenses (negative amounts)
- **Debug**: Use the "🔍 Show Budget Debug Info" checkbox in the app

#### Import Errors
- **Cause**: Missing dependencies
- **Solution**: All required packages are in `requirements_cloud.txt`

#### Memory Issues
- **Cause**: Large files or inefficient processing
- **Solution**: The app automatically chunks large files for processing

### 4. File Structure for Deployment
```
your-repo/
├── streamlit_app.py          # Main app file
├── requirements_cloud.txt    # Dependencies
├── transaction_processor.py  # Core processing
├── budget_analyzer.py        # Budget analysis
├── currency_converter.py     # Currency conversion
├── enhanced_transaction_processor.py
├── config.py
└── models/                   # ML model storage
    └── categorization_model.pkl
```

### 5. Environment Variables (Optional)
You can set these in Streamlit Cloud settings:
- `ENVIRONMENT=production`
- `DEBUG=False`

### 6. Testing Your Deployment
1. Upload a CSV file with sample transactions
2. Check that analysis runs without errors
3. Verify budget recommendations appear
4. Test currency conversion if needed

### 7. Troubleshooting
If budget recommendations still don't show:
1. Check the "🔍 Error Details" expander
2. Look at the debug information
3. Ensure your CSV has the required columns: date, description, amount
4. Make sure you have both income and expense transactions
