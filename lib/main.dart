import 'dart:io';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/app_state_provider.dart';
import 'widgets/configuration_form.dart';
import 'widgets/progress_display.dart';
import 'widgets/results_display.dart';
import 'services/process_service.dart';
import 'services/secure_storage_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppStateProvider(),
      child: MaterialApp(
        title: 'AICCSA',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF2E7D32),
            brightness: Brightness.light,
          ),
        ),
        home: const HomePage(),
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentTabIndex = 0;
  Process? _currentProcess;
  StreamSubscription<Map<String, dynamic>>? _batchStatusSubscription;

  @override
  void initState() {
    super.initState();
    _loadSavedApiKey();
  }

  Future<void> _loadSavedApiKey() async {
    final apiKey = await SecureStorageService.getApiKey();
    if (apiKey != null && mounted) {
      context.read<AppStateProvider>().setApiKey(apiKey);
    }
  }

  Future<void> _startProcessing() async {
    final appState = context.read<AppStateProvider>();
    final config = appState.configuration;

    // Validate configuration
    if (config.targetStore.isEmpty) {
      _showErrorSnackBar('Please select at least one target store');
      return;
    }

    if (!config.useEssentialQueries && config.keywords.isEmpty) {
      _showErrorSnackBar('Please enter keywords or select a file');
      return;
    }

    if (config.countries.isEmpty) {
      _showErrorSnackBar('Please select at least one country');
      return;
    }

    if (!config.scrapeOnly &&
        (appState.apiKey == null || appState.apiKey!.isEmpty)) {
      _showErrorSnackBar('Please enter your OpenAI API key');
      return;
    }

    try {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'scraping',
          progress: 0.0,
          message: 'Starting scraping process...',
          startTime: DateTime.now(),
        ),
      );

      // Start processing
      _currentProcess = await ProcessService.startProcessing(
        targetStore: config.targetStore,
        keywords: config.keywords,
        useEssentialQueries: config.useEssentialQueries,
        countries: config.countries,
        llmModel: config.llmModel,
        searchTopCollections: config.searchTopCollections,
        scrapeOnly: config.scrapeOnly,
        apiKey: appState.apiKey,
      );

      // Stream stdout
      ProcessService.streamProcessOutput(_currentProcess!).listen((line) {
        debugPrint('[Output] $line');
        _updateProgressFromOutput(line, appState);
      });

      // Stream stderr
      ProcessService.streamProcessError(_currentProcess!).listen((line) {
        debugPrint('[Error] $line');
      });

      if (!config.scrapeOnly) {
        _batchStatusSubscription?.cancel();
        _batchStatusSubscription = ProcessService.pollBatchStatus().listen((
          status,
        ) {
          final batches = (status['batches'] as List<dynamic>? ?? []);
          final batchIds = batches
              .map(
                (b) => b is Map<String, dynamic>
                    ? (b['batchId']?.toString() ?? '')
                    : '',
              )
              .where((id) => id.isNotEmpty)
              .toList();

          if (batchIds.isNotEmpty || status['status'] == 'error') {
            final stage = status['stage']?.toString();
            final mappedStage =
                stage == 'uploading' || stage == 'polling' || stage == 'merging'
                ? stage
                : appState.progress.stage;
            appState.updateProgress(
              appState.progress.copyWith(
                stage: mappedStage,
                batchIds: batchIds,
                message: status['status'] == 'error'
                    ? 'Batch status reported an error'
                    : appState.progress.message,
              ),
            );
          }
        });
      }

      // Wait for process to complete
      final exitCode = await _currentProcess!.exitCode;
      await _batchStatusSubscription?.cancel();
      _batchStatusSubscription = null;
      if (exitCode == 0) {
        appState.updateProgress(
          appState.progress.copyWith(
            stage: 'completed',
            progress: 1.0,
            message: 'Processing completed successfully!',
            completionTime: DateTime.now(),
          ),
        );
        _showSuccessSnackBar('Processing completed!');
        setState(() {
          _currentTabIndex = 2; // Switch to results tab
        });
      } else {
        appState.updateProgress(
          appState.progress.copyWith(
            stage: 'error',
            errorMessage: 'Process exited with code $exitCode',
          ),
        );
        _showErrorSnackBar('Processing failed. Check logs for details.');
      }
    } catch (e) {
      appState.updateProgress(
        appState.progress.copyWith(stage: 'error', errorMessage: e.toString()),
      );
      _showErrorSnackBar('Error: $e');
    }
  }

  void _updateProgressFromOutput(String line, AppStateProvider appState) {
    final lower = line.toLowerCase();

    if (lower.contains('starting parallel scraping') ||
        lower.contains('starting apple app store collection') ||
        lower.contains('starting google play store collection')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'scraping',
          message: 'Scraping app store data...',
        ),
      );
    } else if (lower.contains('[batch] scrape-descriptions')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'scraping',
          message: 'Fetching app descriptions by appId...',
          progress: 0.2,
        ),
      );
    } else if (lower.contains('[batch] build-input') ||
        lower.contains('wrote batch input:')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'chunking',
          message: 'Building OpenAI batch input chunks...',
          progress: 0.45,
        ),
      );
    } else if (lower.contains('[batch] submit-openai') ||
        lower.contains('batch submitted:')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'uploading',
          message: 'Submitting chunks to OpenAI Batch API...',
          progress: 0.65,
        ),
      );
    } else if (lower.contains('batch status:')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'polling',
          message: 'Waiting for classification results...',
          progress: 0.8,
        ),
      );
    } else if (lower.contains('[batch] merge-results') ||
        lower.contains('wrote:') &&
            lower.contains('apps_with_classification_')) {
      appState.updateProgress(
        appState.progress.copyWith(
          stage: 'merging',
          message: 'Merging classification into final XLSX...',
          progress: 0.95,
        ),
      );
    }
  }

  Future<void> _cancelProcessing() async {
    if (_currentProcess != null) {
      await ProcessService.cancelProcessing(_currentProcess!);
      await _batchStatusSubscription?.cancel();
      _batchStatusSubscription = null;
      if (!mounted) return;
      context.read<AppStateProvider>().resetProgress();
      _showErrorSnackBar('Processing cancelled');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppStateProvider>(
      builder: (context, appState, _) {
        return Scaffold(
          appBar: AppBar(
            title: const Text(
              'AICCSA - AI tool for collecting and classifying sports applications',
            ),
            elevation: 2,
          ),
          body: IndexedStack(
            index: _currentTabIndex,
            children: [
              ConfigurationForm(
                onConfigurationChanged: (config) {
                  appState.updateConfiguration(config);
                },
              ),
              const ProgressDisplay(),
              const ResultsDisplay(),
            ],
          ),
          bottomNavigationBar: BottomNavigationBar(
            currentIndex: _currentTabIndex,
            onTap: (index) {
              setState(() {
                _currentTabIndex = index;
              });
            },
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.settings),
                label: 'Configuration',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.timeline),
                label: 'Progress',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.assessment),
                label: 'Results',
              ),
            ],
          ),
          floatingActionButton: appState.progress.isProcessing
              ? FloatingActionButton(
                  onPressed: _cancelProcessing,
                  backgroundColor: Colors.red,
                  child: const Icon(Icons.stop),
                )
              : FloatingActionButton.extended(
                  onPressed: _startProcessing,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Start Processing'),
                ),
        );
      },
    );
  }

  @override
  void dispose() {
    if (_currentProcess != null) {
      ProcessService.cancelProcessing(_currentProcess!);
    }
    _batchStatusSubscription?.cancel();
    super.dispose();
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return const Scaffold();
  }
}
