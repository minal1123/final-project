# Testing Page GUI component with real-time progress, console logging, and input forms
import customtkinter as ctk
import json
import time
from datetime import datetime
from frontend.utils.theme import get_font, get_color
from frontend.utils.validation import (
    validate_url, validate_requests, validate_concurrency, 
    validate_interval, validate_json_string
)

class TestingPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        
        # Test status state
        self.task_id = None
        self.is_running = False
        self.last_completed_count = 0

        # Header Title
        title = ctk.CTkLabel(
            self, text="API Load Testing",
            font=get_font(24, "bold"),
            text_color=get_color("text_primary")
        )
        title.pack(anchor="w", padx=30, pady=(30, 10))

        # Main grid container (Left: Form Inputs, Right: Progress & Console Log)
        grid_container = ctk.CTkFrame(self, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        grid_container.columnconfigure(0, weight=4, pad=15)
        grid_container.columnconfigure(1, weight=5, pad=15)
        grid_container.rowconfigure(0, weight=1)

        # ==========================================
        # LEFT COLUMN: Form Inputs
        # ==========================================
        self.form_frame = ctk.CTkScrollableFrame(grid_container, fg_color=get_color("bg_secondary"), corner_radius=10)
        self.form_frame.grid(row=0, column=0, sticky="nsew")

        lbl_setup = ctk.CTkLabel(self.form_frame, text="Load Test Configurations", font=get_font(16, "bold"), text_color=get_color("accent"))
        lbl_setup.pack(anchor="w", padx=20, pady=(15, 15))

        # Endpoint entry
        lbl_url = ctk.CTkLabel(self.form_frame, text="Target URL", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        lbl_url.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.url_entry = ctk.CTkEntry(self.form_frame, placeholder_text="e.g. http://127.0.0.1:5000/api/dummy/success", font=get_font(12))
        self.url_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.url_entry.insert(0, "http://127.0.0.1:5000/api/dummy/success") # Default to mock server success route

        # HTTP Method and Concurrency row
        row1 = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        row1.columnconfigure(0, weight=1, pad=10)
        row1.columnconfigure(1, weight=1, pad=10)

        # Method OptionMenu
        col_m = ctk.CTkFrame(row1, fg_color="transparent")
        col_m.grid(row=0, column=0, sticky="ew")
        lbl_method = ctk.CTkLabel(col_m, text="HTTP Method", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        lbl_method.pack(anchor="w")
        self.method_menu = ctk.CTkOptionMenu(
            col_m, values=["GET", "POST", "PUT", "DELETE"],
            font=get_font(12), fg_color=get_color("accent"), button_color=get_color("accent_hover")
        )
        self.method_menu.pack(fill="x", pady=(2, 0))

        # Concurrency
        col_c = ctk.CTkFrame(row1, fg_color="transparent")
        col_c.grid(row=0, column=1, sticky="ew")
        lbl_con = ctk.CTkLabel(col_c, text="Concurrency Level", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        lbl_con.pack(anchor="w")
        self.con_entry = ctk.CTkEntry(col_c, font=get_font(12))
        self.con_entry.pack(fill="x", pady=(2, 0))
        self.con_entry.insert(0, "10")

        # Requests Count and Interval row
        row2 = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(5, 10))
        row2.columnconfigure(0, weight=1, pad=10)
        row2.columnconfigure(1, weight=1, pad=10)

        # Total Requests
        col_r = ctk.CTkFrame(row2, fg_color="transparent")
        col_r.grid(row=0, column=0, sticky="ew")
        lbl_req = ctk.CTkLabel(col_r, text="Total Requests", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        lbl_req.pack(anchor="w")
        self.req_entry = ctk.CTkEntry(col_r, font=get_font(12))
        self.req_entry.pack(fill="x", pady=(2, 0))
        self.req_entry.insert(0, "100")

        # Request Interval
        col_i = ctk.CTkFrame(row2, fg_color="transparent")
        col_i.grid(row=0, column=1, sticky="ew")
        lbl_int = ctk.CTkLabel(col_i, text="Interval Delay (sec)", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        lbl_int.pack(anchor="w")
        self.int_entry = ctk.CTkEntry(col_i, font=get_font(12))
        self.int_entry.pack(fill="x", pady=(2, 0))
        self.int_entry.insert(0, "0.0")

        # Tabview for Headers and Body
        self.tabs = ctk.CTkTabview(self.form_frame, height=180)
        self.tabs._segmented_button.configure(font=get_font(11, "bold"))
        self.tabs.pack(fill="x", padx=20, pady=10)
        
        tab_headers = self.tabs.add("Headers (JSON)")
        tab_body = self.tabs.add("Request Body (JSON)")

        # Headers Textbox
        self.headers_text = ctk.CTkTextbox(tab_headers, font=("Consolas", 11), height=110)
        self.headers_text.pack(fill="both", expand=True)
        self.headers_text.insert("0.0", '{\n  "Content-Type": "application/json"\n}')

        # Body Textbox
        self.body_text = ctk.CTkTextbox(tab_body, font=("Consolas", 11), height=110)
        self.body_text.pack(fill="both", expand=True)
        self.body_text.insert("0.0", '{\n  "test_param": "hello"\n}')

        # Submit / Cancel Buttons
        btns_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btns_row.pack(fill="x", padx=20, pady=(10, 15))

        self.btn_start = ctk.CTkButton(
            btns_row, text="🚀 Start Load Test",
            command=self._start_testing,
            font=get_font(13, "bold"),
            fg_color=get_color("accent"),
            hover_color=get_color("accent_hover"),
            height=36
        )
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_stop = ctk.CTkButton(
            btns_row, text="🛑 Stop Test",
            command=self._stop_testing,
            font=get_font(13, "bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            height=36,
            state="disabled"
        )
        self.btn_stop.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ==========================================
        # RIGHT COLUMN: Progress & Console Log
        # ==========================================
        self.console_frame = ctk.CTkFrame(grid_container, fg_color=get_color("bg_secondary"), corner_radius=10)
        self.console_frame.grid(row=0, column=1, sticky="nsew")

        # Title
        lbl_console_title = ctk.CTkLabel(self.console_frame, text="Live Test Monitor", font=get_font(16, "bold"), text_color=get_color("accent"))
        lbl_console_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Progress bar panel
        self.progress_panel = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.progress_panel.pack(fill="x", padx=20, pady=(0, 10))

        self.progress_label = ctk.CTkLabel(self.progress_panel, text="Status: Ready to Test", font=get_font(12, "bold"), text_color=get_color("text_primary"))
        self.progress_label.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(self.progress_panel, height=8, fg_color=get_color("bg_tertiary"), progress_color=get_color("accent"))
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0.0)

        # Logging Console Textbox
        self.log_console = ctk.CTkTextbox(
            self.console_frame,
            font=("Consolas", 10),
            fg_color="#0a0a0c" if ctk.get_appearance_mode().lower() == "dark" else "#f8f9fa",
            text_color="#30ff90" if ctk.get_appearance_mode().lower() == "dark" else "#065f46"
        )
        self.log_console.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.log_console.configure(state="disabled")

        # Switch to Analytics action link
        self.lnk_analytics = ctk.CTkButton(
            self.console_frame, text="📊 View Performance Analytics for this run",
            command=self._view_analytics,
            font=get_font(12, "bold"),
            fg_color="transparent",
            text_color=get_color("accent"),
            hover=False,
            state="disabled",
            height=25
        )
        self.lnk_analytics.pack(pady=(0, 15))

    def _start_testing(self):
        """Validates input fields, blocks form input, and hits backend REST endpoint to begin."""
        # 1. Gather inputs
        url = self.url_entry.get().strip()
        method = self.method_menu.get()
        reqs_str = self.req_entry.get().strip()
        con_str = self.con_entry.get().strip()
        int_str = self.int_entry.get().strip()
        
        headers_str = self.headers_text.get("0.0", "end")
        body_str = self.body_text.get("0.0", "end")

        # 2. Client-side input validations
        valid, res_url = validate_url(url)
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_url}", "error")
            return
            
        valid, res_reqs = validate_requests(reqs_str)
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_reqs}", "error")
            return
            
        valid, res_con = validate_concurrency(con_str, res_reqs)
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_con}", "error")
            return
            
        valid, res_int = validate_interval(int_str)
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_int}", "error")
            return
            
        valid, res_headers = validate_json_string(headers_str, "Headers")
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_headers}", "error")
            return
            
        valid, res_body = validate_json_string(body_str, "Request Body")
        if not valid:
            self.controller.show_notification(f"Validation Error: {res_body}", "error")
            return

        # 3. Lock controls
        self._toggle_form_inputs(state="disabled")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.lnk_analytics.configure(state="disabled")
        
        # Reset Log Console
        self.log_console.configure(state="normal")
        self.log_console.delete("0.0", "end")
        self.log_console.configure(state="disabled")
        
        self.last_completed_count = 0
        self.is_running = True
        
        self._write_log(f"Initializing Stress Test against {res_url}...")
        self._write_log(f"Configuration: Concurrency={res_con}, Total Requests={res_reqs}, Stagger delay={res_int}s.")

        # 4. Initiate Flask endpoint call
        try:
            task_id = self.controller.api_client.start_test(
                url=res_url,
                method=method,
                requests_count=res_reqs,
                concurrency=res_con,
                interval=res_int,
                headers=res_headers,
                body=res_body
            )
            self.task_id = task_id
            self.progress_label.configure(text=f"Progress: 0 / {res_reqs} requests (0.0%)")
            self.progress_bar.set(0.0)
            
            # Start polling loop
            self.after(200, self._poll_status)
        except Exception as e:
            self._write_log(f"CRITICAL BACKEND ERROR: {str(e)}")
            self.controller.show_notification(f"Run initiation failed: {str(e)}", "error")
            self._finalize_run_gui()

    def _poll_status(self):
        """Periodically requests metrics snapshot and populates console."""
        if not self.is_running:
            return

        try:
            snapshot = self.controller.api_client.get_test_status(self.task_id)
            status = snapshot["status"]
            
            # Update Progress Bar & Title
            completed = snapshot["completed_count"]
            total = snapshot["total_requests"]
            progress = snapshot["progress_percent"] / 100.0 if total > 0 else 0.0
            
            self.progress_bar.set(progress)
            self.progress_label.configure(
                text=f"Progress: {completed} / {total} requests ({snapshot['progress_percent']}%)"
            )

            # Append new completed request logs to console
            details = snapshot["details"]
            if len(details) > self.last_completed_count:
                new_details = details[self.last_completed_count:]
                for d in new_details:
                    time_stamp = datetime.now().strftime("%H:%M:%S")
                    if d["success"]:
                        self._write_log(
                            f"[{time_stamp}] Request #{d['request_index']}: HTTP {d['status_code']} OK ({d['response_time']:.4f}s)"
                        )
                    else:
                        self._write_log(
                            f"[{time_stamp}] Request #{d['request_index']}: FAILED - {d.get('error_message') or 'Network Error'} ({d['response_time']:.4f}s)"
                        )
                self.last_completed_count = len(details)

            # Check termination
            if status in ["finished", "stopped", "error"]:
                self.is_running = False
                
                # Update main controller result storage
                self.controller.active_test_result = {
                    "metrics": {
                        "url": snapshot["details"][0]["error_message"] if len(snapshot["details"]) == 0 and status == "error" else self.url_entry.get().strip(),
                        "method": self.method_menu.get(),
                        "total_requests": snapshot["completed_count"],
                        "success_count": snapshot["success_count"],
                        "failure_count": snapshot["failure_count"],
                        "avg_response_time": snapshot["avg_response_time"],
                        "min_response_time": snapshot["min_response_time"],
                        "max_response_time": snapshot["max_response_time"],
                        "requests_per_second": snapshot["requests_per_second"],
                        "timestamp": snapshot["timestamp"]
                    },
                    "details": snapshot["details"]
                }
                
                if status == "finished":
                    self._write_log("-" * 60)
                    self._write_log(f"TEST COMPLETED SUCCESSFULLY IN {snapshot['elapsed_time']:.2f}s!")
                    self._write_log(f"Average response latency: {snapshot['avg_response_time']:.4f} seconds.")
                    self._write_log(f"RPS: {snapshot['requests_per_second']:.1f} | Success Rate: {snapshot['success_count']}/{snapshot['completed_count']}")
                    self.controller.show_notification("Stress load testing complete!", "success")
                elif status == "stopped":
                    self._write_log("-" * 60)
                    self._write_log(f"TEST TERMINATED EARLY BY USER (Ran for {snapshot['elapsed_time']:.2f}s)")
                    self._write_log(f"Saved partial metrics: {snapshot['completed_count']} requests completed.")
                    self.controller.show_notification("Test stopped by user.", "warning")
                else: # error
                    self._write_log("-" * 60)
                    self._write_log(f"TEST ABORTED DUE TO ERROR: {snapshot['error_message']}")
                    self.controller.show_notification(f"Run error: {snapshot['error_message']}", "error")

                self._finalize_run_gui()
            else:
                # Schedule next poll
                self.after(200, self._poll_status)

        except Exception as e:
            self._write_log(f"POLLING EXCEPTION: {str(e)}")
            self.is_running = False
            self.controller.show_notification("Lost connection to Flask API.", "error")
            self._finalize_run_gui()

    def _stop_testing(self):
        """Requests backend to abort thread execution."""
        if not self.task_id:
            return
            
        try:
            self.btn_stop.configure(state="disabled")
            self._write_log("Sending abort signal to backend...")
            self.controller.api_client.stop_test(self.task_id)
        except Exception as e:
            self._write_log(f"Failed to cancel: {str(e)}")

    def _finalize_run_gui(self):
        """Unlocks configuration inputs, enables View Analytics link, and resets buttons."""
        self._toggle_form_inputs(state="normal")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        
        # Enable analytics link if we have some data
        if self.controller.active_test_result and len(self.controller.active_test_result["details"]) > 0:
            self.lnk_analytics.configure(state="normal")

    def _toggle_form_inputs(self, state: str):
        """Helper to unlock/lock fields."""
        self.url_entry.configure(state=state)
        self.method_menu.configure(state=state)
        self.con_entry.configure(state=state)
        self.req_entry.configure(state=state)
        self.int_entry.configure(state=state)

    def _write_log(self, text: str):
        """Appends line to Console textbox."""
        self.log_console.configure(state="normal")
        self.log_console.insert("end", f"{text}\n")
        self.log_console.see("end")
        self.log_console.configure(state="disabled")

    def _view_analytics(self):
        """Helper redirection link to Analytics page."""
        self.controller.show_page("analytics")
        self.controller.pages["analytics"].render_active_charts()
