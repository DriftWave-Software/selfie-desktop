import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/event.dart';
import '../utils/constants.dart';
import '../services/auth_service.dart';

class ApiService {
  final String baseUrl = ApiConstants.baseUrl;
  final Map<String, String> headers = {
    'Content-Type': 'application/json',
  };
  String? _accessToken;
  String? _refreshToken;
  AuthService? _authService;
  
  // Set the auth service reference
  void setAuthService(AuthService authService) {
    _authService = authService;
  }

  // Get headers with current access token
  Map<String, String> _getHeaders() {
    final Map<String, String> requestHeaders = Map.from(headers);
    if (_accessToken != null) {
      requestHeaders['Authorization'] = 'Bearer $_accessToken';
    }
    return requestHeaders;
  }

  // Update tokens
  void updateTokens(String accessToken, String refreshToken) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
  }

  // Clear tokens
  void clearTokens() {
    _accessToken = null;
    _refreshToken = null;
  }

  // Login with JWT
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/jwt/create/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _accessToken = data['access'];
      _refreshToken = data['refresh'];
      return data;
    } else {
      throw Exception('Failed to login: ${response.body}');
    }
  }

  // Get Events list with pagination and filters
  Future<Map<String, dynamic>> getEvents({
    String? search,
    String tab = 'upcoming',
    int page = 1,
    int pageSize = 10,
    String? fromDate,
    String? toDate,
  }) async {
    final queryParams = {
      'page': page.toString(),
      'page_size': pageSize.toString(),
      'tab': tab,
      if (search != null && search.isNotEmpty) 'search': search,
      if (fromDate != null) 'from_date': fromDate,
      if (toDate != null) 'to_date': toDate,
    };

    final uri = Uri.parse('$baseUrl/api/events/').replace(queryParameters: queryParams);
    final response = await _authenticatedRequest(() => http.get(uri, headers: _getHeaders()));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'events': (data['results'] as List).map((e) => Event.fromJson(e)).toList(),
        'total': data['count'],
        'next': data['next'],
        'previous': data['previous'],
      };
    } else {
      throw Exception('Failed to load events: ${response.body}');
    }
  }

  // Get Event details
  Future<Event> getEventDetails(int eventId) async {
    final response = await _authenticatedRequest(() => http.get(
      Uri.parse('$baseUrl/api/events/$eventId/'),
      headers: _getHeaders(),
    ));

    if (response.statusCode == 200) {
      return Event.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load event details: ${response.body}');
    }
  }

  // Upload photo
  Future<Map<String, dynamic>> uploadPhoto(int eventId, String filePath) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/events/$eventId/photos/'),
    );

    // Add auth header
    final requestHeaders = _getHeaders();
    requestHeaders.forEach((key, value) {
      request.headers[key] = value;
    });

    // Add file
    request.files.add(await http.MultipartFile.fromPath('photo', filePath));

    var response = await request.send();
    var responseData = await response.stream.bytesToString();

    if (response.statusCode == 201) {
      return jsonDecode(responseData);
    } else {
      throw Exception('Failed to upload photo: $responseData');
    }
  }

  // Refresh access token
  Future<bool> _refreshAccessToken() async {
    if (_refreshToken == null) return false;
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/jwt/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': _refreshToken}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _accessToken = data['access'];
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  
  // Helper for authenticated requests with token refresh
  Future<http.Response> _authenticatedRequest(Future<http.Response> Function() request) async {
    // First attempt with current token
    var response = await request();
    
    // If unauthorized, try to refresh token and retry
    if (response.statusCode == 401) {
      final refreshSuccess = await _refreshAccessToken();
      
      if (refreshSuccess) {
        // Retry with new token
        response = await request();
      } else {
        // If refresh failed, log out user
        if (_authService != null) {
          await _authService!.logout();
        }
      }
    }
    
    return response;
  }
}
