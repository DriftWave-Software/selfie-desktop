import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../models/event.dart';
import '../utils/app_theme.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';
import 'camera_settings_screen.dart';
import 'package:permission_handler/permission_handler.dart';

class CameraScreen extends StatefulWidget {
  final Event event;
  final String experienceType;

  const CameraScreen({
    Key? key,
    required this.event,
    required this.experienceType,
  }) : super(key: key);

  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  bool _isInitialized = false;
  bool _isCapturing = false;
  String? _capturedImagePath;
  bool _isUploading = false;
  String _errorMessage = '';
  
  // Camera settings
  CameraSettings _cameraSettings = CameraSettings();
  
  // Timer related variables
  bool _isCountdownActive = false;
  int _countdownValue = 3;

  @override
  void initState() {
    super.initState();
    _checkPermissionsAndInitializeCamera();
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  Future<void> _checkPermissionsAndInitializeCamera() async {
    // First, check current permission status
    PermissionStatus status = await Permission.camera.status;
    
    // If not determined yet, request permission
    if (status.isDenied || status.isRestricted) {
      status = await Permission.camera.request();
    }
    
    if (status.isGranted) {
      _initializeCamera();
    } else if (status.isPermanentlyDenied) {
      // If permanently denied, show a message instructing to open settings
      setState(() {
        _errorMessage = 'Camera access is required for this app. You have permanently denied camera permission. Please enable it in device settings to continue.';
      });
      // Show dialog forcing user to open settings
      _showForcePermissionDialog(true);
    } else {
      // If denied but not permanently, explain and request again
      setState(() {
        _errorMessage = 'Camera access is required for this app. You must grant camera permission to continue.';
      });
      // Show dialog forcing user to grant permission
      _showForcePermissionDialog(false);
    }
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      
      if (_cameras.isEmpty) {
        setState(() {
          _errorMessage = 'No cameras found';
        });
        return;
      }
      
      // Start with the first camera
      await _setupCamera(_cameras[0]);
    } catch (e) {
      setState(() {
        _errorMessage = 'Error initializing camera: $e';
      });
    }
  }
  
  Future<void> _setupCamera(CameraDescription camera) async {
    _controller = CameraController(
      camera,
      ResolutionPreset.high,
      enableAudio: widget.experienceType == 'video',
      imageFormatGroup: ImageFormatGroup.jpeg,
    );
    
    try {
      await _controller!.initialize();
      
      // Apply camera settings if available
      await _applyCameraSettings();
      
      // Start image stream for live view
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error initializing camera controller: $e';
      });
    }
  }
  
  Future<void> _applyCameraSettings() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    
    try {
      // Apply brightness and contrast settings if supported
      await _controller!.setExposureOffset(_cameraSettings.brightness);
      
      // Note: Contrast isn't directly exposed in the camera plugin,
      // but we're keeping the setting for future implementation
    } catch (e) {
      print('Error applying camera settings: $e');
    }
  }
  
  void _openCameraSettings() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CameraSettingsScreen(
          initialSettings: _cameraSettings,
          onSettingsChanged: (newSettings) {
            setState(() {
              _cameraSettings = newSettings;
            });
            _applyCameraSettings();
          },
        ),
      ),
    );
  }

  Future<void> _startCountdown() async {
    setState(() {
      _isCountdownActive = true;
      _countdownValue = 3;
    });
    
    for (int i = 0; i < 3; i++) {
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        setState(() {
          _countdownValue--;
        });
      }
    }
    
    if (mounted) {
      setState(() {
        _isCountdownActive = false;
      });
      _capturePhoto();
    }
  }

  Future<void> _capturePhoto() async {
    if (_controller == null || !_controller!.value.isInitialized || _isCapturing) {
      return;
    }
    
    setState(() {
      _isCapturing = true;
      _errorMessage = '';
    });
    
    try {
      final image = await _controller!.takePicture();
      
      final directory = await getApplicationDocumentsDirectory();
      final fileName = '${widget.event.id}_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final savedImagePath = path.join(directory.path, fileName);
      
      // Copy the image file to our own location
      await File(image.path).copy(savedImagePath);
      
      setState(() {
        _capturedImagePath = savedImagePath;
        _isCapturing = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Error capturing photo: $e';
        _isCapturing = false;
      });
    }
  }

  Future<void> _uploadPhoto() async {
    if (_capturedImagePath == null) return;
    
    setState(() {
      _isUploading = true;
      _errorMessage = '';
    });
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      await apiService.uploadPhoto(widget.event.id, _capturedImagePath!);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo uploaded successfully')),
        );
        setState(() {
          _isUploading = false;
          // Go back to camera mode
          _capturedImagePath = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error uploading photo: $e';
        _isUploading = false;
      });
    }
  }
  
  void _retakePhoto() {
    setState(() {
      _capturedImagePath = null;
      _errorMessage = '';
    });
  }

  void _switchCamera() async {
    if (_cameras.length < 2) return;
    
    final currentCameraIndex = _cameras.indexOf(_controller!.description);
    final newCameraIndex = (currentCameraIndex + 1) % _cameras.length;
    
    await _controller?.dispose();
    await _setupCamera(_cameras[newCameraIndex]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: _errorMessage.isNotEmpty
          ? _buildErrorView()
          : _buildCameraView(),
    );
  }

  void _showForcePermissionDialog(bool isPermanentlyDenied) {
    showDialog(
      context: context,
      barrierDismissible: false, // User must tap a button to proceed
      builder: (BuildContext context) {
        return WillPopScope(
          // Prevent back button from dismissing the dialog
          onWillPop: () async => false,
          child: AlertDialog(
            backgroundColor: AppTheme.darkSurface,
            title: const Text('Camera Permission Required', 
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
            content: Text(
              isPermanentlyDenied
                  ? 'This app cannot function without camera access. Please open settings and grant camera permission.'
                  : 'This app cannot function without camera access. Please grant camera permission to continue.',
              style: const TextStyle(color: Colors.white),
            ),
            actions: <Widget>[
              TextButton(
                child: const Text('Exit App', style: TextStyle(color: Colors.grey)),
                onPressed: () {
                  // Navigate all the way back to exit the camera flow
                  Navigator.of(context).popUntil((route) => route.isFirst);
                },
              ),
              ElevatedButton(
                child: Text(isPermanentlyDenied ? 'Open Settings' : 'Grant Permission'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                ),
                onPressed: () {
                  Navigator.of(context).pop(); // Dismiss dialog
                  if (isPermanentlyDenied) {
                    openAppSettings();
                  } else {
                    _checkPermissionsAndInitializeCamera();
                  }
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32.0),
            child: Text(
              _errorMessage,
              style: const TextStyle(color: Colors.red, fontSize: 16),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              if (_errorMessage.contains('permanently denied')) {
                openAppSettings();
              } else {
                _checkPermissionsAndInitializeCamera();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryColor,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            ),
            child: Text(_errorMessage.contains('permanently denied')
                ? 'Open Settings'
                : 'Grant Permission'),
          ),
          const SizedBox(height: 16),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Go Back'),
          ),
        ],
      ),
    );
  }

  Widget _buildCameraView() {
    if (!_isInitialized) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }
    
    // If image has been captured, show preview screen
    if (_capturedImagePath != null) {
      return _buildCapturedImageView();
    }
    
    return Stack(
      fit: StackFit.expand,
      children: [
        // Camera preview
        CameraPreview(_controller!),
        
        // Countdown overlay
        if (_isCountdownActive)
          Container(
            color: Colors.black.withOpacity(0.5),
            child: Center(
              child: Text(
                '$_countdownValue',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 100,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        
        // Controls overlay
        SafeArea(
          child: Column(
            children: [
              // Top bar with close button
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    Text(
                      '${widget.experienceType.toUpperCase()} CAPTURE',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.camera_enhance, color: Colors.white),
                          onPressed: _isInitialized ? _openCameraSettings : null,
                          tooltip: 'Camera Settings',
                        ),
                        IconButton(
                          icon: const Icon(Icons.switch_camera, color: Colors.white),
                          onPressed: _cameras.length < 2 ? null : _switchCamera,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              const Spacer(),
              
              // Bottom controls
              Padding(
                padding: const EdgeInsets.all(24.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Capture button
                    GestureDetector(
                      onTap: _isCapturing ? null : _startCountdown,
                      child: Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: Colors.white,
                            width: 4,
                          ),
                        ),
                        child: _isCapturing
                            ? const CircularProgressIndicator(
                                valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
                              )
                            : Container(),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCapturedImageView() {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Display captured image
        Image.file(
          File(_capturedImagePath!),
          fit: BoxFit.contain,
        ),
        
        // Controls overlay
        SafeArea(
          child: Column(
            children: [
              // Top bar with close button
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Text(
                      'PREVIEW',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 48),
                  ],
                ),
              ),
              
              const Spacer(),
              
              // Bottom controls
              Padding(
                padding: const EdgeInsets.all(24.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // Retake button
                    ElevatedButton.icon(
                      onPressed: _isUploading ? null : _retakePhoto,
                      icon: const Icon(Icons.replay),
                      label: const Text('Retake'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.grey[800],
                        foregroundColor: Colors.white,
                      ),
                    ),
                    
                    // Save/Upload button
                    ElevatedButton.icon(
                      onPressed: _isUploading ? null : _uploadPhoto,
                      icon: _isUploading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                strokeWidth: 2,
                              ),
                            )
                          : const Icon(Icons.check),
                      label: Text(_isUploading ? 'Uploading...' : 'Save'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
