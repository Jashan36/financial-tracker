# Financial Tracker - Streamlit Version

A comprehensive personal finance tracking application built with Streamlit, featuring multi-currency support, AI-powered transaction categorization, and advanced analytics.

## 🌟 Features

- **📁 Multi-Format Support**: Upload CSV and PDF files
- **💱 Multi-Currency Support**: Automatic currency detection and conversion
- **🤖 AI-Powered Categorization**: Intelligent transaction categorization
- **📊 Advanced Analytics**: Spending patterns, budget recommendations
- **📈 Interactive Visualizations**: Charts and graphs with Plotly
- **🔄 Real-Time Processing**: Fast file processing and analysis
- **💾 Session Management**: Persistent data across interactions

## 🚀 Quick Start

### Option 1: Using the Batch File (Windows)
```bash
# Simply double-click or run:
start_streamlit.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the startup script
python run_streamlit.py

# 3. Or run directly
streamlit run streamlit_app.py
```

### Option 3: Direct Streamlit Command
```bash
streamlit run streamlit_app.py --server.port 8501
```

## 📋 Requirements

- Python 3.8 or higher
- All dependencies listed in `requirements.txt`
- At least 2GB RAM (for processing large files)

## 🎯 How to Use

1. **📁 Upload File**: Use the sidebar to upload a CSV or PDF file
2. **🔍 Analyze**: Click "Run Analysis" to get insights
3. **📊 View Results**: Explore your financial data with interactive charts
4. **💱 Convert Currency**: Use the currency conversion feature if needed
5. **📋 Export**: View and analyze your transaction data

## 📁 File Structure

```
financial-tracker/
├── streamlit_app.py          # Main Streamlit application
├── run_streamlit.py          # Startup script
├── start_streamlit.bat       # Windows batch file
├── requirements.txt          # Python dependencies
├── README_STREAMLIT.md       # This file
│
├── transaction_processor.py  # Core transaction processing logic
├── budget_analyzer.py        # Budget analysis and recommendations
├── enhanced_transaction_processor.py  # Enhanced processing features
├── currency_converter.py     # Currency conversion utilities
├── config.py                 # Configuration settings
│
├── models/                   # AI models directory
├── static/                   # Static assets (CSS, JS, images)
├── templates/                # HTML templates (not used in Streamlit)
├── uploads/                  # Upload directory
└── logs/                     # Log files
```

## 🔧 Configuration

The application uses the same configuration as the Flask version. Key settings can be modified in `config.py`:

- File upload limits
- Supported file formats
- Logging configuration
- Model paths

## 🌐 Accessing the Application

Once started, the application will be available at:
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501 (if configured)

## 📊 Supported File Formats

### CSV Files
- **Encodings**: UTF-8, UTF-8-BOM, Latin-1, CP1252
- **Required Columns**: Date, Description, Amount, Category
- **Optional Columns**: Currency, Type, Account
- **Date Formats**: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY

### PDF Files
- Bank statements and transaction reports
- Automatic text extraction and parsing
- Support for multiple page formats

## 💱 Currency Support

The application supports 100+ currencies with:
- Automatic detection from transaction data
- Real-time exchange rate conversion
- Locale-aware formatting
- Historical rate caching

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Model Not Found**
   - Ensure `models/categorization_model.pkl` exists
   - Run the training script if needed

3. **Port Already in Use**
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

4. **File Upload Issues**
   - Check file format (CSV/PDF only)
   - Ensure file size is under 16MB
   - Verify file encoding

### Debug Mode

Enable debug mode by setting:
```bash
export STREAMLIT_DEBUG=true
streamlit run streamlit_app.py
```

## 🔄 Migration from Flask Version

The Streamlit version preserves all existing logic and functionality:

- ✅ All processing logic maintained
- ✅ Same file formats supported
- ✅ Identical analysis algorithms
- ✅ Same currency conversion features
- ✅ All error handling preserved

**Key Differences:**
- Web interface instead of REST API
- Session state instead of Flask sessions
- Streamlit components instead of HTML templates
- Built-in caching instead of Flask-Caching

## 📈 Performance

- **File Processing**: Optimized for files up to 10,000 transactions
- **Memory Usage**: Efficient pandas operations
- **Caching**: Built-in Streamlit caching for better performance
- **Concurrent Users**: Single-user application (Streamlit limitation)

## 🛡️ Security

- File upload validation
- Input sanitization
- Error handling and logging
- No external API dependencies (except exchange rates)

## 📝 Logging

Logs are written to:
- `financial_tracker.log` (file)
- Console output (real-time)

Log levels: INFO, WARNING, ERROR, DEBUG

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue with detailed information

---

**Built with ❤️ using Streamlit**

