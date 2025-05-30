import httpx
from typing import Optional, Dict, List, Any, Tuple
import os

class APIClient:
    """API Client for SelfieBooth application"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_data: Optional[Dict] = None
        self.client = httpx.Client(timeout=30.0)
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user and store tokens"""
        try:
            response = self.client.post(
                f"{self.base_url}/auth/jwt/create/",
                json={'email': username, 'password': password}
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                self._fetch_user_info()
                return True
            return False
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def _fetch_user_info(self) -> bool:
        """Fetch user information after login"""
        try:
            response = self._request_with_refresh('GET', f"{self.base_url}/auth/users/me/")
            if response.status_code == 200:
                self.user_data = response.json()
                return True
            return False
        except Exception:
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
        try:
            response = self.client.post(
                f"{self.base_url}/auth/jwt/refresh/",
                json={'refresh': self.refresh_token}
            )
            if response.status_code == 200:
                self.access_token = response.json().get('access')
                return True
            return False
        except Exception:
            return False
    
    def _request_with_refresh(self, method, url, **kwargs):
        """Make a request and refresh token if needed"""
        kwargs.setdefault('headers', {}).update(self._get_headers())
        response = self.client.request(method, url, **kwargs)
        
        if response.status_code == 401:
            # Try to refresh the token and retry the request
            if self._refresh_access_token():
                kwargs['headers'].update(self._get_headers())
                response = self.client.request(method, url, **kwargs)
        
        return response
    
    def logout(self):
        """Clear authentication data"""
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
    
    def get_events(self) -> List[Dict]:
        """Get all events"""
        response = self._request_with_refresh('GET', f"{self.base_url}/events/")
        return response.json() if response.status_code == 200 else []
    
    def get_events_paginated(self, page=1, page_size=10, tab=None, search=None) -> Tuple[List[Dict], int]:
        """Get paginated events with filters"""
        params = {'page': page, 'page_size': page_size}
        
        if tab:
            if tab == 'upcoming':
                params['date_filter'] = 'gt'
            elif tab == 'today':
                params['date_filter'] = 'exact'
            elif tab == 'past':
                params['date_filter'] = 'lt'
        
        if search:
            params['search'] = search
        
        response = self._request_with_refresh('GET', f"{self.base_url}/events/", params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', []), data.get('count', 0)
        return [], 0
    
    def get_event(self, event_id: int) -> Optional[Dict]:
        """Get details for a specific event"""
        response = self._request_with_refresh('GET', f"{self.base_url}/events/{event_id}/")
        return response.json() if response.status_code == 200 else None
    
    def verify_event_pin(self, event_id: int, pin: str) -> bool:
        """Verify an event's PIN code"""
        response = self._request_with_refresh(
            'POST',
            f"{self.base_url}/events/{event_id}/verify_pin/",
            json={'pin': pin}
        )
        return response.status_code == 200
    
    def get_templates(self, event_id: Optional[int] = None) -> List[Dict]:
        """Get templates, optionally filtered by event"""
        url = f"{self.base_url}/templates/"
        if event_id:
            url = f"{self.base_url}/events/{event_id}/templates/"
        
        response = self._request_with_refresh('GET', url)
        return response.json() if response.status_code == 200 else []
    
    def upload_media(self, event_id: int, file_path: str, media_type: str = 'photo',
                     template_id: Optional[int] = None) -> bool:
        """Upload media file to the server"""
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'media_type': media_type}
                if template_id:
                    data['template_id'] = template_id

                response = self._request_with_refresh(
                    'POST',
                    f"{self.base_url}/events/{event_id}/media/",
                    files=files,
                    data=data
                )
                return response.status_code in (200, 201)
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return False
