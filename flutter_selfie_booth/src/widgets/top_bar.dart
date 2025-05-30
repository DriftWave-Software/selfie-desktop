import 'package:flutter/material.dart';
import '../utils/app_theme.dart';
import '../services/auth_service.dart';
import 'package:provider/provider.dart';

class TopBar extends StatelessWidget {
  final String title;
  final VoidCallback? onBackPressed;
  final VoidCallback? onReloadPressed;
  final VoidCallback? onCameraConfigPressed;

  const TopBar({
    Key? key,
    this.title = 'SelfieBooth',
    this.onBackPressed,
    this.onReloadPressed,
    this.onCameraConfigPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.darkBackground,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          if (onBackPressed != null)
            IconButton(
              icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
              onPressed: onBackPressed,
            ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Spacer(),
          if (onReloadPressed != null)
            IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white),
              onPressed: onReloadPressed,
            ),
          if (onCameraConfigPressed != null)
            IconButton(
              icon: const Icon(Icons.camera_enhance, color: Colors.white),
              onPressed: onCameraConfigPressed,
              tooltip: 'Camera Settings',
            ),
          if (authService.isAuthenticated)
            PopupMenuButton<String>(
              icon: const Icon(Icons.account_circle, color: Colors.white),
              onSelected: (value) {
                if (value == 'logout') {
                  authService.logout();
                  Navigator.of(context).pushReplacementNamed('/login');
                }
              },
              itemBuilder: (BuildContext context) => [
                PopupMenuItem<String>(
                  value: 'account',
                  child: Row(
                    children: [
                      const Icon(Icons.person, color: AppTheme.primaryColor),
                      const SizedBox(width: 8),
                      Text('${authService.email}'),
                    ],
                  ),
                ),
                const PopupMenuDivider(),
                const PopupMenuItem<String>(
                  value: 'logout',
                  child: Row(
                    children: [
                      Icon(Icons.logout, color: Colors.red),
                      SizedBox(width: 8),
                      Text('Logout'),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}
