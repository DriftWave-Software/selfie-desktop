import flet as ft
from src.utils.api_client import APIClient
from src.components.topbar import TopBar

class ExperienceSelectView(ft.View):
    def __init__(self, page: ft.Page, api_client: APIClient, event_id: str):
        super().__init__()
        self.page = page
        self.api_client = api_client
        self.event_id = int(event_id)
        self.event = None
        self.build()
    
    def build(self):
        """Build the experience selection view UI"""
        self.route = f"/experience/{self.event_id}"
        self.bgcolor = "#18181b"
        self.padding = 0
        
        # Top bar with back button
        self.top_bar = TopBar(
            user_name=self.api_client.user_data.get("name", "User") if self.api_client.user_data else None,
            on_back=lambda e: self.page.go(f"/event/{self.event_id}"),
            show_back=True
        )
        
        # Experience title
        self.title = ft.Text(
            "Choose Your Experience",
            size=32,
            weight=ft.FontWeight.BOLD,
            color="#ffffff",
            text_align=ft.TextAlign.CENTER,
        )
        
        # Loading the event details
        self.event = self.api_client.get_event(self.event_id)
        
        # Event name subtitle
        self.event_name = ft.Text(
            self.event.get("name", "Event") if self.event else "Event",
            size=20,
            color="#aaaaaa",
            text_align=ft.TextAlign.CENTER,
        )
        
        # Experience cards
        card_width = 250
        card_height = 200
        
        # Photo experience card
        self.photo_card = self._create_experience_card(
            "Photo",
            ft.Icons.CAMERA_ALT,
            "Take a photo with our professional camera setup",
            "#007bff",
            lambda e: self.page.go(f"/camera_test/{self.event_id}?mode=photo"),
            card_width,
            card_height
        )
        
        # GIF experience card
        self.gif_card = self._create_experience_card(
            "GIF",
            ft.Icons.GIF,
            "Create an animated GIF with multiple photos",
            "#f472b6",
            lambda e: self.page.go(f"/camera_test/{self.event_id}?mode=gif"),
            card_width,
            card_height
        )
        
        # Video experience card
        self.video_card = self._create_experience_card(
            "Video",
            ft.Icons.VIDEOCAM,
            "Record a short video message",
            "#10b981",
            lambda e: self.page.go(f"/camera_test/{self.event_id}?mode=video"),
            card_width,
            card_height
        )
        
        # Boomerang experience card
        self.boomerang_card = self._create_experience_card(
            "Boomerang",
            ft.Icons.LOOP,
            "Create a fun boomerang loop",
            "#f59e0b",
            lambda e: self.page.go(f"/camera_test/{self.event_id}?mode=boomerang"),
            card_width,
            card_height
        )
        
        # Card grid
        self.experience_grid = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.photo_card, self.gif_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    ft.Row(
                        [self.video_card, self.boomerang_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=ft.padding.only(top=30, bottom=40),
        )
        
        # Add content to view
        self.controls = [
            ft.Column(
                controls=[
                    self.top_bar,
                    ft.Container(
                        content=ft.Column(
                            [
                                self.title,
                                self.event_name,
                                self.experience_grid,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(40),
                    ),
                ],
                spacing=0,
                expand=True,
            )
        ]
    
    def _create_experience_card(self, title, icon, description, color, on_click, width, height):
        """Create an experience option card"""
        # Create the card content
        card_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=50, color="#ffffff"),
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="#ffffff"),
                    ft.Text(
                        description, 
                        size=14, 
                        color="#ffffff", 
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            width=width,
            height=height,
            bgcolor=color,
            border_radius=10,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
        )
        
        # Wrap in a GestureDetector for click handling
        return ft.GestureDetector(
            content=ft.Card(
                content=card_content,
                elevation=5,
            ),
            on_tap=on_click,
        )
