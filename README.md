# Financial Tracker 💰

A simple Streamlit app that categorizes your bank transactions and shows spending patterns. Upload a CSV or PDF file, get some basic charts and budget suggestions.

## What it actually does

- **Uploads**: CSV or PDF bank statements
- **Categorizes**: Transactions using AI (scikit-learn + NLTK)
- **Shows**: Basic spending charts and budget recommendations
- **Converts**: Currency if you want (uses free exchange rate APIs)

## What it doesn't do

- ❌ No database - everything is temporary
- ❌ No user accounts or data persistence
- ❌ No advanced analytics or predictions
- ❌ No integration with banks or financial services

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the app**:
```bash
   streamlit run streamlit_app.py
   ```

3. **Open browser**: Go to `http://localhost:8501`

4. **Upload a file**: CSV or PDF with your transactions

## File Format

Your CSV should have columns like:
- `date` (or `transaction_date`)
- `description` (or `merchant`)
- `amount` (or `debit`/`credit`)

## What you get

- Transaction categorization (food, transport, etc.)
- Basic spending charts
- Simple budget recommendations
- Currency conversion (if needed)

## Limitations

- **File size**: Max 16MB
- **Processing**: Simple ML model with limited training data
- **Data**: Nothing is saved - refresh and it's gone
- **Accuracy**: Categorization is hit-or-miss depending on your bank's description format

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Data**: Pandas for CSV processing
- **Charts**: Plotly for visualizations
- **PDF**: PDFPlumber for extracting text
- **Currency**: Free exchange rate APIs
- **AI/ML**: 
  - **scikit-learn**: TF-IDF vectorization + Naive Bayes classifier
  - **NLTK**: Text preprocessing, tokenization, stopwords removal
  - **Pipeline**: Combines text processing and classification

## Project Structure

```
financial-tracker/
├── streamlit_app.py          # Main app
├── transaction_processor.py  # File processing & categorization
├── budget_analyzer.py        # Basic budget calculations
├── currency_converter.py     # Currency conversion
└── requirements.txt          # Dependencies
```

## Docker (Optional)

```bash
docker build -t financial-tracker .
docker run -p 8501:8501 financial-tracker
```


**How the AI works:**
1. **Text preprocessing**: NLTK tokenizes and removes stopwords from transaction descriptions
2. **Feature extraction**: TF-IDF vectorizer converts text to numerical features
3. **Classification**: Naive Bayes classifier predicts transaction categories
4. **Fallback**: If ML fails, falls back to keyword matching

## Technical Implementation & AI/ML Skills Demonstrated

### **AI/ML Pipeline Built:**
- **Text Preprocessing**: NLTK tokenization, stopwords removal, text normalization
- **Feature Engineering**: TF-IDF vectorization with 1000 features, text-to-vector conversion
- **Machine Learning**: Scikit-learn pipeline with Naive Bayes classifier
- **Model Persistence**: Pickle-based model saving/loading with version control
- **Hybrid Approach**: ML model + rule-based fallback for robust categorization
- **Performance Optimization**: Chunked processing for large datasets, memory management

### **Data Processing Skills:**
- **Multi-format Support**: CSV parsing with encoding detection, PDF text extraction
- **Data Validation**: Comprehensive input validation, error handling, data sanitization
- **Currency Detection**: Regex-based pattern matching for 25+ currencies
- **Data Transformation**: Pandas operations, data cleaning, type conversion

### **Full-Stack Development:**
- **Backend**: Python with proper error handling, logging, configuration management
- **Frontend**: Streamlit with interactive charts, file uploads, responsive design
- **DevOps**: Docker containerization, multi-stage builds, environment configuration
- **Testing**: Comprehensive test suite for different scenarios and edge cases

### **What This Demonstrates:**
- **ML Engineering**: End-to-end ML pipeline from data preprocessing to model deployment
- **Production Readiness**: Error handling, logging, configuration management, Docker setup
- **Data Science**: Feature engineering, model evaluation, performance optimization
- **Software Engineering**: Clean code, modular design, proper project structure

### **Project Scope (Honest Assessment):**
- **Personal Project**: Built to learn ML and full-stack development
- **Limited Features**: Basic categorization and visualization (not a complete financial app)
- **No Production Use**: Missing authentication, security, scalability features
- **Learning Focus**: Demonstrates technical skills rather than business viability

### **For Recruiters - Key Technical Achievements:**
1. **Implemented ML Pipeline**: TF-IDF + Naive Bayes with proper preprocessing
2. **Built Full-Stack App**: Python backend + Streamlit frontend + Docker deployment
3. **Handled Real Data**: Multi-format file processing with error handling
4. **Production Practices**: Logging, configuration, testing, containerization
5. **Performance Optimization**: Chunked processing, memory management, caching

**Bottom line**: This project showcases practical ML engineering skills, full-stack development, and production-ready practices. It's a technical demonstration rather than a commercial product.

## License

MIT License - use it, break it, improve it.