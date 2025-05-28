import flet as ft
import os
import sys
import platform
import traceback

# Add current directory to path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Also add the parent directory for mobile platforms where the structure might be different
parent_dir = os.path.dirname(project_dir)
sys.path.insert(0, parent_dir)

# For iOS, sometimes we need to add the specific app directory
is_ios = platform.system() == "Darwin" and (os.path.exists("/var/mobile") or "/CoreSimulator/" in os.getcwd())
if is_ios:
    print(f"Detected iOS environment: {'Simulator' if '/CoreSimulator/' in os.getcwd() else 'Device'}")
    for p in sys.path:
        print(f"Path: {p}")
    # iOS specific path handling
    ios_app_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, ios_app_path)
    print(f"iOS app path added: {ios_app_path}")

# Try different import patterns to handle various deployment scenarios
from utils.api_client import APIClient
from views.login import LoginView
from views.event_list import EventListView
from views.event_details import EventDetailsView
from views.experience_select import ExperienceSelectView
from views.camera_test import CameraTestView
print("Using direct imports without src package")
def main(page: ft.Page):
    # Setup error tracking
    def log_error(error_msg):
        try:
            print(f"ERROR: {error_msg}")
            # On iOS, create a visual error indicator
            if platform.system() == "Darwin" and os.path.exists("/var/mobile"):
                page.add(ft.Text(f"ERROR: {error_msg}", color="red", size=20))
                page.update()
        except Exception as e:
            print(f"Error in error logger: {e}")
    
    try:
        # Configure the page
        page.title = "SelfieBooth"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.bgcolor = "#18181b"
        page.window_width = 900
        page.window_height = 600
        
        # Debug info for iOS
        is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
        if is_ios:
            print("Running on iOS device")
            # Add debug UI to help diagnose navigation issues
            page.add(ft.Text("Starting SelfieBooth on iOS", color="white", size=14))
            page.update()
        
        # Initialize API client with platform-specific endpoints
        is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
        
        # Use a proper API endpoint based on platform
        if is_ios:
            # For iOS, use a remote API endpoint
            api_client = APIClient(base_url="https://selfieboothapiservice.azurewebsites.net/api")
            print(f"Using iOS API endpoint: {api_client.base_url}")
        else:
            # For desktop development
            api_client = APIClient(base_url="http://127.0.0.1:8001/api")
            print(f"Using local API endpoint: {api_client.base_url}")
    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}"
        log_error(error_msg)
        traceback.print_exc()
        page.add(ft.Text(error_msg, color="red", size=16))
        page.update()
        return
    # Handle routing
    def route_change(e):
        try:
            # Get route and parameters
            route = page.route
            print(f"Navigating to route: {route}")
            
            # Debug info for iOS
            is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
            if is_ios:
                print(f"iOS navigation to: {route}")
            
            # Clear the page
            page.views.clear()
            
            # Handle different routes
            if route == "/" or route == "":
                # Login screen
                print("Creating LoginView")
                page.views.append(LoginView(page, api_client))
                print("LoginView added")
            
            elif route == "/events":
                # Event list screen
                print("Creating EventListView")
                page.views.append(EventListView(page, api_client))
                print("EventListView added")
            
            elif route.startswith("/event/"):
                # Event details screen
                event_id = route.split("/")[-1]
                print(f"Creating EventDetailsView for event {event_id}")
                page.views.append(EventDetailsView(page, api_client, event_id))
                print("EventDetailsView added")
            
            elif route.startswith("/experience/"):
                # Experience selection screen
                event_id = route.split("/")[-1]
                print(f"Creating ExperienceSelectView for event {event_id}")
                page.views.append(ExperienceSelectView(page, api_client, event_id))
                print("ExperienceSelectView added")
        except Exception as e:
            error_msg = f"Navigation error for route '{page.route}': {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            # For iOS, provide visual feedback
            is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
            if is_ios:
                # Create a simple error view
                error_view = ft.View(
                    "/error",
                    [ft.AppBar(title=ft.Text("Navigation Error"))],
                    scroll=ft.ScrollMode.AUTO
                )
                
                # Add error details
                error_view.controls.append(ft.Text(f"Error: {str(e)}", color="red", size=16))
                error_view.controls.append(ft.Text(f"Route: {page.route}", size=14))
                error_view.controls.append(ft.Text(f"Trace: {traceback.format_exc()}", size=12))
                
                # Add a back button
                error_view.controls.append(ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/")))
                
                # Show the error view
                page.views.append(error_view)
            else:
                # Just show a simple error message
                page.views.append(LoginView(page, api_client))  # Fallback to login
        
        # After try-except block, update the page
        page.update()
    
    # Define route handler for camera test - separate to avoid indentation issues
    def handle_camera_test(route):
        try:
            # Camera test screen
            parts = route.split("/")
            event_id = parts[-1].split("?")[0] if "?" in parts[-1] else parts[-1]
            
            # Check if mode is specified
            mode = "photo"
            if "?" in route:
                params = route.split("?")[-1]
                if "mode=" in params:
                    mode = params.split("mode=")[-1].split("&")[0]
            
            print(f"Creating CameraTestView for event {event_id} in mode {mode}")
            return CameraTestView(page, api_client, event_id, mode)
        except Exception as e:
            print(f"Error creating CameraTestView: {e}")
            traceback.print_exc()
            return None
    
    # Modify route_change to use the handler
    def route_change(e):
        try:
            # Get route and parameters
            route = page.route
            print(f"Navigating to route: {route}")
            
            # Debug info for iOS
            is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
            if is_ios:
                print(f"iOS navigation to: {route}")
            
            # Clear the page
            page.views.clear()
            
            # Handle different routes
            if route == "/" or route == "":
                # Login screen
                print("Creating LoginView")
                page.views.append(LoginView(page, api_client))
                print("LoginView added")
            
            elif route == "/events":
                # Event list screen
                print("Creating EventListView")
                page.views.append(EventListView(page, api_client))
                print("EventListView added")
            
            elif route.startswith("/event/"):
                # Event details screen
                event_id = route.split("/")[-1]
                print(f"Creating EventDetailsView for event {event_id}")
                page.views.append(EventDetailsView(page, api_client, event_id))
                print("EventDetailsView added")
            
            elif route.startswith("/experience/"):
                # Experience selection screen
                event_id = route.split("/")[-1]
                print(f"Creating ExperienceSelectView for event {event_id}")
                page.views.append(ExperienceSelectView(page, api_client, event_id))
                print("ExperienceSelectView added")
                
            elif route.startswith("/camera_test/"):
                # Use the separate handler function
                view = handle_camera_test(route)
                if view:
                    page.views.append(view)
                    print("CameraTestView added")
                else:
                    # Fallback if handler failed
                    page.views.append(LoginView(page, api_client))
                    print("Fallback to LoginView due to camera error")
        except Exception as e:
            error_msg = f"Navigation error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            # For iOS, provide visual feedback
            is_ios = platform.system() == "Darwin" and os.path.exists("/var/mobile")
            if is_ios:
                # Create a simple error view
                error_view = ft.View(
                    "/error",
                    [ft.AppBar(title=ft.Text("Navigation Error"))],
                    scroll=ft.ScrollMode.AUTO
                )
                
                # Add error details
                error_view.controls.append(ft.Text(f"Error: {str(e)}", color="red", size=16))
                error_view.controls.append(ft.Text(f"Route: {page.route}", size=14))
                error_view.controls.append(ft.Text(f"Trace: {traceback.format_exc()}", size=12))
                
                # Add a back button
                error_view.controls.append(ft.ElevatedButton("Go Back", on_click=lambda _: page.go("/")))
                
                # Show the error view
                page.views.append(error_view)
            else:
                # Just show a simple error message
                page.views.append(LoginView(page, api_client))  # Fallback to login
        
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
    
    # Start directly with camera test page for testing
    print("Opening camera test page directly")
    # Using event_id=1 as a default placeholder for testing
    page.go("/camera_test/1?mode=photo")


# Check if assets folder exists for development vs packaged mode
if os.path.exists(os.path.join(os.path.dirname(__file__), "assets")):
    ft.app(target=main, assets_dir="assets")
else:
    ft.app(target=main)
