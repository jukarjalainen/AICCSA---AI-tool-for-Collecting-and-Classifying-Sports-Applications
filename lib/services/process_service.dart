import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';

class ProcessService {
  static const String scraperEntrypoint = 'backend/COMPLETE_SCRAPER.js';

  // Start the scraping and processing pipeline
  static Future<Process> startProcessing({
    required String targetStore,
    required String keywords,
    required bool useEssentialQueries,
    required List<String> countries,
    required String llmModel,
    required bool searchTopCollections,
    String? apiKey,
  }) async {
    try {
      final args = [
        scraperEntrypoint,
        '--store=$targetStore',
        '--keywords=$keywords',
        '--use-essential-queries=$useEssentialQueries',
        '--countries=${countries.join(",")}',
        '--model=$llmModel',
        '--search-top-collections=$searchTopCollections',
        '--top-collection-stores=$targetStore',
        '--top-collection-categories=SPORTS,HEALTH_AND_FITNESS',
        if (apiKey != null) '--api-key=$apiKey',
      ];

      debugPrint('[ProcessService] Starting Node scraper with args: $args');

      final process = await Process.start(
        'node',
        args,
        mode: ProcessStartMode.normal,
      );

      return process;
    } catch (e) {
      debugPrint('[ProcessService] Error starting process: $e');
      rethrow;
    }
  }

  // Read batch status from local file
  static Future<Map<String, dynamic>> getBatchStatus() async {
    try {
      final file = File('backend/batch_status.json');
      if (await file.exists()) {
        final content = await file.readAsString();
        return jsonDecode(content) as Map<String, dynamic>;
      }
      return {'batches': [], 'status': 'idle'};
    } catch (e) {
      debugPrint('[ProcessService] Error reading batch status: $e');
      return {'batches': [], 'status': 'error', 'error': e.toString()};
    }
  }

  // Poll batch status
  static Stream<Map<String, dynamic>> pollBatchStatus({
    Duration interval = const Duration(seconds: 5),
  }) {
    return Stream.periodic(interval, (_) {
      return getBatchStatus();
    }).asyncMap((event) async => await event);
  }

  // Cancel processing
  static Future<void> cancelProcessing(Process process) async {
    try {
      process.kill();
      debugPrint('[ProcessService] Process cancelled');
    } catch (e) {
      debugPrint('[ProcessService] Error cancelling process: $e');
    }
  }

  // Stream stdout from process
  static Stream<String> streamProcessOutput(Process process) {
    return process.stdout
        .transform(utf8.decoder)
        .transform(const LineSplitter());
  }

  // Stream stderr from process
  static Stream<String> streamProcessError(Process process) {
    return process.stderr
        .transform(utf8.decoder)
        .transform(const LineSplitter());
  }
}
