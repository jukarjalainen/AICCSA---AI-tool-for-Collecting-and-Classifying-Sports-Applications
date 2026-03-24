# AICCSA Flutter UI - Setup & Running Guide

## Prerequisites

Before running the Flutter application, ensure you have:

- **Flutter SDK**: 3.41 or higher
- **Dart SDK**: 3.11 or higher (comes with Flutter)
- **Python**: 3.13+ (for the backend orchestrator)
- **Node.js**: 24+ (for the scraping scripts)
- **Platform-specific setup**:
  - **Windows**: Visual Studio or Visual Studio Build Tools (C++ build tools)
  - **macOS**: Xcode and Xcode Command Line Tools
  - **Linux**: Required build tools (gcc, make, etc.)

## Installation Steps

### 1. Install Flutter Dependencies

Navigate to the project root and run:

```bash
flutter pub get
```

This installs all required packages including:

- provider (state management)
- file_picker (file selection)
- flutter_secure_storage (secure key storage)
- shared_preferences (persistent configuration)

### 2. Platform-Specific Setup

#### Windows

```bash
flutter config --enable-windows-desktop
flutter doctor
# Fix any issues reported
```

#### macOS

```bash
flutter config --enable-macos-desktop
cd macos
pod install  # if needed
cd ..
```

#### Linux

```bash
flutter config --enable-linux-desktop
# Install required libraries (Ubuntu example):
# sudo apt-get install libgtk-3-dev libx11-dev pkg-config
```

### 3. Backend Setup (Python Orchestrator)

The Python backend needs to be available for the app to function:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Alternatively, set up a virtual environment (recommended):
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Note**: Ensure backend/orchestrator.py exists. If it doesn't, create a stub for testing:

```python
# backend/orchestrator.py (stub for testing)
import sys
import json
import time

def main():
    args = sys.argv[1:]
    print("Orchestrator started with args:", args)
    print("Stage: scraping")
    time.sleep(2)
    print("Stage: chunking")
    time.sleep(2)
    print("Stage: uploading")
    time.sleep(2)
    print("Stage: polling")
    time.sleep(2)
    print("Stage: merging")
    time.sleep(2)
    print("Stage: completed")

if __name__ == '__main__':
    main()
```

## Running the Application

### 1. Run on Desktop

#### Windows

```bash
flutter run -d windows
```

#### macOS

```bash
flutter run -d macos
```

#### Linux

```bash
flutter run -d linux
```

### 2. Build Release Version

```bash
# Windows
flutter build windows --release

# macOS
flutter build macos --release

# Linux (if needed)
flutter build linux --release
```

### 3. Hot Reload During Development

While the app is running:

- Press `r` to hot reload
- Press `R` to hot restart
- Press `q` to quit

## Testing the UI

### Manual Testing Workflow

#### Step 1: Configuration Tab

1. Launch the app - should land on Configuration tab
2. **Store Selection**:
   - Click "Google Play" - should highlight
   - Click "Apple App Store" - should toggle
   - Click "Both" - should toggle
   - Verify only one displays as selected state

3. **Keywords Input**:
   - Type "sports,fitness" directly in text field
   - Click "Browse" button and select a .txt file
   - Verify file path appears in text field

4. **Countries Selection**:
   - Click on "US" chip - should turn blue/highlighted
   - Click "DE" - should add to selection
   - Verify multiple countries can be selected
   - Click again to deselect

5. **App Store Collections** (only when AppStore selected):
   - Select "Apple App Store" in Step 1
   - Collections dropdown should appear
   - Select "Top Free"
   - Switch back to "Google Play"
   - Collections dropdown should disappear

6. **LLM Model**:
   - Dropdown should show 3 options (GPT-4, GPT-4 Turbo, GPT-3.5 Turbo)
   - Select each and verify persistence

7. **API Key**:
   - Enter a test API key
   - Toggle visibility icon to show/hide
   - Check "Save API key securely"
   - Close and reopen app (or use hot restart)
   - API key should be auto-populated from secure storage

#### Step 2: Start Processing

1. Fill in all required fields (keywords, at least 1 country, API key)
2. Click "Start Processing" FAB
3. Should switch to Progress tab automatically
4. Verify processing stages appear in order:
   - Scraping (orange indicator)
   - Chunking
   - Uploading
   - Polling
   - Merging
   - Completed (green checkmark)

#### Step 3: Progress Monitoring

1. Verify progress bar increases
2. Verify status card updates with current stage
3. Verify "Stop" FAB appears (red button)
4. Click "Stop" to cancel processing
5. Stage should revert to "error" or initial state

#### Step 4: Results Tab

1. After successful processing, Results tab becomes available
2. Click "Results" tab
3. Verify CSV data loads
4. Check table shows app data
5. Click "Reload Results" button - data should refresh
6. Click "Export CSV" button - should show confirmation

### Troubleshooting Common Issues

#### Issue: "flutter: command not found"

**Solution**: Add Flutter to PATH or use full path to flutter executable

#### Issue: Secure Storage not working

**Solution**:

- Windows/Linux: May need platform-specific setup
- macOS: Ensure Xcode is installed: `xcode-select --install`
- Android: Requires Kotlin properly configured

#### Issue: Process can't find Python orchestrator

**Solution**:

- Check backend/orchestrator.py exists
- Verify Python is in system PATH
- Use full Python path: `python.exe` on Windows

#### Issue: File picker not working

**Solution**:

- Ensure file_picker package is properly installed
- Try `flutter clean` then `flutter pub get` again
- Check platform-specific file permissions

#### Issue: Configuration not persisting

**Solution**:

- Verify shared_preferences package is installed
- Check app has write permissions
- Try clearing app data and reinstalling

## Development Tips

### Debug Mode Features

- Press `v` to toggle debug visual grid
- Press `p` for performance overlay
- Press `w` to show widget inspector
- Press `o` to toggle Android/iOS oriented
- Press `a` for accessibility inspector

### Logging

Add to services for debugging:

```dart
debugPrint('[Tag] Message here');
```

View logs:

```bash
flutter logs
```

### Hot Reload Best Practices

- Works for UI changes (widgets, layouts)
- Requires hot restart for: service changes, dependency updates, custom code paths
- Full rebuild (`flutter run --release`) for production testing

## Configuration Files

### pubspec.yaml

Update version number before distribution:

```yaml
version: 1.0.0+1
```

### platform-specific config

- **Windows**: windows/runner/… (app identity)
- **macOS**: macos/Runner/… (app identity, entitlements)
- **Linux**: linux/… (app metadata)

## Next Development Steps

1. **Implement Python Orchestrator Backend** (backend/orchestrator.py)
2. **Add Unit Tests** (test/providers/test_state_provider.dart)
3. **Add Widget Tests** (test/widgets/test_configuration_form.dart)
4. **Enhance Error Handling** with retry logic
5. **Add Settings Screen** for API endpoint configuration
6. **Implement Batch Resume** for network resilience
7. **Add Desktop Shortcuts** (Ctrl+S, Ctrl+Q, etc.)
8. **Build Installers** (.msi for Windows, .dmg for macOS)

## Support & Debugging

- **Flutter Docs**: https://flutter.dev/docs
- **Flutter Getting Started**: https://flutter.dev/docs/get-started
- **Package Documentation**: https://pub.dev/packages/[package-name]
- **Community**: https://flutter.dev/community

---

**Note**: This UI is designed to work with the Python backend orchestrator. Ensure the backend is properly set up before running end-to-end tests.
