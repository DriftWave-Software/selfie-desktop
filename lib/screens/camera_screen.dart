import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../widgets/camera_controls.dart';
import '../widgets/captured_images.dart';
import '../widgets/filter_selector.dart';
import '../models/selfie_image.dart';
import '../utils/camera_utils.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  late List<CameraDescription> _cameras;
  CameraController? _controller;
  bool _isCameraInitialized = false;
  bool _isCapturing = false;
  
  // Camera settings
  double _brightness = 0.0; // Range from -1.0 to 1.0
  double _contrast = 1.0; // Range from 0.5 to 1.5
  int _timerDuration = 3; // Default timer duration in seconds
  bool _isTimerActive = false;
  int _timerValue = 0;
  
  // Background image
  File? _backgroundImage;
  bool _isUsingBackground = false;
  
  // Captured images
  final List<SelfieImage> _capturedImages = [];
  final int _maxImages = 4;
  SelfieImage? _currentlyEditing;

  // Timer
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    _timer?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Handle app lifecycle changes
    if (state == AppLifecycleState.inactive) {
      _controller?.dispose();
    } else if (state == AppLifecycleState.resumed) {
      if (_controller != null) {
        _initializeCamera();
      }
    }
  }

  Future<void> _initializeCamera() async {
    try {
      // Get available cameras
      _cameras = await availableCameras();
      
      if (_cameras.isEmpty) {
        setState(() {
          _isCameraInitialized = false;
        });
        return;
      }
      
      // By default, select the front camera for selfies
      final frontCameras = _cameras.where((camera) => 
        camera.lensDirection == CameraLensDirection.front).toList();
      
      final camera = frontCameras.isNotEmpty ? frontCameras.first : _cameras.first;
      
      // Initialize controller
      _controller = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      
      // Initialize the controller
      await _controller!.initialize();
      
      if (!mounted) return;
      
      setState(() {
        _isCameraInitialized = true;
      });
    } catch (e) {
      debugPrint('Error initializing camera: $e');
    }
  }

  Future<void> _takePicture() async {
    if (!_controller!.value.isInitialized || _isCapturing) {
      return;
    }
    
    setState(() {
      _isCapturing = true;
    });
    
    try {
      final XFile image = await _controller!.takePicture();
      
      // Create a new selfie image
      final newImage = SelfieImage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        path: image.path,
        appliedFilter: null,
        originalPath: image.path,
      );
      
      setState(() {
        if (_capturedImages.length < _maxImages) {
          _capturedImages.add(newImage);
        } else {
          // Replace the oldest image
          _capturedImages.removeAt(0);
          _capturedImages.add(newImage);
        }
        _isCapturing = false;
      });
    } catch (e) {
      debugPrint('Error taking picture: $e');
      setState(() {
        _isCapturing = false;
      });
    }
  }

  Future<void> _startTimerCapture() async {
    if (_isTimerActive) return;
    
    setState(() {
      _isTimerActive = true;
      _timerValue = _timerDuration;
    });
    
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        if (_timerValue > 0) {
          _timerValue--;
        } else {
          _isTimerActive = false;
          timer.cancel();
          _takePicture();
        }
      });
    });
  }

  Future<void> _selectBackgroundImage() async {
    final File? image = await CameraUtils.pickImage();
    if (image != null) {
      setState(() {
        _backgroundImage = image;
        _isUsingBackground = true;
      });
    }
  }

  void _toggleBackgroundImage() {
    setState(() {
      _isUsingBackground = !_isUsingBackground;
    });
  }

  void _updateBrightness(double value) {
    setState(() {
      _brightness = value;
    });
    // In a real implementation, you would update the camera settings here
    // This requires platform-specific implementation which is beyond this example
  }

  void _updateContrast(double value) {
    setState(() {
      _contrast = value;
    });
    // In a real implementation, you would update the camera settings here
  }

  void _updateTimerDuration(int seconds) {
    setState(() {
      _timerDuration = seconds;
    });
  }

  void _editImage(SelfieImage image) {
    setState(() {
      _currentlyEditing = image;
    });
  }

  void _applyFilter(String filterId) {
    if (_currentlyEditing != null) {
      setState(() {
        // In a real app, you would apply the filter here
        // For now, we'll just update the filter ID
        _currentlyEditing = _currentlyEditing!.copyWith(appliedFilter: filterId);
        
        // Update the image in the list
        final index = _capturedImages.indexWhere((img) => img.id == _currentlyEditing!.id);
        if (index != -1) {
          _capturedImages[index] = _currentlyEditing!;
        }
      });
    }
  }

  void _cancelEditing() {
    setState(() {
      _currentlyEditing = null;
    });
  }

  void _takeMultipleShots() async {
    // Take 4 shots with timer between each
    if (_capturedImages.length >= _maxImages) {
      // Clear existing images if we already have 4
      setState(() {
        _capturedImages.clear();
      });
    }
    
    for (int i = 0; i < _maxImages; i++) {
      if (!mounted) return;
      
      // Wait for timer duration between shots
      await _startTimerCapture();
      
      // Wait for the timer to finish and picture to be taken
      while (_isTimerActive || _isCapturing) {
        await Future.delayed(const Duration(milliseconds: 100));
      }
      
      // Short pause between shots
      await Future.delayed(const Duration(milliseconds: 500));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isCameraInitialized) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Selfie Desktop'),
        actions: [
          IconButton(
            icon: Icon(_isUsingBackground ? Icons.image : Icons.image_not_supported),
            onPressed: _backgroundImage != null ? _toggleBackgroundImage : _selectBackgroundImage,
            tooltip: 'Toggle background image',
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 3,
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Background image if enabled
                if (_isUsingBackground && _backgroundImage != null)
                  Positioned.fill(
                    child: Opacity(
                      opacity: 0.7, // Semi-transparent
                      child: Image.file(
                        _backgroundImage!,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                
                // Camera preview
                CameraPreview(_controller!),
                
                // Timer overlay
                if (_isTimerActive)
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.black54,
                      borderRadius: BorderRadius.circular(50),
                    ),
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      _timerValue.toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 72,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          
          // Camera controls
          CameraControls(
            brightness: _brightness,
            contrast: _contrast,
            timerDuration: _timerDuration,
            onBrightnessChanged: _updateBrightness,
            onContrastChanged: _updateContrast,
            onTimerDurationChanged: _updateTimerDuration,
            onCapture: _takePicture,
            onCaptureWithTimer: _startTimerCapture,
            onCaptureMultiple: _takeMultipleShots,
          ),
          
          // Captured images at the bottom
          CapturedImages(
            images: _capturedImages,
            onImageTap: _editImage,
          ),
        ],
      ),
      
      // Filter selector sheet when editing an image
      bottomSheet: _currentlyEditing != null
          ? FilterSelector(
              image: _currentlyEditing!,
              onFilterSelected: _applyFilter,
              onCancel: _cancelEditing,
            )
          : null,
    );
  }
}
