# Settings Page GUI component
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller

        # Header Title
        title = ctk.CTkLabel(
            self, text="Application Settings",
            font=get_font(24, "bold"),
            text_color=get_color("text_primary")
        )
        title.pack(anchor="w", padx=30, pady=(30, 10))

        subtitle = ctk.CTkLabel(
            self, text="Configure testing parameters, theme options, and view project credits.",
            font=get_font(12, "normal"),
            text_color=get_color("text_secondary")
        )
        subtitle.pack(anchor="w", padx=30, pady=(0, 20))

        # Scrollable container for settings categories
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # --- SECTION 1: APPEARANCE ---
        sec_appearance = ctk.CTkFrame(container, fg_color=get_color("bg_secondary"), corner_radius=10)
        sec_appearance.pack(fill="x", pady=10)
        
        lbl_app = ctk.CTkLabel(sec_appearance, text="Appearance & Styling", font=get_font(16, "bold"), text_color=get_color("accent"))
        lbl_app.pack(anchor="w", padx=20, pady=(15, 10))

        # Theme Option Menu
        theme_frame = ctk.CTkFrame(sec_appearance, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        lbl_theme = ctk.CTkLabel(theme_frame, text="Color Theme Mode", font=get_font(13, "bold"), text_color=get_color("text_primary"))
        lbl_theme.pack(side="left")
        
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Dark", "Light"],
            command=self._change_theme,
            font=get_font(12),
            fg_color=get_color("accent"),
            button_color=get_color("accent_hover")
        )
        self.theme_menu.pack(side="right")
        self.theme_menu.set(ctk.get_appearance_mode())

        # --- SECTION 2: TESTING DEFAULTS ---
        sec_testing = ctk.CTkFrame(container, fg_color=get_color("bg_secondary"), corner_radius=10)
        sec_testing.pack(fill="x", pady=10)
        
        lbl_test_title = ctk.CTkLabel(sec_testing, text="Default Request Configurations", font=get_font(16, "bold"), text_color=get_color("accent"))
        lbl_test_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Timeout setting
        timeout_frame = ctk.CTkFrame(sec_testing, fg_color="transparent")
        timeout_frame.pack(fill="x", padx=20, pady=5)
        lbl_timeout = ctk.CTkLabel(timeout_frame, text="Request Timeout (seconds)", font=get_font(13), text_color=get_color("text_primary"))
        lbl_timeout.pack(side="left")
        
        self.timeout_entry = ctk.CTkEntry(timeout_frame, width=80, font=get_font(12))
        self.timeout_entry.pack(side="right")
        self.timeout_entry.insert(0, str(self.controller.settings.get("timeout", 10.0)))

        # Default concurrency level
        con_frame = ctk.CTkFrame(sec_testing, fg_color="transparent")
        con_frame.pack(fill="x", padx=20, pady=(5, 15))
        lbl_con = ctk.CTkLabel(con_frame, text="Default Concurrency Cap", font=get_font(13), text_color=get_color("text_primary"))
        lbl_con.pack(side="left")
        
        self.con_entry = ctk.CTkEntry(con_frame, width=80, font=get_font(12))
        self.con_entry.pack(side="right")
        self.con_entry.insert(0, str(self.controller.settings.get("concurrency", 10)))

        # Save Settings Button
        save_btn = ctk.CTkButton(
            sec_testing, text="Save Default Settings",
            command=self._save_settings,
            font=get_font(12, "bold"),
            fg_color=get_color("accent"),
            hover_color=get_color("accent_hover")
        )
        save_btn.pack(anchor="e", padx=20, pady=(10, 15))

        # --- SECTION 3: ACADEMIC CREDITS & SE INFO ---
        sec_credits = ctk.CTkFrame(container, fg_color=get_color("bg_secondary"), corner_radius=10)
        sec_credits.pack(fill="x", pady=10)
        
        lbl_cred_title = ctk.CTkLabel(sec_credits, text="University Project Details", font=get_font(16, "bold"), text_color=get_color("accent"))
        lbl_cred_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        credits_text = (
            "Course: Software Construction & Development (4th Semester)\n"
            "Project: API Load Testing Dashboard\n"
            "Tech Stack: Python, CustomTkinter, Matplotlib, SQLite, Flask REST API\n\n"
            "This application validates architectural separation, asynchronous workers,\n"
            "Client-Server synchronization, concurrent load limits, and relational history mapping."
        )
        lbl_credits = ctk.CTkLabel(
            sec_credits, text=credits_text,
            font=get_font(12, "normal"),
            text_color=get_color("text_secondary"),
            justify="left"
        )
        lbl_credits.pack(anchor="w", padx=20, pady=(0, 20))

    def _change_theme(self, choice: str):
        """Sets the app theme mode."""
        ctk.set_appearance_mode(choice)
        self.controller.show_notification(f"Theme mode changed to {choice}", "info")

    def _save_settings(self):
        """Saves current fields in controller memory."""
        timeout_str = self.timeout_entry.get().strip()
        con_str = self.con_entry.get().strip()
        
        try:
            timeout_val = float(timeout_str)
            if timeout_val <= 0:
                raise ValueError
        except ValueError:
            self.controller.show_notification("Timeout must be a positive float number.", "error")
            return
            
        try:
            con_val = int(con_str)
            if con_val <= 0 or con_val > 200:
                raise ValueError
        except ValueError:
            self.controller.show_notification("Concurrency must be an integer between 1 and 200.", "error")
            return

        self.controller.settings["timeout"] = timeout_val
        self.controller.settings["concurrency"] = con_val
        self.controller.show_notification("Configuration saved successfully.", "success")
