import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import '../providers/app_state_provider.dart';

class ResultsDisplay extends StatefulWidget {
  const ResultsDisplay({Key? key}) : super(key: key);

  @override
  State<ResultsDisplay> createState() => _ResultsDisplayState();
}

class _ResultsDisplayState extends State<ResultsDisplay> {
  List<List<String>> _csvData = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadResults();
  }

  Future<void> _loadResults() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      // Try to load the final CSV file
      final file = File('backend/output/final_classified_apps.csv');
      if (await file.exists()) {
        final content = await file.readAsString();
        final lines = content.split('\n');
        final data = lines
            .where((line) => line.isNotEmpty)
            .map((line) => line.split(','))
            .toList();

        setState(() {
          _csvData = data;
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Results file not found. Run processing first.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error loading results: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          const Text(
            'Results',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),

          // Refresh Button
          ElevatedButton.icon(
            onPressed: _loadResults,
            icon: const Icon(Icons.refresh),
            label: const Text('Reload Results'),
          ),
          const SizedBox(height: 24),

          // Error Message
          if (_errorMessage != null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Text(
                _errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            )
          else if (_isLoading)
            const Center(child: CircularProgressIndicator())
          else if (_csvData.isEmpty)
            const Center(child: Text('No data to display'))
          else
            _buildResultsTable(),
        ],
      ),
    );
  }

  Widget _buildResultsTable() {
    final headers = _csvData.isNotEmpty ? _csvData.first : [];
    final rows = _csvData.length > 1 ? _csvData.sublist(1) : [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Total Apps: ${rows.length}',
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: headers
                  .map(
                    (header) => DataColumn(
                      label: Text(
                        header.trim(),
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                  )
                  .toList(),
              rows: rows.take(50).map((row) {
                return DataRow(
                  cells: row
                      .map(
                        (cell) => DataCell(
                          Text(cell.trim(), overflow: TextOverflow.ellipsis),
                        ),
                      )
                      .toList(),
                );
              }).toList(),
            ),
          ),
        ),
        const SizedBox(height: 16),
        if (rows.length > 50)
          Text(
            'Showing first 50 of ${rows.length} results',
            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
          ),
        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: _exportResults,
          icon: const Icon(Icons.download),
          label: const Text('Export CSV'),
        ),
      ],
    );
  }

  Future<void> _exportResults() async {
    try {
      final file = File('backend/output/final_classified_apps.csv');
      if (await file.exists()) {
        // In a real app, you might use path_provider to get a suitable export location
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Results saved to: backend/output/final_classified_apps.csv',
            ),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error exporting results: $e')));
    }
  }
}
