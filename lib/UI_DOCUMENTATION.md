# AICCSA Flutter Application - UI Documentation

## Overview

This is the Flutter-based frontend for the AICCSA (App Intelligence & Classification System) project. It provides a user-friendly interface for configuring and running the complete pipeline: scraping app store data, processing it through the OpenAI Batch API, and exporting classified results.

## Architecture

### Project Structure

```
lib/
├── main.dart                          # Application entry point and main UI logic
├── models/
│   └── app_configuration.dart        # Data models for configuration and progress
├── providers/
│   └── app_state_provider.dart       # State management using Provider
├── services/
│   ├── process_service.dart          # Handle subprocess execution
│   └── secure_storage_service.dart   # Secure API key storage
└── widgets/
    ├── configuration_form.dart       # Configuration input form
    ├── progress_display.dart         # Real-time progress tracking
    └── results_display.dart          # Results visualization
```

### Key Components

#### 1. **AppStateProvider** (`providers/app_state_provider.dart`)

- Manages application state using Provider pattern
- Handles configuration persistence via `shared_preferences`
- Tracks processing progress and status
- Notifies UI of state changes

#### 2. **ProcessService** (`services/process_service.dart`)

- Launches Python orchestrator subprocess
- Streams stdout/stderr from background processes
- Reads batch status from local JSON files
- Handles process cancellation

#### 3. **SecureStorageService** (`services/secure_storage_service.dart`)

- Securely stores OpenAI API key using platform-specific encryption
- Uses `flutter_secure_storage` with AES-GCM on Android and Keychain on iOS/macOS

#### 4. **ConfigurationForm** (`widgets/configuration_form.dart`)

- Dynamic form for app configuration:
  - Target store selection (Google Play, App Store, or both)
  - Keywords input (single or file-based)
  - Country multi-select
  - Conditional App Store collections dropdown
  - LLM model selection
  - Secure API key input
- Uses `file_picker` for .txt file selection
- Saves configuration automatically to `shared_preferences`

#### 5. **ProgressDisplay** (`widgets/progress_display.dart`)

- Real-time pipeline stage visualization
- Progress bar with percentage display
- Status card with current stage info
- Pipeline stage timeline with completion indicators
- Active batch IDs display
- Error message presentation
- Duration calculation

#### 6. **ResultsDisplay** (`widgets/results_display.dart`)

- Loads and displays final classified CSV
- Interactive data table with first 50 results
- Row count summary
- Export functionality
- Auto-refresh capability

## User Flow

### Starting a New Processing Task

1. **Configuration Tab**
   - User selects target store(s)
   - Enters keywords or uploads .txt file
   - Selects desired countries (multi-select)
   - Optionally selects App Store collection
   - Chooses LLM model
   - Enters OpenAI API key (securely stored)

2. **Start Processing**
   - User clicks "Start Processing" FAB
   - Validation checks run (keywords, countries, API key)
   - Python orchestrator starts as subprocess
   - UI automatically switches to Progress tab

3. **Progress Monitoring**
   - Real-time stage updates (scraping → chunking → uploading → polling → merging)
   - Progress bar indicates overall completion
   - Batch IDs displayed for long-running polls
   - User can cancel processing with stop FAB

4. **Results**
   - Upon completion, UI auto-switches to Results tab
   - Final CSV is displayed in an interactive table
   - User can reload or export results

### Resuming After Restart

- API key is loaded from secure storage on app startup
- Configuration is restored from `shared_preferences`
- Batch status can be manually reloaded from `batch_status.json`

## UI Features

### Dynamic Rendering

- **Store-specific UI**: Apple App Store collections dropdown only appears when App Store is selected
- **Progress visualization**: Stages show completion status with icons and colors
- **Responsive layout**: All screens support responsive design

### Non-blocking Operations

- **Async/await pattern**: All I/O operations use async/await
- **Process execution**: Uses `Process.run()` to prevent main thread blocking
- **Stream listening**: Real-time output streaming with `listen()`

### Visual Feedback

- **Loading indicators**: CircularProgressIndicator for pending stages
- **Color coding**: Green (completed), Orange (current/processing), Red (error), Grey (pending)
- **Status messages**: Clear descriptions of current operations
- **Error handling**: Detailed error messages with fallback UI states

## Dependencies

Core packages used:

- **provider**: ^6.1.0 - State management
- **file_picker**: ^6.1.0 - File selection
- **flutter_secure_storage**: ^10.0.0 - Secure API key storage
- **shared_preferences**: ^2.2.2 - Configuration persistence
- **path_provider**: ^2.1.0 - File system paths
- **intl**: ^0.19.0 - Date/time formatting

## Environment Setup

### Prerequisites

- Flutter 3.41+
- Dart 3.11+
- Python 3.13+ (for backend)
- Node.js 24+ (for scrapers)

### Installation

1. **Get dependencies**:

   ```bash
   flutter pub get
   ```

2. **Build platform-specific support** (needed for secure storage):

   ```bash
   flutter pub get
   # On Windows/macOS: run build automatically
   # On Android: requires Kotlin setup
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## Configuration Persistence

### Saved Preferences (shared_preferences)

- `targetStore`: Selected app store
- `keywords`: User keywords
- `countries`: Selected country list
- `collection`: App Store collection (if any)
- `llmModel`: Selected LLM model

### Secure Storage

- OpenAI API key is encrypted at rest using platform-specific encryption
- iOS/macOS: Keychain
- Android: Keystore with AES-GCM
- Windows/Linux: Not currently wrapped (can be enhanced)

## Error Handling

### UI-Level Error Handling

- Validation before processing starts
- SnackBar notifications for user feedback
- Error details displayed in Progress tab
- Graceful fallbacks for missing data

### Process-Level Error Handling

- Exit code checking (0 = success)
- stderr streaming for diagnostics
- Batch status error tracking
- Network failure recovery (delegated to Python backend)

## Testing

### Manual Testing Checklist

- [ ] Store selection works (GPlay, AppStore, Both)
- [ ] Keywords can be entered directly and via file picker
- [ ] Country multi-select works correctly
- [ ] Collections dropdown only shows for AppStore
- [ ] API key is securely stored and retrieved
- [ ] Configuration persists across app restarts
- [ ] Progress stages display correctly
- [ ] Process can be cancelled
- [ ] Results display actual CSV data
- [ ] Results can be exported

## Future Enhancements

1. **Batch Resume**: Implement resumable polling if app crashes
2. **Advanced Filtering**: Filter/sort results in the results table
3. **Export Formats**: Support Excel, JSON exports in addition to CSV
4. **Real-time Logs**: Expandable log viewer in Progress tab
5. **Settings Screen**: API endpoint configuration, logging levels
6. **Notifications**: Desktop notifications for completion
7. **Platform-specific UI**: Adaptive UI for desktop (Windows native style)

## Desktop Considerations

The application is optimized for Windows and macOS desktop:

- Window resizing and responsive layouts
- Keyboard shortcuts (Ctrl+S to save, etc. - WIP)
- File dialogs use native file picker
- Secure storage adapts to platform

## Notes for Developers

1. **State Management**: Always update state through `AppStateProvider` to ensure UI consistency
2. **Process Execution**: Never block the main thread; use async subprocess calls
3. **File Paths**: Use `path_provider` for cross-platform path resolution
4. **API Key Handling**: Always store/retrieve via `SecureStorageService`, never log
5. **Testing**: Mock `ProcessService` and file operations for unit tests
