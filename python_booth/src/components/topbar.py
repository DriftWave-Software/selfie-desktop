import flet as ft
from typing import Callable, Optional

class TopBar(ft.Container):
    """Top bar component for SelfieBooth application"""
    
    def __init__(
        self, 
        user_name: Optional[str] = None,
        on_refresh: Optional[Callable] = None,
        on_logout: Optional[Callable] = None,
        on_back: Optional[Callable] = None,
        show_back: bool = False
    ):
        super().__init__()
        self.user_name = user_name
        self.on_refresh = on_refresh
        self.on_logout = on_logout
        self.on_back = on_back
        self.show_back = show_back
        
        self.build()
        
    def build(self):
        """Build the top bar UI"""
        elements = []
        
        # Add back button if needed
        if self.show_back and self.on_back:
            elements.append(
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Back",
                    on_click=self.on_back,
                    icon_color="#ffffff"
                )
            )
        
        # Logo text
        elements.append(
            ft.Text(
                "SelfieBooth",
                size=24,
                weight=ft.FontWeight.BOLD,
                color="#ffffff"
            )
        )
        
        # Spacer to push elements to the sides
        elements.append(ft.Container(expand=True))
        
        # User name if provided
        if self.user_name:
            elements.append(
                ft.Text(
                    f"Welcome, {self.user_name}",
                    size=16,
                    color="#ffffff"
                )
            )
        
        # Refresh button if handler provided
        if self.on_refresh:
            elements.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh",
                    on_click=self.on_refresh,
                    icon_color="#ffffff"
                )
            )
        
        # Logout button if handler provided
        if self.on_logout:
            elements.append(
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    on_click=self.on_logout,
                    icon_color="#ffffff"
                )
            )
        
        # Set the content
        self.content = ft.Row(
            controls=elements,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # Set container styling
        self.padding = ft.padding.only(left=20, right=20, top=10, bottom=10)
        self.bgcolor = "#1e1e1e"
        self.border_radius = ft.border_radius.only(bottom_left=10, bottom_right=10)
        self.height = 70
