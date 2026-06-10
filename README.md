# AICCSA - AI-tool for Collecting and Classifying Sports Applications
AICCSA is a Flutter-based desktop application designed specifically for research purposes. It automates the collection of sports and health/fitness application data from the Google Play Store and Apple App Store, and utilizes OpenAI's API to intelligently classify the gathered data.

*** THE SEARCH FUNCTION FOR THE GOOGLE PLAY SCRAPER IS TEMPORARILY UNAVAILABLE. WE ARE CURRENTLY INVESTIGATING THE ISSUE.***

The tool categorizes each application into specific taxonomies, including:
- User groups (athlete, supporter, support staff, governing entity).
- Purpose of use (tracking, live scores, betting, training, team management etc.)
- Sport type

## Key features
- Cross-Platform Desktop UI: A user-friendly graphical interface built with Flutter, supporting Windows, macOS, and Linux.
- Automated Scraping: Seamlessly gathers app metadata (descriptions, genres, ratings, etc.) based on custom keyword lists, top collections and targeted countries.
- AI-Powered Classification: Integrates with OpenAI api to process thousands of app descriptions and classify them into structured research data.
- Data Export: Outputs the merged and classified data into clean, analysis-ready CSV and XLSX files.
- Secure Credential Management: Securely stores your OpenAI API keys locally using flutter_secure_storage.

## Prerequisites
- Flutter SDK: 3.41 or higher
- Dart SDK: 3.11 or higher (included with Flutter)
- Python: 3.13+ (required for the backend orchestrator)
- Node.js: 24+ (required for the scraping scripts)

Platform-Specific Build Tools
- Windows: Visual Studio or Visual Studio Build Tools (C++ build tools)
- macOS: Xcode and Xcode Command Line Tools
- Linux: Required build tools (e.g., gcc, make)

## Installation & setup
For a detailed setup process and troubleshooting, please refer to the SETUP_GUIDE.md.

