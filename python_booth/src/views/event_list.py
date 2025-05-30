import flet as ft
from src.utils.api_client import APIClient
from src.components.topbar import TopBar
from datetime import datetime
from typing import List, Dict

class EventListView(ft.View):
    def __init__(self, page: ft.Page, api_client: APIClient):
        super().__init__()
        self.page = page
        self.api_client = api_client
        self.events = []
        self.current_tab = "upcoming"
        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.search_term = ""
        self.build()
    
    def build(self):
        """Build the event list view UI"""
        self.route = "/events"
        self.bgcolor = "#18181b"
        self.padding = 0
        self.scroll = ft.ScrollMode.AUTO
        
        # Top bar component
        self.top_bar = TopBar(
            user_name=self.api_client.user_data.get("name", "User") if self.api_client.user_data else None,
            on_refresh=self.refresh_events,
            on_logout=self.handle_logout
        )
        
        # Tab buttons for filtering events
        self.tab_row = ft.Row(
            controls=[
                self._create_tab_button("Upcoming", "upcoming"),
                self._create_tab_button("Today", "today"),
                self._create_tab_button("Past", "past"),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        
        # Search box
        self.search_field = ft.TextField(
            label="Find event",
            border_radius=10,
            bgcolor="#232323",
            color="#ffffff",
            border_color="#444444",
            focused_border_color="#f472b6",
            focused_bgcolor="#28282c",
            on_change=self.handle_search_change,
            prefix_icon=ft.Icons.SEARCH,
            width=350,
        )
        
        # Search container
        self.search_container = ft.Container(
            content=ft.Row(
                [self.search_field],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.only(left=40, right=40, top=20, bottom=20),
        )
        
        # Event data table
        self.event_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Event Name", color="#ffffff")),
                ft.DataColumn(ft.Text("Date", color="#ffffff")),
                ft.DataColumn(ft.Text("Package", color="#ffffff")),
                ft.DataColumn(ft.Text("Location", color="#ffffff")),
            ],
            rows=[],
            border_radius=10,
            bgcolor="#232323",
            heading_row_color="#18181b",
            heading_row_height=50,
            data_row_min_height=60,
            horizontal_lines=ft.border.BorderSide(1, "#28282c"),
            vertical_lines=ft.border.BorderSide(0, "transparent"),
        )
        
        # Table container with loading overlay
        self.loading_indicator = ft.ProgressRing(
            color="#f472b6",
            width=40,
            height=40,
            visible=False,
        )
        
        self.table_container = ft.Container(
            content=ft.Stack([
                self.event_table,
                ft.Container(
                    content=self.loading_indicator,
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ]),
            margin=ft.margin.only(left=40, right=40, top=10, bottom=20),
        )
        
        # Pagination controls
        self.pagination_text = ft.Text("Page 1 of 1", color="#ffffff")
        
        self.pagination_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: self.change_page(self.current_page - 1),
                    disabled=True,
                    icon_color="#ffffff",
                ),
                self.pagination_text,
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda e: self.change_page(self.current_page + 1),
                    disabled=True,
                    icon_color="#ffffff",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Add content to view
        self.controls = [
            ft.Column(
                controls=[
                    self.top_bar,
                    ft.Divider(height=1, color="#333333"),
                    ft.Container(
                        content=self.tab_row,
                        padding=ft.padding.only(left=40, right=40, top=20)
                    ),
                    self.search_container,
                    self.table_container,
                    self.pagination_row,
                ],
                spacing=0,
                expand=True,
            )
        ]
        
        # Update tab styling
        self._update_tab_styling()
        
    def did_mount(self, e=None):
        """Called when the view is mounted"""
        # Schedule loading events to happen after the view is mounted
        self.page.update()
        # Run the load_events method directly after the view is mounted
        self.load_events()
    
    def _create_tab_button(self, text: str, tab_id: str):
        """Create a tab button for event filtering"""
        return ft.TextButton(
            text=text,
            style=ft.ButtonStyle(
                color="#ffffff",
                overlay_color=ft.Colors.with_opacity(0.2, "#f472b6"),
            ),
            data=tab_id,  # Store tab ID in data attribute
            on_click=self.handle_tab_click,
        )
    
    def _update_tab_styling(self):
        """Update the styling of tab buttons based on the current tab"""
        for button in self.tab_row.controls:
            if button.data == self.current_tab:
                button.style = ft.ButtonStyle(
                    color="#ffffff",
                    overlay_color=ft.Colors.with_opacity(0.2, "#f472b6"),
                )
                button.content = ft.Container(
                    content=ft.Text(button.text),
                    border=ft.border.only(bottom=ft.border.BorderSide(2, "#f472b6")),
                    padding=ft.padding.only(bottom=5),
                )
            else:
                button.style = ft.ButtonStyle(
                    color="#ffffff",
                )
                button.content = ft.Text(button.text)
        
        # View will be updated by the parent
    
    def handle_tab_click(self, e):
        """Handle tab button click"""
        if e.control.data != self.current_tab:
            self.current_tab = e.control.data
            self.current_page = 1
            self._update_tab_styling()
            self.load_events()
    
    def handle_search_change(self, e):
        """Handle search input change"""
        self.search_term = e.control.value
        self.current_page = 1
        self.load_events()
    
    def change_page(self, page):
        """Change to a specific page"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.load_events()
    
    def refresh_events(self, e=None):
        """Refresh events data"""
        self.load_events()
    
    def load_events(self):
        """Load events from API with current filters"""
        # Show loading indicator
        self.loading_indicator.visible = True
        self.update()
        
        # Fetch events from API
        events, total_count = self.api_client.get_events_paginated(
            page=self.current_page,
            page_size=self.page_size,
            tab=self.current_tab,
            search=self.search_term
        )
        
        # Update state
        self.events = events
        self.total_pages = max(1, (total_count + self.page_size - 1) // self.page_size)
        
        # Update pagination
        self.pagination_text.value = f"Page {self.current_page} of {self.total_pages}"
        self.pagination_row.controls[0].disabled = self.current_page <= 1
        self.pagination_row.controls[2].disabled = self.current_page >= self.total_pages
        
        # Clear existing rows
        self.event_table.rows.clear()
        
        # Add event rows
        for event in self.events:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(event.get("name", ""), color="#ffffff")),
                    ft.DataCell(ft.Text(self._format_date(event.get("date", "")), color="#ffffff")),
                    ft.DataCell(ft.Text(event.get("package", {}).get("name", ""), color="#ffffff")),
                    ft.DataCell(ft.Text(event.get("location", ""), color="#ffffff")),
                ],
                on_select_changed=lambda e, ev=event: self.handle_event_click(ev),
            )
            self.event_table.rows.append(row)
        
        # Hide loading indicator
        self.loading_indicator.visible = False
        self.update()
    
    def _format_date(self, date_str):
        """Format API date string for display"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date_obj.strftime("%b %d, %Y")
        except Exception:
            return date_str
    
    def handle_event_click(self, event):
        """Handle event row click"""
        self.page.go(f"/event/{event['id']}")
    
    def handle_logout(self, e=None):
        """Handle logout button click"""
        self.api_client.logout()
        self.page.go("/")
