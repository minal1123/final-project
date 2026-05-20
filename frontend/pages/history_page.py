# History Page GUI component
import customtkinter as ctk
from tkinter import ttk, filedialog
from frontend.utils.theme import get_font, get_color
from frontend.services.api_client import APIClient
from frontend.services.report_exporter import ReportExporter
import os

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Header Title
        title = ctk.CTkLabel(
            self, text="Load Testing History",
            font=get_font(24, "bold"),
            text_color=get_color("text_primary")
        )
        title.pack(anchor="w", padx=30, pady=(30, 10))

        subtitle = ctk.CTkLabel(
            self, text="View previous tests, delete database records, reload past charts, or export summary reports.",
            font=get_font(12, "normal"),
            text_color=get_color("text_secondary")
        )
        subtitle.pack(anchor="w", padx=30, pady=(0, 20))

        # Action Buttons bar
        actions_bar = ctk.CTkFrame(self, fg_color="transparent")
        actions_bar.pack(fill="x", padx=30, pady=(0, 10))

        self.btn_load = ctk.CTkButton(
            actions_bar, text="📈 Load Analytics",
            command=self._load_analytics,
            font=get_font(12, "bold"),
            fg_color=get_color("accent"),
            hover_color=get_color("accent_hover")
        )
        self.btn_load.pack(side="left", padx=(0, 10))

        self.btn_export = ctk.CTkButton(
            actions_bar, text="📥 Export Report",
            command=self._export_report,
            font=get_font(12, "bold"),
            fg_color="#10b981", # Success emerald green
            hover_color="#059669"
        )
        self.btn_export.pack(side="left", padx=10)

        self.btn_delete = ctk.CTkButton(
            actions_bar, text="🗑 Delete Test",
            command=self._delete_test,
            font=get_font(12, "bold"),
            fg_color="#ef4444", # Red
            hover_color="#dc2626"
        )
        self.btn_delete.pack(side="left", padx=10)

        self.btn_refresh = ctk.CTkButton(
            actions_bar, text="🔄 Refresh",
            command=self.refresh_history,
            font=get_font(12, "bold"),
            fg_color=get_color("bg_secondary"),
            text_color=get_color("text_primary"),
            hover_color=get_color("bg_tertiary"),
            width=80
        )
        self.btn_refresh.pack(side="right")

        # Treeview for Listing Runs
        tree_frame = ctk.CTkFrame(self, fg_color=get_color("bg_secondary"), corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Setup custom theme styling for ttk treeview
        self._configure_treeview_styles()

        columns = ("id", "timestamp", "method", "url", "requests", "success_rate", "avg_latency", "rps")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define Headings
        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("method", text="Method")
        self.tree.heading("url", text="Target URL")
        self.tree.heading("requests", text="Total Req.")
        self.tree.heading("success_rate", text="Success Rate")
        self.tree.heading("avg_latency", text="Avg Latency (s)")
        self.tree.heading("rps", text="Req/Sec")

        # Define column widths & anchors
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("timestamp", width=140, anchor="center")
        self.tree.column("method", width=80, anchor="center")
        self.tree.column("url", width=280, anchor="w")
        self.tree.column("requests", width=80, anchor="center")
        self.tree.column("success_rate", width=100, anchor="center")
        self.tree.column("avg_latency", width=110, anchor="center")
        self.tree.column("rps", width=80, anchor="center")

        # Scrollbars
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Bind row selection change
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _configure_treeview_styles(self):
        """Styles the standard ttk Treeview to blend with Dark/Light theme."""
        style = ttk.Style()
        theme = get_color("bg_primary") # Quick theme check
        
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        
        bg_color = "#1e1e24" if is_dark else "#ffffff"
        fg_color = "#f8f9fa" if is_dark else "#111827"
        head_bg = "#121216" if is_dark else "#e5e7eb"
        head_fg = "#ffffff" if is_dark else "#111827"
        select_bg = "#6366f1" if is_dark else "#4f46e5"
        select_fg = "#ffffff"
        
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color,
            font=get_font(11),
            rowheight=30
        )
        style.map(
            "Treeview",
            background=[("selected", select_bg)],
            foreground=[("selected", select_fg)]
        )
        style.configure(
            "Treeview.Heading",
            background=head_bg,
            foreground=head_fg,
            font=get_font(11, "bold"),
            borderwidth=1
        )

    def refresh_history(self):
        """Fetches history records from the Flask backend and populates Treeview."""
        # Refresh colors dynamically
        self._configure_treeview_styles()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            runs = self.controller.api_client.get_history()
            for r in runs:
                # Calculate success rate
                success_pct = 100.0
                if r["total_requests"] > 0:
                    success_pct = (r["success_count"] / r["total_requests"]) * 100
                
                self.tree.insert(
                    "", "end",
                    values=(
                        r["id"],
                        r["timestamp"],
                        r["method"],
                        r["url"],
                        r["total_requests"],
                        f"{success_pct:.1f}%",
                        f"{r['avg_response_time']:.4f}s",
                        f"{r['requests_per_second']:.1f}"
                    )
                )
        except Exception as e:
            self.controller.show_notification(f"History Fetch Failed: {str(e)}", "error")

    def _on_select(self, event):
        """Enables/disables action buttons depending on whether a row is selected."""
        # Browse selection is handled by command callbacks checking self.tree.selection()
        pass

    def _get_selected_run_id(self) -> int | None:
        """Helper to get selected Treeview ID."""
        selected = self.tree.selection()
        if not selected:
            self.controller.show_notification("Please select a test run from the table first.", "warning")
            return None
        item_values = self.tree.item(selected[0], "values")
        return int(item_values[0])

    def _load_analytics(self):
        """Loads selected run metrics and switches to Analytics Page."""
        run_id = self._get_selected_run_id()
        if not run_id:
            return
            
        try:
            self.controller.show_loading_animation()
            # Fetch detail
            run_data = self.controller.api_client.get_history_detail(run_id)
            
            # Store in controller active run slot
            self.controller.active_test_result = {
                "metrics": run_data["metrics"],
                "details": run_data["details"]
            }
            
            # Switch to analytics page and render charts
            self.controller.show_page("analytics")
            # Trigger render
            self.controller.pages["analytics"].render_active_charts()
            self.controller.show_notification(f"Loaded analytics for run #{run_id}", "success")
        except Exception as e:
            self.controller.show_notification(f"Failed to load analytics: {str(e)}", "error")
        finally:
            self.controller.hide_loading_animation()

    def _export_report(self):
        """Opens file dialog and exports the test run."""
        run_id = self._get_selected_run_id()
        if not run_id:
            return
            
        try:
            run_data = self.controller.api_client.get_history_detail(run_id)
            metrics = run_data["metrics"]
            details = run_data["details"]
            
            # Open file dialog
            file_types = [("CSV Document", "*.csv"), ("Text Report", "*.txt")]
            filepath = filedialog.asksaveasfilename(
                title="Export Load Testing Report",
                filetypes=file_types,
                defaultextension=".csv",
                initialfile=f"load_test_report_run_{run_id}"
            )
            
            if not filepath:
                return # User cancelled
                
            _, ext = os.path.splitext(filepath)
            
            success = False
            if ext.lower() == ".csv":
                success = ReportExporter.export_to_csv(filepath, metrics, details)
            else:
                success = ReportExporter.export_to_text(filepath, metrics, details)
                
            if success:
                self.controller.show_notification(f"Report exported to {os.path.basename(filepath)}", "success")
            else:
                self.controller.show_notification("Export failed during file write.", "error")
        except Exception as e:
            self.controller.show_notification(f"Failed to export: {str(e)}", "error")

    def _delete_test(self):
        """Deletes selected test run."""
        run_id = self._get_selected_run_id()
        if not run_id:
            return
            
        try:
            success = self.controller.api_client.delete_history(run_id)
            if success:
                self.controller.show_notification(f"Deleted test run #{run_id}", "success")
                self.refresh_history()
            else:
                self.controller.show_notification("Failed to delete record.", "error")
        except Exception as e:
            self.controller.show_notification(f"Deletion failed: {str(e)}", "error")
