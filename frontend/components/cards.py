# Custom reusable cards for frontend dashboard
import customtkinter as ctk
from frontend.utils.theme import get_font, get_color

class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str, subtext: str = "", border_color: str = None, **kwargs):
        super().__init__(parent, corner_radius=10, border_width=1 if border_color else 0, **kwargs)
        
        self.configure(fg_color=get_color("bg_secondary"))
        if border_color:
            self.configure(border_color=border_color)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text=title.upper(),
            font=get_font(11, "bold"),
            text_color=get_color("text_muted")
        )
        self.title_label.pack(anchor="w", padx=15, pady=(15, 2))

        # Value Label
        self.value_label = ctk.CTkLabel(
            self, text=value,
            font=get_font(28, "bold"),
            text_color=get_color("text_primary")
        )
        self.value_label.pack(anchor="w", padx=15, pady=(0, 2))

        # Subtext Label
        self.subtext_label = ctk.CTkLabel(
            self, text=subtext,
            font=get_font(11, "normal"),
            text_color=get_color("text_secondary")
        )
        if subtext:
            self.subtext_label.pack(anchor="w", padx=15, pady=(0, 15))
        else:
            # Spacer at bottom
            ctk.CTkFrame(self, height=10, fg_color="transparent").pack()

    def update_value(self, new_value: str, new_subtext: str = None):
        """Updates card text dynamically."""
        self.value_label.configure(text=new_value)
        if new_subtext is not None:
            self.subtext_label.configure(text=new_subtext)
