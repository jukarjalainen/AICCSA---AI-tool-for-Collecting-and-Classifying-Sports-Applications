import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../models/app_configuration.dart';
import '../providers/app_state_provider.dart';
import '../services/secure_storage_service.dart';

class ConfigurationForm extends StatefulWidget {
  final Function(AppConfiguration) onConfigurationChanged;

  const ConfigurationForm({super.key, required this.onConfigurationChanged});

  @override
  State<ConfigurationForm> createState() => _ConfigurationFormState();
}

class _ConfigurationFormState extends State<ConfigurationForm> {
  late TextEditingController _keywordsController;
  late TextEditingController _apiKeyController;
  String? _selectedFile;
  bool _showApiKey = false;
  bool _showCountriesDropdown = false;

  @override
  void initState() {
    super.initState();
    _keywordsController = TextEditingController();
    _apiKeyController = TextEditingController();
    _loadApiKey();
  }

  @override
  void dispose() {
    _keywordsController.dispose();
    _apiKeyController.dispose();
    super.dispose();
  }

  Future<void> _loadApiKey() async {
    final apiKey = await SecureStorageService.getApiKey();
    if (mounted && apiKey != null) {
      setState(() {
        _apiKeyController.text = apiKey;
      });
    }
  }

  Future<void> _pickKeywordsFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt'],
      );

      if (result != null && result.files.isNotEmpty) {
        setState(() {
          _selectedFile = result.files.first.path;
          _keywordsController.text = _selectedFile!;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error picking file: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppStateProvider>(
      builder: (context, appState, _) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title
              const Text(
                'AICCSA Configuration',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),

              // Target Store Selection
              const Text(
                'Target Store',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  _buildStoreButton('google_play', 'Google Play', appState),
                  _buildStoreButton('app_store', 'Apple App Store', appState),
                  _buildStoreButton('both', 'Both', appState),
                ],
              ),
              const SizedBox(height: 24),

              // Keywords Input
              const Text(
                'Keywords',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _keywordsController,
                      decoration: InputDecoration(
                        hintText:
                            'Enter keywords (comma-separated) or select a file',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 12,
                        ),
                      ),
                      onChanged: (value) {
                        appState.setKeywords(value);
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: _pickKeywordsFile,
                    icon: const Icon(Icons.folder_open),
                    label: const Text('Browse'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Countries Selection
              const Text(
                'Countries',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: () {
                  setState(() {
                    _showCountriesDropdown = !_showCountriesDropdown;
                  });
                },
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade400),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          _buildCountriesSummary(
                            appState.configuration.countries,
                            appState.availableCountries.length,
                          ),
                        ),
                      ),
                      Icon(
                        _showCountriesDropdown
                            ? Icons.keyboard_arrow_up
                            : Icons.keyboard_arrow_down,
                      ),
                    ],
                  ),
                ),
              ),
              if (_showCountriesDropdown) ...[
                const SizedBox(height: 8),
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      CheckboxListTile(
                        dense: true,
                        title: const Text('Select all countries'),
                        value:
                            appState.configuration.countries.length ==
                            appState.availableCountries.length,
                        onChanged: (selected) {
                          if (selected == true) {
                            appState.setCountries(
                              List<String>.from(appState.availableCountries),
                            );
                          } else {
                            appState.setCountries([]);
                          }
                        },
                      ),
                      const Divider(height: 1),
                      ConstrainedBox(
                        constraints: const BoxConstraints(maxHeight: 220),
                        child: ListView(
                          shrinkWrap: true,
                          children: appState.availableCountries.map((country) {
                            final isSelected = appState.configuration.countries
                                .contains(country);
                            return CheckboxListTile(
                              dense: true,
                              controlAffinity: ListTileControlAffinity.leading,
                              title: Text(country),
                              value: isSelected,
                              onChanged: (selected) {
                                final countries = List<String>.from(
                                  appState.configuration.countries,
                                );
                                if (selected == true) {
                                  if (!countries.contains(country)) {
                                    countries.add(country);
                                  }
                                } else {
                                  countries.remove(country);
                                }
                                appState.setCountries(countries);
                              },
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 24),

              const Text(
                'Top Collections',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              const Text(
                'All available collections are always searched for both stores.',
                style: TextStyle(fontSize: 12, color: Colors.black54),
              ),
              const SizedBox(height: 8),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Search Google Play top lists'),
                value: appState.configuration.searchGooglePlayTopLists,
                onChanged: (value) {
                  appState.setSearchGooglePlayTopLists(value);
                },
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: appState.configuration.topCollectionGenre,
                decoration: InputDecoration(
                  labelText: 'Top collection genre',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: 'SPORTS', child: Text('SPORTS')),
                  DropdownMenuItem(
                    value: 'HEALTH_AND_FITNESS',
                    child: Text('HEALTH_AND_FITNESS'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    appState.setTopCollectionGenre(value);
                  }
                },
              ),
              const SizedBox(height: 24),

              // LLM Model Selection
              const Text(
                'LLM Model',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: appState.configuration.llmModel,
                decoration: InputDecoration(
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: 'gpt-4', child: Text('GPT-4')),
                  DropdownMenuItem(
                    value: 'gpt-4-turbo',
                    child: Text('GPT-4 Turbo'),
                  ),
                  DropdownMenuItem(
                    value: 'gpt-3.5-turbo',
                    child: Text('GPT-3.5 Turbo'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    appState.setLlmModel(value);
                  }
                },
              ),
              const SizedBox(height: 24),

              // OpenAI API Key
              const Text(
                'OpenAI API Key',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _apiKeyController,
                obscureText: !_showApiKey,
                decoration: InputDecoration(
                  hintText: 'Enter your OpenAI API key',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _showApiKey ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() {
                        _showApiKey = !_showApiKey;
                      });
                    },
                  ),
                ),
                onChanged: (value) {
                  appState.setApiKey(value);
                },
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Checkbox(
                    value: appState.configuration.useCustomApi,
                    onChanged: (value) {
                      if (value == true && _apiKeyController.text.isNotEmpty) {
                        SecureStorageService.saveApiKey(_apiKeyController.text);
                        appState.updateConfiguration(
                          appState.configuration.copyWith(useCustomApi: true),
                        );
                      }
                    },
                  ),
                  const Expanded(child: Text('Save API key securely')),
                ],
              ),
              const SizedBox(height: 32),

              // Info Box
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'About this pipeline:',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    SizedBox(height: 8),
                    Text(
                      '• Scrapes app data from selected stores\n'
                      '• Processes data through OpenAI Batch API\n'
                      '• Classifies apps into user groups, sports types, and purposes\n'
                      '• Generates final classified CSV export',
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStoreButton(
    String value,
    String label,
    AppStateProvider appState,
  ) {
    final isSelected = appState.configuration.targetStore == value;
    return ElevatedButton(
      onPressed: () {
        appState.setTargetStore(value);
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected
            ? Theme.of(context).primaryColor
            : Colors.grey.shade300,
        foregroundColor: isSelected ? Colors.white : Colors.black,
      ),
      child: Text(label),
    );
  }

  String _buildCountriesSummary(List<String> selectedCountries, int total) {
    if (selectedCountries.isEmpty) {
      return 'Select countries';
    }
    if (selectedCountries.length == total) {
      return 'All countries selected';
    }
    return '${selectedCountries.length} countries selected';
  }
}
