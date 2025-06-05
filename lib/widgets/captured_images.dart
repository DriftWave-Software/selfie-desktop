import 'dart:io';
import 'package:flutter/material.dart';
import '../models/selfie_image.dart';

class CapturedImages extends StatelessWidget {
  final List<SelfieImage> images;
  final Function(SelfieImage) onImageTap;

  const CapturedImages({
    super.key,
    required this.images,
    required this.onImageTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      color: Colors.black,
      child: images.isEmpty
          ? const Center(
              child: Text(
                'No images captured yet',
                style: TextStyle(color: Colors.white60),
              ),
            )
          : ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: images.length,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              itemBuilder: (context, index) {
                final image = images[index];
                return _buildImageThumbnail(image);
              },
            ),
    );
  }

  Widget _buildImageThumbnail(SelfieImage image) {
    return GestureDetector(
      onTap: () => onImageTap(image),
      child: Container(
        width: 80,
        height: 80,
        margin: const EdgeInsets.only(right: 8),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.white, width: 2),
          borderRadius: BorderRadius.circular(8),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: Image.file(
            File(image.path),
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }
}
