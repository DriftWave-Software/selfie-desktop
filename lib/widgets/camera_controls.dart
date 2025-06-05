import 'package:flutter/material.dart';

class CameraControls extends StatelessWidget {
  final double brightness;
  final double contrast;
  final int timerDuration;
  final Function(double) onBrightnessChanged;
  final Function(double) onContrastChanged;
  final Function(int) onTimerDurationChanged;
  final VoidCallback onCapture;
  final VoidCallback onCaptureWithTimer;
  final VoidCallback onCaptureMultiple;

  const CameraControls({
    super.key,
    required this.brightness,
    required this.contrast,
    required this.timerDuration,
    required this.onBrightnessChanged,
    required this.onContrastChanged,
    required this.onTimerDurationChanged,
    required this.onCapture,
    required this.onCaptureWithTimer,
    required this.onCaptureMultiple,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 24.0),
      decoration: BoxDecoration(
        color: Colors.black.withValues(red: 0, green: 0, blue: 0, alpha: 204), // 0.8 opacity
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(16.0),
          topRight: Radius.circular(16.0),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildControlRow('Brightness', brightness, -1.0, 1.0, onBrightnessChanged),
          const SizedBox(height: 8.0),
          _buildControlRow('Contrast', contrast, 0.5, 1.5, onContrastChanged),
          const SizedBox(height: 8.0),
          _buildTimerControl(),
          const SizedBox(height: 16.0),
          _buildCaptureButtons(),
        ],
      ),
    );
  }

  Widget _buildControlRow(
    String label,
    double value,
    double min,
    double max,
    Function(double) onChanged,
  ) {
    return Row(
      children: [
        SizedBox(
          width: 90,
          child: Text(
            label,
            style: const TextStyle(color: Colors.white),
          ),
        ),
        Expanded(
          child: Slider(
            value: value,
            min: min,
            max: max,
            divisions: 100,
            label: value.toStringAsFixed(2),
            onChanged: onChanged,
            activeColor: Colors.white,
          ),
        ),
        SizedBox(
          width: 50,
          child: Text(
            value.toStringAsFixed(2),
            style: const TextStyle(color: Colors.white),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Widget _buildTimerControl() {
    return Row(
      children: [
        const SizedBox(
          width: 90,
          child: Text(
            'Timer',
            style: TextStyle(color: Colors.white),
          ),
        ),
        Expanded(
          child: Wrap(
            alignment: WrapAlignment.spaceEvenly,
            children: [
              _buildTimerChip(3),
              _buildTimerChip(5),
              _buildTimerChip(10),
            ],
          ),
        ),
        SizedBox(
          width: 50,
          child: Text(
            '$timerDuration s',
            style: const TextStyle(color: Colors.white),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Widget _buildTimerChip(int seconds) {
    final isSelected = timerDuration == seconds;
    return GestureDetector(
      onTap: () => onTimerDurationChanged(seconds),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        margin: const EdgeInsets.only(right: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.grey[800],
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          '$seconds s',
          style: TextStyle(
            color: isSelected ? Colors.black : Colors.white,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _buildCaptureButtons() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildActionButton(
          icon: Icons.timer,
          label: 'Timer',
          onPressed: onCaptureWithTimer,
        ),
        _buildCaptureButton(),
        _buildActionButton(
          icon: Icons.burst_mode,
          label: '4 Shots',
          onPressed: onCaptureMultiple,
        ),
      ],
    );
  }

  Widget _buildCaptureButton() {
    return GestureDetector(
      onTap: onCapture,
      child: Container(
        height: 70,
        width: 70,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white, width: 3),
          color: Colors.transparent,
        ),
        child: Center(
          child: Container(
            height: 60,
            width: 60,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: Icon(icon, color: Colors.white),
          onPressed: onPressed,
          iconSize: 28,
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
