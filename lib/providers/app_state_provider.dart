import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_configuration.dart';

class AppStateProvider with ChangeNotifier {
  AppConfiguration _configuration = AppConfiguration(
    targetStore: 'google_play',
    keywords: '',
    countries: ['US'],
    searchGooglePlayTopLists: false,
    topCollectionGenre: 'SPORTS',
    llmModel: 'gpt-4',
  );

  ProcessProgress _progress = ProcessProgress();

  String? _apiKey;
  List<String> _availableCountries = [];
  bool _isLoading = false;

  // Getters
  AppConfiguration get configuration => _configuration;
  ProcessProgress get progress => _progress;
  String? get apiKey => _apiKey;
  List<String> get availableCountries => _availableCountries;
  bool get isLoading => _isLoading;

  // Constructor
  AppStateProvider() {
    _initializeAvailableCountries();
    _loadSavedConfiguration();
  }

  // Initialize country list
  void _initializeAvailableCountries() {
    _availableCountries = [
      'US',
      'GB',
      'CA',
      'AU',
      'DE',
      'FR',
      'IT',
      'ES',
      'JP',
      'KR',
      'CN',
      'IN',
      'BR',
      'MX',
      'FI',
      'SE',
      'NO',
      'DK',
      'NL',
      'CH',
      'ZA',
      'NZ',
      'SG',
      'HK',
      'ID',
      'TH',
      'PL',
      'RU',
      'TR',
      'AE',
    ];
  }

  // Load saved configuration from shared_preferences
  Future<void> _loadSavedConfiguration() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final targetStore = prefs.getString('targetStore') ?? 'google_play';
      final keywords = prefs.getString('keywords') ?? '';
      final countries = prefs.getStringList('countries') ?? ['US'];
      final collection = prefs.getString('collection');
      final searchGooglePlayTopLists =
          prefs.getBool('searchGooglePlayTopLists') ?? false;
      final topCollectionGenre =
          prefs.getString('topCollectionGenre') ?? 'SPORTS';
      final llmModel = prefs.getString('llmModel') ?? 'gpt-4';

      _configuration = AppConfiguration(
        targetStore: targetStore,
        keywords: keywords,
        countries: countries,
        collection: collection,
        searchGooglePlayTopLists: searchGooglePlayTopLists,
        topCollectionGenre: topCollectionGenre,
        llmModel: llmModel,
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading saved configuration: $e');
    }
  }

  // Update configuration
  Future<void> updateConfiguration(AppConfiguration config) async {
    _configuration = config;

    // Save to shared_preferences
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('targetStore', config.targetStore);
      await prefs.setString('keywords', config.keywords);
      await prefs.setStringList('countries', config.countries);
      if (config.collection != null) {
        await prefs.setString('collection', config.collection!);
      }
      await prefs.setBool(
        'searchGooglePlayTopLists',
        config.searchGooglePlayTopLists,
      );
      await prefs.setString('topCollectionGenre', config.topCollectionGenre);
      await prefs.setString('llmModel', config.llmModel);
    } catch (e) {
      debugPrint('Error saving configuration: $e');
    }

    notifyListeners();
  }

  // Update target store
  void setTargetStore(String store) {
    _configuration = _configuration.copyWith(targetStore: store);
    notifyListeners();
  }

  // Update keywords
  void setKeywords(String keywords) {
    _configuration = _configuration.copyWith(keywords: keywords);
    notifyListeners();
  }

  // Update countries
  void setCountries(List<String> countries) {
    _configuration = _configuration.copyWith(countries: countries);
    notifyListeners();
  }

  // Update collection
  void setCollection(String? collection) {
    _configuration = _configuration.copyWith(collection: collection);
    notifyListeners();
  }

  void setSearchGooglePlayTopLists(bool enabled) {
    _configuration = _configuration.copyWith(searchGooglePlayTopLists: enabled);
    notifyListeners();
  }

  void setTopCollectionGenre(String genre) {
    _configuration = _configuration.copyWith(topCollectionGenre: genre);
    notifyListeners();
  }

  // Update LLM model
  void setLlmModel(String model) {
    _configuration = _configuration.copyWith(llmModel: model);
    notifyListeners();
  }

  // Set API key
  void setApiKey(String key) {
    _apiKey = key;
    notifyListeners();
  }

  // Update progress
  void updateProgress(ProcessProgress progress) {
    _progress = progress;
    notifyListeners();
  }

  // Update progress stage
  void setProgressStage(String stage, {String? message}) {
    _progress = _progress.copyWith(
      stage: stage,
      message: message ?? _progress.message,
    );
    notifyListeners();
  }

  // Update progress value
  void setProgressValue(double value) {
    _progress = _progress.copyWith(progress: value);
    notifyListeners();
  }

  // Set loading state
  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Reset progress
  void resetProgress() {
    _progress = ProcessProgress();
    notifyListeners();
  }

  // Reset all
  void resetAll() {
    _configuration = AppConfiguration(
      targetStore: 'google_play',
      keywords: '',
      countries: ['US'],
      searchGooglePlayTopLists: false,
      topCollectionGenre: 'SPORTS',
      llmModel: 'gpt-4',
    );
    _progress = ProcessProgress();
    _apiKey = null;
    notifyListeners();
  }
}
