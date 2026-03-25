class AppConfiguration {
  final String targetStore; // 'google_play' or 'app_store' or 'both'
  final String keywords; // Single keyword or path to .txt file
  final bool useEssentialQueries;
  final List<String> countries;
  final String? collection; // For App Store specific collections
  final bool searchTopCollections;
  final String llmModel;
  final bool useCustomApi;

  AppConfiguration({
    required this.targetStore,
    required this.keywords,
    this.useEssentialQueries = false,
    required this.countries,
    this.collection,
    this.searchTopCollections = false,
    this.llmModel = 'gpt-5-mini',
    this.useCustomApi = false,
  });

  AppConfiguration copyWith({
    String? targetStore,
    String? keywords,
    bool? useEssentialQueries,
    List<String>? countries,
    String? collection,
    bool? searchTopCollections,
    String? llmModel,
    bool? useCustomApi,
  }) {
    return AppConfiguration(
      targetStore: targetStore ?? this.targetStore,
      keywords: keywords ?? this.keywords,
      useEssentialQueries: useEssentialQueries ?? this.useEssentialQueries,
      countries: countries ?? this.countries,
      collection: collection ?? this.collection,
      searchTopCollections: searchTopCollections ?? this.searchTopCollections,
      llmModel: llmModel ?? this.llmModel,
      useCustomApi: useCustomApi ?? this.useCustomApi,
    );
  }
}

class ProcessProgress {
  final String
  stage; // 'idle', 'scraping', 'chunking', 'uploading', 'polling', 'merging', 'completed', 'error'
  final double progress; // 0.0 - 1.0
  final String message;
  final String? errorMessage;
  final List<String> batchIds;
  final DateTime? startTime;
  final DateTime? completionTime;

  ProcessProgress({
    this.stage = 'idle',
    this.progress = 0.0,
    this.message = 'Ready',
    this.errorMessage,
    this.batchIds = const [],
    this.startTime,
    this.completionTime,
  });

  ProcessProgress copyWith({
    String? stage,
    double? progress,
    String? message,
    String? errorMessage,
    List<String>? batchIds,
    DateTime? startTime,
    DateTime? completionTime,
  }) {
    return ProcessProgress(
      stage: stage ?? this.stage,
      progress: progress ?? this.progress,
      message: message ?? this.message,
      errorMessage: errorMessage ?? this.errorMessage,
      batchIds: batchIds ?? this.batchIds,
      startTime: startTime ?? this.startTime,
      completionTime: completionTime ?? this.completionTime,
    );
  }

  bool get isProcessing => [
    'scraping',
    'chunking',
    'uploading',
    'polling',
    'merging',
  ].contains(stage);
  bool get isCompleted => stage == 'completed';
  bool get hasError => stage == 'error';
}
