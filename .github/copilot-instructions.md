1. Project Overview & Goals
Project Name: AICCSA
Objective: Transform an existing CLI-based Node.js (scraping) and Python (OpenAI classification) pipeline into a standalone desktop application (Windows & macOS) using Flutter 3.41+ / Dart 3.11+.
Core Functionality:

Scrape sports and fitness application data from Google Play Store and Apple App Store based on keywords (single or .txt list) and predefined/custom country codes.

Combine and clean the scraped app data into a single CSV.

Automatically chunk the data and send it to the OpenAI Batch API for categorization (User Groups, Sport type, Purpose).

Merge the AI-classified results back into the final CSV.

2. High-Level Architecture
The application follows a decoupled Frontend-Backend architecture via Local IPC / Process Execution:

Frontend Layer (Flutter/Dart):

Provides the graphical user interface.

Captures user configurations (Target Store, Keywords, Countries, Top-list Collections, LLM Model, API Key).

Displays real-time progress (Scraping status, Batch API polling status).

Strict Rule: The UI must never be blocked by background tasks. Use Isolates or asynchronous Process.run()/Process.start().

Orchestration & AI Layer (Python):

Acts as the central controller for the data pipeline.

Executes the Node.js scraping scripts as subprocesses.

Handles the complex OpenAI Batch API logic (chunking data -> generating .jsonl -> uploading -> creating batches -> polling -> downloading -> merging).

Maintains a local state file (batch_status.json) so the Flutter app can read the current status of long-running Batch jobs even after app restarts.

Data Gathering Layer (Node.js):

Utilizes google-play-scraper and app-store-scraper.

Takes CLI arguments (countries, search terms, collections) passed down from the Python orchestrator.

3. Data Flow & OpenAI Batch API Pipeline
When the user clicks "Start Processing", the following automated pipeline is triggered:

Scraping: Flutter calls the Python orchestrator -> Python calls Node.js scrapers -> Node.js outputs raw store_apps.csv.

Chunking: Python reads store_apps.csv. It groups 50 app descriptions into a single prompt string to save tokens (System prompt is ~200 lines).

JSONL Generation: Python packs these prompts into requests. A maximum of 130 requests are allowed per .jsonl file. Multiple .jsonl files are generated if the dataset is massive (e.g., 50,000 apps).

Batch Execution: Python uploads the .jsonl files to OpenAI, starts the Batch jobs, and saves the batch_ids to a local batch_status.json file.

Polling: Flutter routinely requests the status of these batches. Python checks OpenAI (client.batches.retrieve) and returns the status.

Merging: Once a batch is completed, Python downloads the results, parses the AI outputs, and appends the new columns (User Group, Sport, Purpose) to the final output CSV.

4. Tech Stack & State Management
UI Framework: Flutter (Dart).

Desktop Support: macOS & Windows native compilation.

State Management (Flutter): Provider (manage UI state, form inputs, and background task progress).

Local Storage: shared_preferences (for saving UI selections) and flutter_secure_storage ^10.0.0 (for securely storing the OpenAI API Key).

Backend Subprocesses: Python 3.13+, Node.js 24+.

5. Strict Instructions for GitHub Copilot
When generating code for this project, adhere to the following rules:

Flutter / Dart Rules:
Null Safety: Always use sound null safety.

Asynchronous UI: Always use async/await for file I/O and Process execution. Use CircularProgressIndicator or LinearProgressIndicator to reflect loading states.

Dynamic UI Rendering: If "Google Play" is selected, hide Apple App Store specific collections, and vice versa.

File Handling: Use the file_picker package for selecting the keyword .txt lists. Use path_provider for saving temporary JSONL and CSV files.

Python / AI Rules:
Batch Tracking: You MUST implement local file-based tracking for Batch IDs (e.g., batch_status.json). If the Flutter app is closed and reopened, it must be able to resume polling the OpenAI Batch API using this file.

Error Handling: OpenAI API calls must have retry logic (tenacity or custom try-except blocks). Node.js subprocess calls must capture stderr and bubble errors up to the Flutter UI gracefully.

Cost Efficiency: Strictly adhere to the chunking logic (50 apps per prompt). Do not generate code that sends one app per API request unless explicitly requested.

Node.js / Scraping Rules:
CLI Arguments: Ensure Node.js scripts can accept dynamic parameters (e.g., --country=fi, --keyword=sports, --store=apple) using packages like yargs or minimist.

No Hardcoding: Remove any hardcoded arrays of countries or search terms in the legacy scripts; read them from arguments or external files provided by Flutter.