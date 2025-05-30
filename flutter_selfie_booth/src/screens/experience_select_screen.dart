import 'package:flutter/material.dart';
import '../models/event.dart';
import '../widgets/top_bar.dart';
import '../utils/app_theme.dart';
import 'camera_screen.dart';

class ExperienceSelectScreen extends StatelessWidget {
  final Event event;

  const ExperienceSelectScreen({
    Key? key,
    required this.event,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF221533), Color(0xFF5C267C)],
          ),
        ),
        child: Column(
          children: [
            TopBar(
              title: 'Choose Your Experience',
              onBackPressed: () => Navigator.pop(context),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    _buildGalleryButton(context),
                    const SizedBox(height: 40),
                    const Text(
                      'Choose Your Experience',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 40),
                    if (event.coverImage != null) ...[
                      _buildEventImage(event.coverImage!),
                      const SizedBox(height: 40),
                    ],
                    Expanded(
                      child: _buildExperienceOptions(context),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGalleryButton(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: ElevatedButton.icon(
        onPressed: () {
          // Gallery functionality will be implemented later
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Gallery will be implemented later')),
          );
        },
        icon: const Icon(Icons.photo_library),
        label: const Text('Gallery'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white.withOpacity(0.2),
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildEventImage(String imageUrl) {
    return Container(
      height: 180,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: imageUrl.startsWith('http')
          ? Image.network(
              imageUrl,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return const Center(
                  child: Icon(Icons.broken_image, color: Colors.white70, size: 50),
                );
              },
            )
          : Image.asset(
              'assets/images/placeholder.jpg',
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return const Center(
                  child: Icon(Icons.broken_image, color: Colors.white70, size: 50),
                );
              },
            ),
    );
  }

  Widget _buildExperienceOptions(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      childAspectRatio: 1.2,
      crossAxisSpacing: 20,
      mainAxisSpacing: 20,
      children: [
        _buildExperienceCard(
          context,
          'Photo',
          Icons.camera_alt,
          () => _navigateToCameraScreen(context, 'photo'),
        ),
        _buildExperienceCard(
          context,
          'Boomerang',
          Icons.refresh,
          () => _navigateToCameraScreen(context, 'boomerang'),
        ),
        _buildExperienceCard(
          context,
          'GIF',
          Icons.gif,
          () => _navigateToCameraScreen(context, 'gif'),
        ),
        _buildExperienceCard(
          context,
          'Video',
          Icons.videocam,
          () => _navigateToCameraScreen(context, 'video'),
        ),
      ],
    );
  }

  Widget _buildExperienceCard(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onPressed,
  ) {
    return Card(
      color: Colors.white.withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 48,
              color: Colors.white,
            ),
            const SizedBox(height: 12),
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
      ),
    );
  }

  void _navigateToCameraScreen(BuildContext context, String experienceType) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CameraScreen(
          event: event,
          experienceType: experienceType,
        ),
      ),
    );
  }
}
