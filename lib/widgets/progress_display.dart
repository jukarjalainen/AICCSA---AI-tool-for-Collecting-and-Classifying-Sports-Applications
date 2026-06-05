import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/app_configuration.dart';
import '../providers/app_state_provider.dart';

class ProgressDisplay extends StatefulWidget {
  const ProgressDisplay({Key? key}) : super(key: key);

  @override
  State<ProgressDisplay> createState() => _ProgressDisplayState();
}

class _ProgressDisplayState extends State<ProgressDisplay> {
  Timer? _clockTimer;
  DateTime _now = DateTime.now();

  @override
  void initState() {
    super.initState();
    _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        _now = DateTime.now();
      });
    });
  }

  @override
  void dispose() {
    _clockTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppStateProvider>(
      builder: (context, appState, _) {
        final progress = appState.progress;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title
              const Text(
                'Processing Progress',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),

              // Overall Progress Bar
              if (progress.isProcessing) ...[
                const Text(
                  'Overall Progress',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: progress.progress,
                    minHeight: 8,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${(progress.progress * 100).toStringAsFixed(1)}%',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 24),
              ],

              if (progress.isProcessing && progress.stage == 'scraping') ...[
                _buildScrapingEta(progress, _now),
                const SizedBox(height: 24),
              ],

              // Status Card
              _buildStatusCard(progress, context),
              const SizedBox(height: 24),

              // Stage Details
              _buildStageDetails(progress),
              const SizedBox(height: 24),

              // Batch Information
              if (progress.batchIds.isNotEmpty) ...[
                _buildBatchInformation(progress),
                const SizedBox(height: 24),
              ],

              // Error Message
              if (progress.hasError && progress.errorMessage != null) ...[
                _buildErrorMessage(progress.errorMessage!),
                const SizedBox(height: 24),
              ],

              // Timeline (simplified)
              _buildTimeline(progress),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatusCard(ProcessProgress progress, BuildContext context) {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    if (progress.hasError) {
      statusColor = Colors.red;
      statusIcon = Icons.error;
      statusText = 'Error';
    } else if (progress.isCompleted) {
      statusColor = Colors.green;
      statusIcon = Icons.check_circle;
      statusText = 'Completed';
    } else if (progress.isProcessing) {
      statusColor = Colors.orange;
      statusIcon = Icons.hourglass_bottom;
      statusText = _getStageLabel(progress.stage);
    } else {
      statusColor = Colors.grey;
      statusIcon = Icons.info;
      statusText = 'Ready';
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        border: Border.all(color: statusColor),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(statusIcon, color: statusColor, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  progress.message,
                  style: const TextStyle(fontSize: 14, color: Colors.grey),
                ),
                if (progress.stage == 'polling') ...[
                  const SizedBox(height: 6),
                  const Text(
                    'Polling means checking OpenAI batch status every 5 seconds until results are ready.',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ],
            ),
          ),
          if (progress.isProcessing)
            const SizedBox(
              width: 32,
              height: 32,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
        ],
      ),
    );
  }

  Widget _buildStageDetails(ProcessProgress progress) {
    const stages = [
      'scraping',
      'chunking',
      'uploading',
      'polling',
      'merging',
      'completed',
    ];
    const stageLabels = [
      'Scraping',
      'Chunking Data',
      'Uploading to API',
      'Polling Batch Status',
      'Merging Data',
      'Completed',
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Pipeline Stages',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        ...List.generate(stages.length, (index) {
          final stage = stages[index];
          final label = stageLabels[index];
          final isCompleted =
              stages.indexOf(progress.stage) >= index || progress.isCompleted;
          final isCurrent = progress.stage == stage && progress.isProcessing;

          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isCurrent
                        ? Colors.orange
                        : isCompleted
                        ? Colors.green
                        : Colors.grey.shade300,
                  ),
                  child: Center(
                    child: isCurrent
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.white,
                              ),
                              strokeWidth: 2,
                            ),
                          )
                        : Icon(
                            isCompleted ? Icons.check : Icons.circle_outlined,
                            color: isCompleted
                                ? Colors.white
                                : Colors.grey.shade600,
                            size: 14,
                          ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    color: isCurrent ? Colors.orange : Colors.black,
                    fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildBatchInformation(ProcessProgress progress) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Active Batches',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          ...progress.batchIds.asMap().entries.map((entry) {
            final index = entry.key;
            final batchId = entry.value;
            return Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Text(
                    'Batch ${index + 1}:',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      batchId,
                      style: const TextStyle(
                        fontSize: 12,
                        fontFamily: 'monospace',
                        color: Colors.grey,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildErrorMessage(String errorMessage) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Error Details',
            style: TextStyle(fontWeight: FontWeight.w600, color: Colors.red),
          ),
          const SizedBox(height: 8),
          Text(errorMessage, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildTimeline(ProcessProgress progress) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Timeline', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          if (progress.startTime != null)
            Text(
              'Started: ${progress.startTime!.toString().split('.').first}',
              style: const TextStyle(fontSize: 12),
            ),
          if (progress.completionTime != null) ...[
            const SizedBox(height: 4),
            Text(
              'Completed: ${progress.completionTime!.toString().split('.').first}',
              style: const TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 4),
            Text(
              'Duration: ${_formatDuration(progress.completionTime!.difference(progress.startTime!))}',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildScrapingEta(ProcessProgress progress, DateTime now) {
    final startTime = progress.startTime;
    if (startTime == null) {
      return const SizedBox.shrink();
    }

    final elapsed = now.difference(startTime);
    final remaining = _estimateScrapingRemaining(progress, elapsed);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Scraping Time Estimate',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'Elapsed: ${_formatDuration(elapsed)}',
            style: const TextStyle(fontSize: 12),
          ),
          const SizedBox(height: 4),
          Text(
            remaining == null
                ? 'Estimating remaining time...'
                : 'Estimated remaining: ${_formatDuration(remaining)}',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 4),
          const Text(
            'Estimate is based on current progress speed and may vary by API/network response times.',
            style: TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Duration? _estimateScrapingRemaining(
    ProcessProgress progress,
    Duration elapsed,
  ) {
    const scrapingTargetProgress = 0.45;
    final currentProgress = progress.progress.clamp(0.0, 1.0);
    final elapsedSeconds = elapsed.inSeconds;

    if (elapsedSeconds < 5 || currentProgress <= 0.01) {
      return null;
    }

    if (currentProgress >= scrapingTargetProgress) {
      return Duration.zero;
    }

    final progressPerSecond = currentProgress / elapsedSeconds;
    if (progressPerSecond <= 0) {
      return null;
    }

    final estimatedTotalScrapingSeconds =
        scrapingTargetProgress / progressPerSecond;
    final remainingSeconds = (estimatedTotalScrapingSeconds - elapsedSeconds)
        .ceil();

    if (remainingSeconds <= 0) {
      return Duration.zero;
    }

    if (remainingSeconds > 6 * 60 * 60) {
      return null;
    }

    return Duration(seconds: remainingSeconds);
  }

  String _getStageLabel(String stage) {
    const labels = {
      'scraping': 'Scraping App Store',
      'chunking': 'Processing Data',
      'uploading': 'Uploading to OpenAI',
      'polling': 'Polling OpenAI Batch Status',
      'merging': 'Merging Results',
    };
    return labels[stage] ?? 'Processing';
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds.remainder(60);
    if (minutes > 0) {
      return '${minutes}m ${seconds}s';
    }
    return '${seconds}s';
  }
}
