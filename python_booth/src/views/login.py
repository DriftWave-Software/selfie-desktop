import flet as ft
from src.utils.api_client import APIClient

class LoginView(ft.View):
    def __init__(self, page: ft.Page, api_client: APIClient):
        super().__init__()
        self.page = page
        self.api_client = api_client
        self.build()

    def build(self):
        """Build the login view UI"""
        self.route = "/"
        self.bgcolor = "#18181b"
        self.padding = 0
        
        # Logo placeholder (we'll replace with actual logo when images are set up)
        self.logo = ft.Icon(
            name=ft.Icons.PHOTO_CAMERA,
            size=50,
            color="#ffffff",
        )
        
        # Form fields
        self.email_field = ft.TextField(
            label="Email",
            border_radius=10,
            text_size=16,
            color="#ffffff",
            bgcolor="#23232a",
            border_color="#444444",
            focused_border_color="#7c3aed",
            focused_bgcolor="#23233a",
            width=350,
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            text_size=16,
            color="#ffffff",
            bgcolor="#23232a",
            border_color="#444444",
            focused_border_color="#7c3aed",
            focused_bgcolor="#23233a",
            width=350,
            on_submit=self.handle_login,
        )
        
        # Error message
        self.error_banner = ft.Container(
            content=ft.Text(
                "",
                color="#b30000",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor="#ffeaea",
            border_radius=12,
            padding=ft.padding.all(16),
            visible=False,
            width=350,
        )
        
        # Login button
        self.login_button = ft.ElevatedButton(
            text="Login",
            style=ft.ButtonStyle(
                color="#ffffff",
                bgcolor="#007bff",
                padding=ft.padding.all(10),
            ),
            width=200,
            height=48,
            on_click=self.handle_login,
        )
        
        # Form container
        form_container = ft.Container(
            content=ft.Column(
                [
                    self.logo,
                    ft.Divider(height=20, color="transparent"),
                    self.email_field,
                    ft.Divider(height=10, color="transparent"),
                    self.password_field,
                    ft.Divider(height=10, color="transparent"),
                    self.error_banner,
                    ft.Divider(height=10, color="transparent"),
                    self.login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            width=400,
            bgcolor=ft.Colors.with_opacity(0.8, "#000000"),
            border_radius=10,
            padding=ft.padding.all(30),
        )
        
        # Main container with background
        main_container = ft.Container(
            content=form_container,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.BLACK,
        )
        
        # Note: In newer Flet versions, we need to use this approach for background images
        # We'll add a background image when we have the actual image file
        
        # Add controls to view
        self.controls = [main_container]
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_banner.content.value = message
        self.error_banner.visible = True
        self.update()
    
    def clear_error(self):
        """Clear error message"""
        self.error_banner.content.value = ""
        self.error_banner.visible = False
        self.update()
    
    def handle_login(self, e=None):
        """Handle login button click"""
        # Get form values
        email = self.email_field.value
        password = self.password_field.value
        
        # Validate inputs
        if not email or not password:
            self.show_error("Please enter both email and password")
            return
        
        # Clear previous error
        self.clear_error()
        
        # Update UI to show loading state
        self.login_button.text = "Logging in..."
        self.login_button.disabled = True
        self.update()
        
        # Attempt login
        # success = self.api_client.login(email, password)
        success = True
        if success:
            # Navigate to events page
            # self.page.go("/events")
            self.page.views.append("/camera_test/1?mode=photo")
        else:
            # Show error
            self.show_error("Invalid email or password")
            self.password_field.value = ""
            self.login_button.text = "Login"
            self.login_button.disabled = False
            self.update()
