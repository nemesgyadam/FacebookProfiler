# Facebook Digital Psychometrics Profile

A comprehensive psychological profiling tool that analyzes your Facebook data export to generate detailed insights about your digital personality, behavioral patterns, and psychological traits.

## 🚀 Features

- **Automated Data Processing**: Filters and processes Facebook data exports
- **Psychological Analysis**: Generates detailed psychological profiles using AI
- **Privacy-First**: All processing happens locally on your machine
- **Web Interface**: User-friendly web dashboard for data exploration
- **Comprehensive Profiling**: Analyzes personality traits, vulnerabilities, and behavioral patterns

## 📋 Prerequisites

- Python 3.11+
- UV package manager
- OpenRouter API key (for profile generation)
- Your Facebook data export

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fb-profile
   ```

2. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   # Create a .env file or set environment variable
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   ```

## 📊 Getting Your Facebook Data

1. **Download Your Facebook Data**:
   - Go to Facebook Settings > Your Facebook Information
   - Click "Download Your Information"
   - Select:
     - **Format**: JSON
     - **Date Range**: All time
     - **Media Quality**: Low (to reduce file size)
   - Include at least: Ads and Businesses, Apps and Websites, Posts, Comments, Friends, Profile Information

2. **Extract and Place Data**:
   - Download and extract the ZIP file
   - Copy the `data` folder to this project's root directory

## 🚀 Usage

### Step 1: Start the Web Server

```bash
python run_web.py
```

Then open http://localhost:5000 in your browser.

### Step 2: Follow the Web Interface

The application will guide you through:

1. **Data Check**: Verifies if your Facebook data is present
2. **Data Filtering**: Processes and filters your data (excludes messages for privacy)
3. **Profile Generation**: Creates your psychological profile using AI
4. **Results**: View your comprehensive psychological analysis

### Alternative: Command Line Usage

```bash
# Generate profile directly
python generate_profile.py

# Or use the main analysis script
python main.py data/
```

## 📁 Project Structure

```
fb-profile/
├── data/                    # Your Facebook data export (you provide this)
├── data_filtered/           # Processed data (auto-generated)
├── src/
│   ├── web/                # Web interface
│   ├── analysis/           # Analysis modules
│   └── data_handler.py     # Data processing logic
├── prompts/
│   └── profiler.txt        # AI prompting for profile generation
├── generate_profile.py     # Profile generation script
├── run_web.py             # Web server launcher
└── required_files.csv     # Files needed for analysis
```

## 🔒 Privacy & Security

- **Local Processing**: All data remains on your computer
- **No Data Upload**: Your Facebook data is never uploaded anywhere
- **Messages Excluded**: Private messages are automatically excluded from analysis
- **API Usage**: Only filtered, anonymized data insights are sent to AI services

## 🧠 What You'll Get

Your psychological profile includes:

- **OCEAN Personality Traits**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- **Facebook's Assessment**: How Facebook categorizes you vs. actual analysis
- **Vulnerability Analysis**: Potential psychological vulnerabilities
- **Manipulation Susceptibility**: How susceptible you are to different influence tactics
- **Protective Recommendations**: Strategies to protect your digital privacy
- **Behavioral Patterns**: Insights into your digital behavior

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## ⚠️ Disclaimer

This tool is for educational and self-awareness purposes. The psychological analysis should not be considered as professional psychological assessment or medical advice.

## 📄 License

This project is open source. Please check the license file for details.
