import 'package:flutter/material.dart';
import '../utils/app_theme.dart';
import '../widgets/top_bar.dart';

class CameraSettings {
  double brightness;
  double contrast;
  
  CameraSettings({
    this.brightness = 0.0,
    this.contrast = 0.0,
  });
  
  CameraSettings copyWith({
    double? brightness,
    double? contrast,
  }) {
    return CameraSettings(
      brightness: brightness ?? this.brightness,
      contrast: contrast ?? this.contrast,
    );
  }
}

class CameraSettingsScreen extends StatefulWidget {
  final CameraSettings initialSettings;
  final Function(CameraSettings) onSettingsChanged;
  
  const CameraSettingsScreen({
    Key? key,
    required this.initialSettings,
    required this.onSettingsChanged,
  }) : super(key: key);
  
  @override
  _CameraSettingsScreenState createState() => _CameraSettingsScreenState();
}

class _CameraSettingsScreenState extends State<CameraSettingsScreen> {
  late CameraSettings _settings;
  
  @override
  void initState() {
    super.initState();
    _settings = widget.initialSettings;
  }
  
  void _updateSettings() {
    widget.onSettingsChanged(_settings);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBackground,
      body: Column(
        children: [
          TopBar(
            title: 'Camera Settings',
            onBackPressed: () {
              _updateSettings();
              Navigator.pop(context);
            },
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSettingHeader('Camera Settings'),
                    const SizedBox(height: 24),
                    _buildSliderSetting(
                      'Brightness',
                      _settings.brightness,
                      -1.0,
                      1.0,
                      (value) {
                        setState(() {
                          _settings = _settings.copyWith(brightness: value);
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    _buildSliderSetting(
                      'Contrast',
                      _settings.contrast,
                      -1.0,
                      1.0,
                      (value) {
                        setState(() {
                          _settings = _settings.copyWith(contrast: value);
                        });
                      },
                    ),
                    const SizedBox(height: 32),
                    Center(
                      child: ElevatedButton(
                        onPressed: () {
                          setState(() {
                            _settings = CameraSettings();
                          });
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[800],
                        ),
                        child: const Text('Reset to Default'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: ElevatedButton(
              onPressed: () {
                _updateSettings();
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
              child: const Text('Apply Settings'),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSettingHeader(String title) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: AppTheme.primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.camera, color: AppTheme.primaryColor),
          const SizedBox(width: 12),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSliderSetting(
    String label,
    double value,
    double min,
    double max,
    Function(double) onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
              ),
            ),
            Text(
              value.toStringAsFixed(2),
              style: TextStyle(
                color: Colors.grey[400],
                fontSize: 16,
              ),
            ),
          ],
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: 40,
          activeColor: AppTheme.primaryColor,
          inactiveColor: Colors.grey[800],
          onChanged: onChanged,
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              min.toStringAsFixed(1),
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            Text(
              '0.0',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            Text(
              max.toStringAsFixed(1),
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
