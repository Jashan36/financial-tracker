# Financial Tracker - Smart Spending Insights 🚀

A modern, comprehensive web application that automatically categorizes bank transactions using AI/ML and provides intelligent spending insights with personalized budget recommendations.

## ✨ What's New in Version 2.0

- 🤖 **AI-Powered Categorization**: Machine Learning models with TF-IDF vectorization for superior transaction categorization
- 🌍 **Multi-Currency Support**: Automatic detection and formatting for 25+ global currencies (USD, INR, EUR, GBP, JPY, CAD, AUD, and more)
- 🎯 **Smart Currency Detection**: Automatically detects currency from transaction data and formats according to regional conventions
- 🌙 **Dark Mode**: Beautiful dark theme with smooth transitions
- 🔒 **Enhanced Security**: Rate limiting, security headers, and comprehensive input validation
- 📊 **Real-time Progress**: Visual progress tracking during file processing
- 🔔 **Smart Notifications**: Non-intrusive notification system with auto-dismiss
- ⚡ **Performance Optimized**: Caching, session management, and optimized database queries
- 🐳 **Docker Ready**: Complete containerization with multi-stage builds
- 🎯 **Better UX**: Keyboard shortcuts, drag & drop improvements, and responsive design
- 📈 **Advanced Analytics**: Enhanced charts with theme support and interactivity

## 🚀 Features

### Core Functionality
- **Multi-Currency Support**: Automatic detection and formatting for 25+ global currencies
- **File Upload Support**: Upload CSV and PDF bank statements from major banks worldwide
- **Automatic Categorization**: AI-powered transaction categorization using NLP and keyword matching
- **Spending Analytics**: Comprehensive analysis of spending patterns and trends
- **Budget Recommendations**: Personalized budget suggestions based on income and spending patterns
- **Visual Charts**: Interactive charts showing monthly trends, category breakdowns, and daily patterns
- **Export Functionality**: Download processed data as CSV for further analysis
- **Regional Formatting**: Proper number formatting according to local currency conventions

### Transaction Categories
- 🍽️ **Food**: Restaurants, groceries, dining, coffee shops
- 🚗 **Transport**: Uber, gas, parking, public transit
- 🎬 **Entertainment**: Movies, streaming services, games
- 🛍️ **Shopping**: Online stores, retail, clothing
- 💡 **Utilities**: Electricity, water, internet, phone
- 🏥 **Healthcare**: Medical expenses, pharmacy, insurance
- 📚 **Education**: Courses, books, tuition
- ✈️ **Travel**: Hotels, flights, vacation expenses
- 🛡️ **Insurance**: Various insurance types
- 📈 **Investment**: Stocks, bonds, trading
- 📦 **Other**: Miscellaneous expenses

### Supported Currencies
- 💵 **USD**: US Dollar ($)
- 🇮🇳 **INR**: Indian Rupee (₹)
- 🇪🇺 **EUR**: Euro (€)
- 🇬🇧 **GBP**: British Pound (£)
- 🇯🇵 **JPY**: Japanese Yen (¥)
- 🇨🇦 **CAD**: Canadian Dollar (C$)
- 🇦🇺 **AUD**: Australian Dollar (A$)
- 🇨🇭 **CHF**: Swiss Franc (CHF)
- 🇨🇳 **CNY**: Chinese Yuan (¥)
- 🇸🇪 **SEK**: Swedish Krona (kr)
- 🇳🇴 **NOK**: Norwegian Krone (kr)
- 🇩🇰 **DKK**: Danish Krone (kr)
- 🇵🇱 **PLN**: Polish Złoty (zł)
- 🇨🇿 **CZK**: Czech Koruna (Kč)
- 🇭🇺 **HUF**: Hungarian Forint (Ft)
- 🇷🇺 **RUB**: Russian Ruble (₽)
- 🇧🇷 **BRL**: Brazilian Real (R$)
- 🇲🇽 **MXN**: Mexican Peso ($)
- 🇿🇦 **ZAR**: South African Rand (R)
- 🇰🇷 **KRW**: South Korean Won (₩)
- 🇸🇬 **SGD**: Singapore Dollar (S$)
- 🇭🇰 **HKD**: Hong Kong Dollar (HK$)
- 🇳🇿 **NZD**: New Zealand Dollar (NZ$)
- 🇹🇭 **THB**: Thai Baht (฿)
- 🇲🇾 **MYR**: Malaysian Ringgit (RM)
- 🇮🇩 **IDR**: Indonesian Rupiah (Rp)
- 🇵🇭 **PHP**: Philippine Peso (₱)

## 🛠️ Technology Stack

### Backend
- **Framework**: Python Flask with enhanced architecture
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn, NLTK, TF-IDF Vectorization
- **PDF Processing**: PDFPlumber
- **Database**: SQLite with optimized queries
- **Caching**: Flask-Caching
- **Security**: Flask-Limiter, comprehensive validation
- **Logging**: Structured logging with file rotation

### Frontend
- **Core**: HTML5, CSS3, Modern JavaScript (ES6+)
- **UI Framework**: Bootstrap 5 with custom enhancements
- **Visualization**: Plotly with theme support
- **Icons**: Font Awesome 6
- **Features**: Dark mode, responsive design, accessibility features

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Web Server**: Gunicorn for production
- **Reverse Proxy**: Nginx configuration included
- **Monitoring**: Health checks and performance metrics

## 📋 Requirements

- Python 3.8+
- Modern web browser
- 16MB maximum file size for uploads

## 🚀 Installation & Setup

### Quick Setup (Recommended)
```bash
# Run the automated setup script
python start.py
```
This script will automatically:
- Check Python version compatibility
- Install all required dependencies
- Test package imports
- Start the application

### Manual Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd financial-tracker
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Test the Installation
```bash
# Test basic functionality
python test_functionality.py

# Test multi-currency support
python test_multi_currency.py

# Test currency detection fixes
python test_currency_fixes.py
```

#### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### CPU Optimization Features
- **Chunked Processing**: Large files are processed in small chunks (1000 rows) to prevent CPU overload
- **Memory Management**: Automatic cleanup and garbage collection
- **Worker Limits**: Maximum 4 worker threads to prevent system strain
- **File Size Limits**: Maximum 10,000 rows per file for optimal performance
- **Progress Tracking**: Real-time progress indicators for large file processing

## 📁 Project Structure

```
financial-tracker/
├── app.py                 # Main Flask application
├── transaction_processor.py  # Transaction processing and categorization
├── budget_analyzer.py     # Spending analysis and budget recommendations
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── js/
│       └── app.js        # Frontend JavaScript
└── uploads/              # Temporary upload directory (auto-created)
```

## 💡 Usage Guide

### 1. Upload Bank Statement
- Drag and drop your CSV or PDF file onto the upload area
- Or click "Choose File" to browse and select a file
- Supported formats: CSV, PDF
- Maximum file size: 16MB

### 2. Automatic Processing
- The system automatically processes your file
- Extracts transaction data
- Categorizes transactions using AI
- Generates spending insights

### 3. View Results
- **Summary Statistics**: Total expenses, transaction count, daily averages
- **Spending Analytics**: Interactive charts and visualizations
- **Budget Recommendations**: Personalized budget suggestions
- **Transaction Details**: Complete transaction list with categories

### 4. Export Data
- Click "Export CSV" to download processed data
- Use exported data for further analysis in Excel or other tools

## 🔧 Configuration

### Customizing Categories
Edit `transaction_processor.py` to modify transaction categories and keywords:

```python
self.categories = {
    'food': ['restaurant', 'cafe', 'grocery', ...],
    'transport': ['uber', 'lyft', 'gas', ...],
    # Add your custom categories
}
```

### Budget Percentages
Modify `budget_analyzer.py` to adjust recommended budget percentages:

```python
self.standard_budgets = {
    'food': 0.15,        # 15% of income
    'transport': 0.10,   # 10% of income
    # Adjust percentages as needed
}
```

## 📊 Supported File Formats

### CSV Files
The application automatically detects common column names:
- Date columns: `date`, `transaction_date`, `posted_date`
- Description columns: `description`, `merchant`, `payee`
- Amount columns: `amount`, `debit`, `credit`
- Category columns: `category`, `transaction_category`

### PDF Files
- Extracts text content from PDF bank statements
- Uses regex patterns to identify transaction data
- Supports common bank statement formats

## 🎯 Key Features Explained

### Automatic Categorization
- Uses Natural Language Processing (NLP) with NLTK
- Keyword-based scoring system for category matching
- Removes stop words and analyzes transaction descriptions
- Assigns confidence scores to category matches

### Spending Analysis
- Monthly spending trends and patterns
- Category-wise spending breakdown
- Daily spending patterns by day of week
- Top merchant analysis

### Budget Recommendations
- Based on standard financial planning guidelines
- Considers your actual income and spending
- Provides category-specific budget targets
- Generates alerts for overspending areas

## 🔒 Security & Privacy

- Files are processed temporarily and deleted after processing
- No data is stored permanently on the server
- All processing happens locally on your machine
- No external API calls for data processing

## 🐛 Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size (max 16MB)
   - Ensure file is CSV or PDF format
   - Verify file is not corrupted
   - Try different CSV encodings if needed

2. **Transactions Not Categorized**
   - Check if transaction descriptions are clear
   - Verify CSV column names match expected format
   - PDF text extraction may vary by format
   - Ensure required columns: Date, Description, Amount

3. **Charts Not Displaying**
   - Ensure JavaScript is enabled
   - Check browser console for errors
   - Verify Plotly library is loaded
   - Clear browser cache and reload

4. **Processing Errors**
   - Large files are automatically chunked for processing
   - PDF files limited to first 50 pages for performance
   - Check console logs for detailed error messages
   - Run `python test_functionality.py` for diagnostics

5. **CPU Performance Issues**
   - Application automatically limits processing to prevent overload
   - Large files are processed in chunks of 1000 rows
   - Maximum 10,000 rows per file for optimal performance
   - Consider splitting very large files

6. **Currency Detection Issues**
   - Application now supports improved currency detection for 25+ currencies
   - Enhanced pattern matching for symbols like C$, A$, R$, RM, S$, etc.
   - Better handling of European decimal formats (comma vs period)
   - Automatic fallback to USD if currency cannot be detected

### Performance Tips

- **For Large Files**: Processing is automatically optimized with chunking
- **CSV vs PDF**: CSV files process faster than PDF files
- **Memory Usage**: Application automatically manages memory usage
- **CPU Load**: Limited worker threads prevent system strain
- **Progress Tracking**: Watch progress indicators for large file processing

### Testing and Diagnostics

Run the comprehensive test suite:
```bash
python test_functionality.py
```

This will verify:
- All dependencies are properly installed
- Configuration is correctly loaded
- Transaction processor is working
- Sample data can be processed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Uses NLTK for natural language processing
- Plotly for interactive data visualization
- Bootstrap for responsive UI design

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

---

**Note**: This application is designed for personal financial analysis. Always verify the accuracy of categorized transactions and consult with financial professionals for important financial decisions. 