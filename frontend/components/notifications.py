# Reusable notification widget for CustomTkinter
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color

class NotificationBanner(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=6, border_width=0, height=40, **kwargs)
        
        self.message_label = ctk.CTkLabel(
            self, text="",
            font=get_font(12, "bold"),
            text_color="#ffffff"
        )
        self.message_label.pack(side="left", fill="both", expand=True, padx=(15, 10))
        
        # Close Button
        self.close_btn = ctk.CTkButton(
            self, text="✕", width=25, height=25,
            font=get_font(10, "bold"),
            fg_color="transparent",
            hover_color="rgba(255,255,255,0.15)",
            text_color="#ffffff",
            command=self.hide
        )
        self.close_btn.pack(side="right", padx=10)
        
        self.hide()

    def show(self, message: str, level: str = "info"):
        """Displays banner with message themed according to level."""
        self.message_label.configure(text=message)
        
        # Define background colors based on notification type
        if level == "success":
            self.configure(fg_color=get_color("success"))
        elif level == "danger" or level == "error":
            self.configure(fg_color=get_color("danger"))
        elif level == "warning":
            self.configure(fg_color=get_color("warning"))
        else: # info
            self.configure(fg_color=get_color("accent"))
            
        self.pack(fill="x", padx=20, pady=(10, 0), before=self.master.winfo_children()[0])
        
        # Auto-dismiss after 6 seconds
        self.after(6000, self.hide)

    def hide(self):
        """Hides banner from screen."""
        self.pack_forget()
