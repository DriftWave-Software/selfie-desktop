import flet as ft
from src.utils.api_client import APIClient
from src.components.topbar import TopBar
from datetime import datetime

class EventDetailsView(ft.View):
    def __init__(self, page: ft.Page, api_client: APIClient, event_id: str):
        super().__init__()
        self.page = page
        self.api_client = api_client
        self.event_id = int(event_id)
        self.event = None
        self.build()
    
    def build(self):
        """Build the event details view UI"""
        self.route = f"/event/{self.event_id}"
        self.bgcolor = "#18181b"
        self.padding = 0
        
        # Top bar with back button
        self.top_bar = TopBar(
            user_name=self.api_client.user_data.get("name", "User") if self.api_client.user_data else None,
            on_back=lambda e: self.page.go("/events"),
            show_back=True
        )
        
        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            color="#f472b6",
            width=40,
            height=40,
        )
        
        # Event details (will be populated after loading)
        self.event_name = ft.Text(
            value="Loading...",
            size=32,
            weight=ft.FontWeight.BOLD,
            color="#ffffff",
        )
        
        self.event_date = ft.Text(
            value="",
            size=18,
            color="#aaaaaa",
        )
        
        self.event_location = ft.Text(
            value="",
            size=18,
            color="#aaaaaa",
        )
        
        self.event_description = ft.Text(
            value="",
            size=16,
            color="#ffffff",
        )
        
        # Start event button
        self.start_button = ft.ElevatedButton(
            "Start Event",
            icon=ft.Icons.PLAY_CIRCLE,
            on_click=self.start_event,
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#007bff",
                padding=ft.padding.all(16),
            ),
            width=200,
            height=50,
            disabled=True,
        )
        
        # Event details container
        self.details_container = ft.Container(
            content=ft.Column(
                [
                    self.event_name,
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, color="#aaaaaa"),
                        self.event_date,
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, color="#aaaaaa"),
                        self.event_location,
                    ]),
                    ft.Divider(height=20, color="transparent"),
                    self.event_description,
                    ft.Divider(height=30, color="transparent"),
                    self.start_button,
                ],
                spacing=10,
            ),
            padding=ft.padding.all(20),
            bgcolor="#232323",
            border_radius=10,
            width=700,
            visible=False,
        )
        
        # Loading container
        self.loading_container = ft.Container(
            content=ft.Column(
                [
                    self.loading_indicator,
                    ft.Text("Loading event details...", color="#ffffff"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=ft.padding.all(20),
            bgcolor="#232323",
            border_radius=10,
            width=700,
            height=300,
        )
        
        # Add content to view
        self.controls = [
            ft.Column(
                controls=[
                    self.top_bar,
                    ft.Container(
                        content=ft.Column(
                            [
                                self.loading_container,
                                self.details_container,
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.all(40),
                    ),
                ],
                spacing=0,
                expand=True,
            )
        ]
        
        # Event will be loaded when view is mounted
    
    def did_mount(self, e=None):
        """Called when the view is mounted"""
        # Schedule loading event to happen after the view is mounted
        self.page.update()
        # Load event details
        self.load_event()
    
    def load_event(self):
        """Load event details from API"""
        # Fetch event details
        self.event = self.api_client.get_event(self.event_id)
        
        if self.event:
            # Update UI with event details
            self.event_name.value = self.event.get("name", "Unknown Event")
            self.event_date.value = self._format_date(self.event.get("date", ""))
            self.event_location.value = self.event.get("location", "")
            self.event_description.value = self.event.get("description", "No description available")
            
            # Hide loading, show details
            self.loading_container.visible = False
            self.details_container.visible = True
            self.start_button.disabled = False
        else:
            # Show error message
            self.loading_container.content = ft.Column(
                [
                    ft.Icon(ft.icons.ERROR, color="#ff4444", size=50),
                    ft.Text("Unable to load event details", color="#ffffff", size=18),
                    ft.ElevatedButton(
                        "Go Back",
                        on_click=lambda e: self.page.go("/events"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        
        self.update()
    
    def _format_date(self, date_str):
        """Format API date string for display"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date_obj.strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            return date_str
    
    def start_event(self, e):
        """Handle start event button click"""
        self.page.go(f"/experience/{self.event_id}")
