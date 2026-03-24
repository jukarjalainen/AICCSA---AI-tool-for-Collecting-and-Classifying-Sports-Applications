import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/foundation.dart';

class SecureStorageService {
  static const String _apiKeyKey = 'openai_api_key';

  static const FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      keyCipherAlgorithm:
          KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
      storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
    ),
  );

  // Save API key securely
  static Future<void> saveApiKey(String apiKey) async {
    try {
      await _storage.write(key: _apiKeyKey, value: apiKey);
      debugPrint('[SecureStorage] API key saved');
    } catch (e) {
      debugPrint('[SecureStorage] Error saving API key: $e');
      rethrow;
    }
  }

  // Retrieve API key
  static Future<String?> getApiKey() async {
    try {
      return await _storage.read(key: _apiKeyKey);
    } catch (e) {
      debugPrint('[SecureStorage] Error retrieving API key: $e');
      return null;
    }
  }

  // Delete API key
  static Future<void> deleteApiKey() async {
    try {
      await _storage.delete(key: _apiKeyKey);
      debugPrint('[SecureStorage] API key deleted');
    } catch (e) {
      debugPrint('[SecureStorage] Error deleting API key: $e');
    }
  }

  // Check if API key exists
  static Future<bool> hasApiKey() async {
    try {
      final key = await _storage.read(key: _apiKeyKey);
      return key != null && key.isNotEmpty;
    } catch (e) {
      debugPrint('[SecureStorage] Error checking API key: $e');
      return false;
    }
  }
}
