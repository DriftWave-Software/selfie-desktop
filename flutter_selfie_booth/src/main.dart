import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/login_screen.dart';
import 'screens/event_list_screen.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'utils/app_theme.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        ChangeNotifierProxyProvider<ApiService, AuthService>(
          create: (_) => AuthService(),
          update: (_, apiService, authService) {
            authService!.setApiService(apiService);
            return authService;
          },
        ),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    
    return MaterialApp(
      title: 'SelfieBooth',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.dark,
      debugShowCheckedModeBanner: false,
      home: authService.isAuthenticated ? const EventListScreen() : const LoginScreen(),
    );
  }
}
