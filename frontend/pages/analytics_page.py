# Analytics Page GUI component with Matplotlib charts
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        self.canvas = None

        # Header Title
        title = ctk.CTkLabel(
            self, text="Performance Analytics",
            font=get_font(24, "bold"),
            text_color=get_color("text_primary")
        )
        title.pack(anchor="w", padx=30, pady=(30, 10))

        # Main Layout Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Empty State Panel (shown when no test result is loaded)
        self.empty_state_frame = ctk.CTkFrame(self.main_container, fg_color=get_color("bg_secondary"), corner_radius=10)
        self.empty_state_frame.pack(fill="both", expand=True)

        empty_label = ctk.CTkLabel(
            self.empty_state_frame,
            text="No Load Test Data Loaded",
            font=get_font(18, "bold"),
            text_color=get_color("text_muted")
        )
        empty_label.pack(expand=True, pady=(0, 5))

        empty_sub = ctk.CTkLabel(
            self.empty_state_frame,
            text="Go to 'API Testing' to start a new load run\nor select a past record in the 'Test History' page.",
            font=get_font(12, "normal"),
            text_color=get_color("text_secondary")
        )
        empty_sub.pack(expand=True, pady=(0, 20))

        # Active Data Panel (swapped in dynamically)
        self.data_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")

        # Stats Cards Grid inside Data Frame
        self.stats_grid = ctk.CTkFrame(self.data_frame, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=(0, 15))

        # Metric labels details
        self.url_badge = ctk.CTkLabel(self.stats_grid, text="URL: N/A", font=get_font(12, "bold"), text_color=get_color("accent"))
        self.url_badge.pack(anchor="w", pady=(0, 10))

        cards_container = ctk.CTkFrame(self.stats_grid, fg_color="transparent")
        cards_container.pack(fill="x")

        # Reusable mini statistic displays
        self.card_total = self._create_mini_card(cards_container, "Total Requests", "0", 0)
        self.card_success = self._create_mini_card(cards_container, "Success Rate", "0%", 1)
        self.card_avg = self._create_mini_card(cards_container, "Avg Response", "0.000s", 2)
        self.card_rps = self._create_mini_card(cards_container, "Req / Sec", "0.0", 3)

        # Charts Area
        self.charts_frame = ctk.CTkFrame(self.data_frame, fg_color=get_color("bg_secondary"), corner_radius=10)
        self.charts_frame.pack(fill="both", expand=True)

    def _create_mini_card(self, parent, title: str, val: str, col: int) -> dict:
        """Helper to create grids of simple stat cells."""
        parent.columnconfigure(col, weight=1)
        frame = ctk.CTkFrame(parent, fg_color=get_color("bg_secondary"), corner_radius=8, height=70)
        frame.grid(row=0, column=col, padx=10, sticky="nsew")
        frame.grid_propagate(False)

        lbl_title = ctk.CTkLabel(frame, text=title.upper(), font=get_font(10, "bold"), text_color=get_color("text_muted"))
        lbl_title.pack(anchor="w", padx=10, pady=(8, 2))

        lbl_val = ctk.CTkLabel(frame, text=val, font=get_font(18, "bold"), text_color=get_color("text_primary"))
        lbl_val.pack(anchor="w", padx=10, pady=(0, 8))

        return {"frame": frame, "val_lbl": lbl_val}

    def render_active_charts(self):
        """Draws/Redraws the charts using matplotlib based on the controller active run data."""
        data = self.controller.active_test_result
        if not data:
            self.data_frame.pack_forget()
            self.empty_state_frame.pack(fill="both", expand=True)
            return

        # Hide empty state, reveal data panel
        self.empty_state_frame.pack_forget()
        self.data_frame.pack(fill="both", expand=True)

        metrics = data["metrics"]
        details = data["details"]

        # 1. Update stats cards values
        self.url_badge.configure(text=f"TARGET ENDPOINT:  [{metrics['method']}] {metrics['url']}")
        
        success_pct = 100.0
        if metrics["total_requests"] > 0:
            success_pct = (metrics["success_count"] / metrics["total_requests"]) * 100
            
        self.card_total["val_lbl"].configure(text=str(metrics["total_requests"]))
        self.card_success["val_lbl"].configure(text=f"{success_pct:.1f}%")
        self.card_avg["val_lbl"].configure(text=f"{metrics['avg_response_time']:.4f}s")
        self.card_rps["val_lbl"].configure(text=f"{metrics['requests_per_second']:.1f}")

        # 2. Render matplotlib subplots
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Theme color detection for styling plots matching the main GUI
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg_hex = "#17171e" if is_dark else "#ffffff"
        fg_hex = "#adb5bd" if is_dark else "#495057"
        grid_hex = "#2a2a35" if is_dark else "#e5e7eb"
        text_primary = "#f8f9fa" if is_dark else "#111827"
        accent_hex = "#6366f1"

        fig = Figure(figsize=(9, 6), dpi=100)
        fig.patch.set_facecolor(bg_hex)

        # Gather dataset arrays
        indices = [d["request_index"] for d in details]
        latencies = [d["response_time"] for d in details]
        success_statuses = [d["success"] for d in details]
        status_codes = [d.get("status_code", 0) for d in details]

        # --- Chart 1: Latency Line Chart ---
        ax1 = fig.add_subplot(221)
        ax1.set_facecolor(bg_hex)
        ax1.plot(indices, latencies, color=accent_hex, linewidth=1.5, label="Latency")
        # Rolling average curve
        if len(latencies) > 5:
            rolling_idx = np.convolve(latencies, np.ones(5)/5, mode='valid')
            ax1.plot(indices[4:], rolling_idx, color="#f59e0b", linestyle="--", linewidth=1.2, label="MA-5")
        ax1.set_title("Response Time Curve", color=text_primary, fontname='Segoe UI', fontsize=11, fontweight='bold', pad=10)
        ax1.set_xlabel("Request index", color=fg_hex, fontsize=9)
        ax1.set_ylabel("Seconds", color=fg_hex, fontsize=9)
        ax1.tick_params(colors=fg_hex, labelsize=8)
        ax1.grid(True, color=grid_hex, linestyle=":", alpha=0.6)
        ax1.legend(facecolor=bg_hex, edgecolor=grid_hex, labelcolor=fg_hex, fontsize=8)

        # --- Chart 2: Success Rate Pie Chart ---
        ax2 = fig.add_subplot(222)
        ax2.set_facecolor(bg_hex)
        success_count = metrics["success_count"]
        failure_count = metrics["failure_count"]
        
        # Guard against zero requests
        if success_count == 0 and failure_count == 0:
            pie_data = [1]
            pie_labels = ["No Data"]
            pie_colors = ["#6c757d"]
        else:
            pie_data = []
            pie_labels = []
            pie_colors = []
            if success_count > 0:
                pie_data.append(success_count)
                pie_labels.append("Success")
                pie_colors.append("#10b981") # Green
            if failure_count > 0:
                pie_data.append(failure_count)
                pie_labels.append("Failure")
                pie_colors.append("#ef4444") # Red

        wedges, texts, autotexts = ax2.pie(
            pie_data, labels=pie_labels, autopct='%1.1f%%',
            colors=pie_colors, startangle=140,
            textprops=dict(color=fg_hex, fontsize=9)
        )
        for autotext in autotexts:
            autotext.set_color('#ffffff')
            autotext.set_fontweight('bold')
        ax2.set_title("Success vs Failure Ratio", color=text_primary, fontname='Segoe UI', fontsize=11, fontweight='bold', pad=10)

        # --- Chart 3: Latency Distribution (Histogram) ---
        ax3 = fig.add_subplot(223)
        ax3.set_facecolor(bg_hex)
        
        bins = min(15, max(5, len(latencies) // 10))
        ax3.hist(latencies, bins=bins, color=accent_hex, edgecolor=bg_hex, alpha=0.85)
        ax3.set_title("Latency Distribution", color=text_primary, fontname='Segoe UI', fontsize=11, fontweight='bold', pad=10)
        ax3.set_xlabel("Seconds", color=fg_hex, fontsize=9)
        ax3.set_ylabel("Requests count", color=fg_hex, fontsize=9)
        ax3.tick_params(colors=fg_hex, labelsize=8)
        ax3.grid(True, color=grid_hex, linestyle=":", alpha=0.6)

        # --- Chart 4: Request Timeline Graph (Latency vs Index, categorized by success) ---
        ax4 = fig.add_subplot(224)
        ax4.set_facecolor(bg_hex)
        
        # Plot Successes as green dots, Failures as red crosses
        success_indices = [indices[i] for i in range(len(indices)) if success_statuses[i]]
        success_latencies = [latencies[i] for i in range(len(latencies)) if success_statuses[i]]
        
        fail_indices = [indices[i] for i in range(len(indices)) if not success_statuses[i]]
        fail_latencies = [latencies[i] for i in range(len(latencies)) if not success_statuses[i]]

        if success_indices:
            ax4.scatter(success_indices, success_latencies, color="#10b981", alpha=0.7, label="2xx OK", s=25)
        if fail_indices:
            ax4.scatter(fail_indices, fail_latencies, color="#ef4444", alpha=0.9, marker="x", label="Error", s=30)
            
        ax4.set_title("Request Timeline Scatter", color=text_primary, fontname='Segoe UI', fontsize=11, fontweight='bold', pad=10)
        ax4.set_xlabel("Request sequence", color=fg_hex, fontsize=9)
        ax4.set_ylabel("Response Latency (s)", color=fg_hex, fontsize=9)
        ax4.tick_params(colors=fg_hex, labelsize=8)
        ax4.grid(True, color=grid_hex, linestyle=":", alpha=0.6)
        ax4.legend(facecolor=bg_hex, edgecolor=grid_hex, labelcolor=fg_hex, fontsize=8)

        # Tight layout adjustments
        fig.tight_layout(pad=3.0)

        # Embed inside CustomTkinter canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
