# Home Dashboard Page GUI component
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color
from frontend.components.cards import MetricCard

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Header Title & Welcome Banner
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=(30, 10))

        welcome_lbl = ctk.CTkLabel(
            title_frame, text="API Load Testing Dashboard",
            font=get_font(24, "bold"),
            text_color=get_color("text_primary")
        )
        welcome_lbl.pack(side="left")

        # Health status badge
        self.health_badge = ctk.CTkLabel(
            title_frame, text="● BACKEND ACTIVE",
            font=get_font(10, "bold"),
            text_color="#10b981", # Active green
            fg_color=get_color("bg_secondary"),
            padx=10, pady=4,
            corner_radius=12
        )
        self.health_badge.pack(side="right", pady=5)

        subtitle = ctk.CTkLabel(
            self, text="Real-time Client-Server benchmarking platform for software construction evaluation.",
            font=get_font(12, "normal"),
            text_color=get_color("text_secondary")
        )
        subtitle.pack(anchor="w", padx=30, pady=(0, 20))

        # Main scroll container
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # --- Welcome Jumbotron ---
        jumbo = ctk.CTkFrame(container, fg_color=get_color("bg_secondary"), corner_radius=10)
        jumbo.pack(fill="x", pady=(0, 15))
        
        jumbo_title = ctk.CTkLabel(
            jumbo, text="Welcome back, Developer!",
            font=get_font(18, "bold"), text_color=get_color("accent")
        )
        jumbo_title.pack(anchor="w", padx=20, pady=(15, 5))
        
        jumbo_text = (
            "Analyze and bench target APIs. Deploy concurrent load-generating threads,\n"
            "monitor system health, capture latency metrics, and inspect historical profiles offline."
        )
        jumbo_lbl = ctk.CTkLabel(
            jumbo, text=jumbo_text, font=get_font(12),
            text_color=get_color("text_secondary"), justify="left"
        )
        jumbo_lbl.pack(anchor="w", padx=20, pady=(0, 15))

        # --- Aggregate Statistics Section ---
        stats_lbl = ctk.CTkLabel(container, text="System Aggregated Metrics", font=get_font(14, "bold"), text_color=get_color("text_primary"))
        stats_lbl.pack(anchor="w", pady=(5, 10))

        # Card layout grid
        self.grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.grid_frame.pack(fill="x", pady=(0, 15))
        self.grid_frame.columnconfigure((0, 1), weight=1, pad=15)
        self.grid_frame.columnconfigure((2, 3), weight=1, pad=15)

        # Dynamic metric cards
        self.card_runs = MetricCard(self.grid_frame, "Total Runs Executed", "0", "Runs logged in SQLite")
        self.card_runs.grid(row=0, column=0, sticky="nsew")

        self.card_reqs = MetricCard(self.grid_frame, "Requests Dispatched", "0", "Total concurrent attempts")
        self.card_reqs.grid(row=0, column=1, sticky="nsew")

        self.card_success = MetricCard(self.grid_frame, "Global Success Rate", "100.0%", "Successful vs failed runs")
        self.card_success.grid(row=0, column=2, sticky="nsew")

        self.card_latency = MetricCard(self.grid_frame, "Global Avg Latency", "0.00s", "Average overall response time")
        self.card_latency.grid(row=0, column=3, sticky="nsew")

        # --- Quick Actions Row ---
        actions_lbl = ctk.CTkLabel(container, text="Quick Shortcuts", font=get_font(14, "bold"), text_color=get_color("text_primary"))
        actions_lbl.pack(anchor="w", pady=(10, 10))

        actions_grid = ctk.CTkFrame(container, fg_color="transparent")
        actions_grid.pack(fill="x", pady=(0, 10))
        actions_grid.columnconfigure((0, 1, 2), weight=1, pad=15)

        # Action Card 1: Start Testing
        card1 = ctk.CTkFrame(actions_grid, fg_color=get_color("bg_secondary"), corner_radius=8)
        card1.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(card1, text="API Load Testing", font=get_font(13, "bold"), text_color=get_color("text_primary")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(card1, text="Run new API stress trials.", font=get_font(11), text_color=get_color("text_secondary")).pack(anchor="w", padx=15, pady=(0, 15))
        ctk.CTkButton(
            card1, text="Start Test 🚀", font=get_font(11, "bold"),
            fg_color=get_color("accent"), hover_color=get_color("accent_hover"),
            command=lambda: self.controller.show_page("testing")
        ).pack(fill="x", padx=15, pady=(0, 15))

        # Action Card 2: View History
        card2 = ctk.CTkFrame(actions_grid, fg_color=get_color("bg_secondary"), corner_radius=8)
        card2.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(card2, text="Database History", font=get_font(13, "bold"), text_color=get_color("text_primary")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(card2, text="Review historical load data.", font=get_font(11), text_color=get_color("text_secondary")).pack(anchor="w", padx=15, pady=(0, 15))
        ctk.CTkButton(
            card2, text="View History 📂", font=get_font(11, "bold"),
            fg_color=get_color("accent"), hover_color=get_color("accent_hover"),
            command=lambda: self.controller.show_page("history")
        ).pack(fill="x", padx=15, pady=(0, 15))

        # Action Card 3: Configure Settings
        card3 = ctk.CTkFrame(actions_grid, fg_color=get_color("bg_secondary"), corner_radius=8)
        card3.grid(row=0, column=3, sticky="nsew")
        ctk.CTkLabel(card3, text="App Preferences", font=get_font(13, "bold"), text_color=get_color("text_primary")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(card3, text="Adjust timeouts, details.", font=get_font(11), text_color=get_color("text_secondary")).pack(anchor="w", padx=15, pady=(0, 15))
        ctk.CTkButton(
            card3, text="Settings ⚙️", font=get_font(11, "bold"),
            fg_color=get_color("accent"), hover_color=get_color("accent_hover"),
            command=lambda: self.controller.show_page("settings")
        ).pack(fill="x", padx=15, pady=(0, 15))

    def refresh_dashboard(self):
        """Fetches aggregate metrics from REST API and updates stats cards."""
        try:
            stats = self.controller.api_client.get_stats()
            
            # Update health badge
            self.health_badge.configure(
                text="● BACKEND ACTIVE",
                text_color="#10b981", # Emerald Green
                fg_color=get_color("bg_secondary")
            )
            
            # Update metric cards
            self.card_runs.update_value(str(stats["total_runs"]))
            self.card_reqs.update_value(str(stats["total_requests"]))
            self.card_success.update_value(f"{stats['success_rate']:.1f}%")
            self.card_latency.update_value(f"{stats['overall_avg_response']:.3f}s")
            
        except Exception as e:
            # Mark backend as offline
            self.health_badge.configure(
                text="● BACKEND OFFLINE",
                text_color="#ef4444", # Red
                fg_color=get_color("bg_secondary")
            )
            
            # Reset cards
            self.card_runs.update_value("N/A")
            self.card_reqs.update_value("N/A")
            self.card_success.update_value("N/A")
            self.card_latency.update_value("N/A")
            
            self.controller.show_notification(f"Database Server Connection Lost: {str(e)}", "danger")
