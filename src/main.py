import flet as ft
import os
import sys


# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import APIClient
from views.login import LoginView
from views.event_list import EventListView
from views.event_details import EventDetailsView
from views.experience_select import ExperienceSelectView
from views.camera_test import CameraTestView

def main(page: ft.Page):
    # Configure the page
    page.title = "SelfieBooth"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#18181b"
    page.window_width = 900
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    
    # Initialize API client
    api_client = APIClient(base_url="http://127.0.0.1:8001/api")
    
    # Handle routing
    def route_change(e):
        # Get route and parameters
        route = page.route
        
        # Clear the page
        page.views.clear()
        
        # Handle different routes
        if route == "/" or route == "":
            # Login screen
            page.views.append(LoginView(page, api_client))
        
        elif route == "/events":
            # Event list screen
            page.views.append(EventListView(page, api_client))
        
        elif route.startswith("/event/"):
            # Event details screen
            event_id = route.split("/")[-1]
            page.views.append(EventDetailsView(page, api_client, event_id))
        
        elif route.startswith("/experience/"):
            # Experience selection screen
            event_id = route.split("/")[-1]
            page.views.append(ExperienceSelectView(page, api_client, event_id))
        
        elif route.startswith("/camera_test/"):
            # Camera test screen
            parts = route.split("/")
            event_id = parts[-1].split("?")[0] if "?" in parts[-1] else parts[-1]
            
            # Check if mode is specified
            mode = "photo"
            if "?" in route:
                params = route.split("?")[-1]
                if "mode=" in params:
                    mode = params.split("mode=")[-1].split("&")[0]
            
            page.views.append(CameraTestView(page, api_client, event_id, mode))
        
        # Update the page
        page.update()
    
    def view_pop(e):
        # Handle back button navigation
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    # Set up routing events
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start with the login route
    page.go("/")


# Check if assets folder exists for development vs packaged mode
if os.path.exists(os.path.join(os.path.dirname(__file__), "assets")):
    ft.app(target=main, assets_dir="assets")
else:
    ft.app(target=main)
