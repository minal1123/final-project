# Main Application window routing and navigation framework
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color
from frontend.services.api_client import APIClient
from frontend.components.notifications import NotificationBanner

# Page Imports
from frontend.pages.dashboard_page import DashboardPage
from frontend.pages.testing_page import TestingPage
from frontend.pages.analytics_page import AnalyticsPage
from frontend.pages.history_page import HistoryPage
from frontend.pages.settings_page import SettingsPage

class APILoadTesterApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Window setup
        self.title("API Load Testing Dashboard")
        self.geometry("1100x700")
        self.minsize(950, 600)
        
        # Default application global state variables
        self.api_client = APIClient()
        self.settings = {
            "timeout": 10.0,
            "concurrency": 10
        }
        
        # Active result memory shared between Testing and Analytics pages
        self.active_test_result = None

        # Base Grid Layout configuration (2 columns: Sidebar, Content Area)
        self.grid_columnconfigure(0, weight=1) # Sidebar
        self.grid_columnconfigure(1, weight=5) # Content Page
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # NAVIGATION SIDEBAR
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=get_color("sidebar_bg"), corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Spacer

        # Logo / Title Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="⚡ LOADTEST.IO",
            font=get_font(18, "bold"), text_color=get_color("accent")
        )
        self.logo_label.pack(anchor="w", padx=20, pady=(30, 20))

        # Nav Buttons list
        self.nav_buttons = {}
        self._add_nav_button("dashboard", "🏠  Home Dashboard", self._nav_to_dashboard)
        self._add_nav_button("testing", "🚀  API Testing", lambda: self.show_page("testing"))
        self._add_nav_button("analytics", "📊  Performance Analytics", lambda: self.show_page("analytics"))
        self._add_nav_button("history", "📂  Test History", lambda: self.show_page("history"))
        self._add_nav_button("settings", "⚙️  Settings", lambda: self.show_page("settings"))

        # Footer Label
        footer_label = ctk.CTkLabel(
            self.sidebar_frame, text="SE Viva v1.0",
            font=get_font(10), text_color=get_color("text_muted")
        )
        footer_label.pack(side="bottom", pady=20)

        # ==========================================
        # CONTENT PAGE ROUTER WINDOW
        # ==========================================
        self.content_container = ctk.CTkFrame(self, fg_color=get_color("bg_primary"), corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Reusable Notifications banner at top of content area
        self.notification = NotificationBanner(self.content_container)
        self.notification.place(relx=0.0, rely=0.0, relwidth=1.0, anchor="nw")

        # Loading animation overlay
        self.loading_overlay = ctk.CTkFrame(self.content_container, fg_color=("#c1c1c1", "#0a0a0c"))
        self.loading_lbl = ctk.CTkLabel(
            self.loading_overlay, text="Fetching database history, please wait...",
            font=get_font(14, "bold"), text_color="#ffffff",
            fg_color=get_color("bg_secondary"), corner_radius=8, padx=20, pady=10
        )
        self.loading_lbl.pack(expand=True)

        # Initialize all pages in memory
        self.pages = {}
        for PageClass in [DashboardPage, TestingPage, AnalyticsPage, HistoryPage, SettingsPage]:
            page_name = PageClass.__name__.lower().replace("page", "")
            page = PageClass(parent=self.content_container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Start with dashboard
        self.show_page("dashboard")

    def _add_nav_button(self, name: str, text: str, command):
        """Helper to create unified style nav buttons in the sidebar."""
        btn = ctk.CTkButton(
            self.sidebar_frame, text=text, anchor="w",
            font=get_font(12, "bold"),
            fg_color="transparent",
            text_color=get_color("text_secondary"),
            hover_color=get_color("bg_tertiary"),
            height=38, corner_radius=6,
            command=command
        )
        btn.pack(fill="x", padx=12, pady=3)
        self.nav_buttons[name] = btn

    def show_page(self, page_name: str):
        """Lifts target frame to the front and adjusts sidebar highlights."""
        page = self.pages.get(page_name)
        if not page:
            return
            
        page.tkraise()

        # Update sidebar selections
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(
                    fg_color=get_color("accent"),
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=get_color("text_secondary")
                )

        # Trigger page-specific refresh operations
        if page_name == "dashboard":
            page.refresh_dashboard()
        elif page_name == "history":
            page.refresh_history()

    def _nav_to_dashboard(self):
        """Standard routing wrapper for sidebar dashboard link."""
        self.show_page("dashboard")

    def show_notification(self, message: str, level: str = "info"):
        """Displays toast alert at top of window."""
        self.notification.show(message, level)

    def show_loading_animation(self):
        """Reveals block overlay."""
        self.loading_overlay.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.update()

    def hide_loading_animation(self):
        """Hides block overlay."""
        self.loading_overlay.place_forget()
