import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  bool _isAuthenticated = false;
  String? _accessToken;
  String? _refreshToken;
  String? _email;
  late ApiService _apiService;
  
  bool get isAuthenticated => _isAuthenticated;
  String? get accessToken => _accessToken;
  String? get refreshToken => _refreshToken;
  String? get email => _email;
  
  void setApiService(ApiService apiService) {
    _apiService = apiService;
    _apiService.setAuthService(this);
  }
  
  final _storage = const FlutterSecureStorage();
  
  AuthService() {
    _checkAuthentication();
  }
  
  Future<void> _checkAuthentication() async {
    _accessToken = await _storage.read(key: 'access_token');
    _refreshToken = await _storage.read(key: 'refresh_token');
    _email = await _storage.read(key: 'email');
    _isAuthenticated = _accessToken != null && _refreshToken != null;
    
    if (_isAuthenticated && _apiService != null) {
      _apiService.updateTokens(_accessToken!, _refreshToken!);
    }
    
    notifyListeners();
  }
  
  Future<void> login(String accessToken, String refreshToken, String email) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
    await _storage.write(key: 'email', value: email);
    
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    _email = email;
    _isAuthenticated = true;
    
    _apiService.updateTokens(accessToken, refreshToken);
    
    notifyListeners();
  }
  
  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'email');
    
    _accessToken = null;
    _refreshToken = null;
    _email = null;
    _isAuthenticated = false;
    
    _apiService.clearTokens();
    
    notifyListeners();
  }
}
