import 'dart:io';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:photofilters/photofilters.dart';
import 'package:image/image.dart' as img;
import 'package:flutter/foundation.dart' show debugPrint;

class CameraUtils {
  /// Pick an image from gallery
  static Future<File?> pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    
    if (pickedFile != null) {
      return File(pickedFile.path);
    }
    return null;
  }

  /// Apply filter to an image
  static Future<String?> applyFilter({
    required String imagePath,
    required Filter filter,
  }) async {
    try {
      // Read the image
      final imageBytes = await File(imagePath).readAsBytes();
      img.Image? image = img.decodeImage(imageBytes);
      
      if (image == null) return null;
      
      // Apply filter - properly provide all required parameters
      filter.apply(Uint8List.fromList(img.encodeJpg(image)), image.width, image.height);
      
      // Save to temporary file
      final directory = await getTemporaryDirectory();
      final filename = path.basename(imagePath);
      final filteredPath = path.join(directory.path, 'filtered_$filename');
      
      final filteredFile = File(filteredPath);
      await filteredFile.writeAsBytes(img.encodeJpg(image));
      
      return filteredPath;
    } catch (e) {
      debugPrint('Error applying filter: $e');
      return null;
    }
  }

  /// Save image to gallery
  static Future<bool> saveToGallery(String imagePath) async {
    try {
      await File(imagePath).copy(
        '${(await getApplicationDocumentsDirectory()).path}/${DateTime.now().millisecondsSinceEpoch}.jpg'
      );
      return true;
    } catch (e) {
      debugPrint('Error saving to gallery: $e');
      return false;
    }
  }
}
