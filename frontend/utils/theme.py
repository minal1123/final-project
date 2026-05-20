# Theme definitions for CustomTkinter Frontend
import customtkinter as ctk

THEME_COLORS = {
    "dark": {
        "bg_primary": "#0f0f12",
        "bg_secondary": "#17171e",
        "bg_tertiary": "#22222d",
        "sidebar_bg": "#0c0c0e",
        "accent": "#6366f1",          # Indigo
        "accent_hover": "#4f46e5",
        "text_primary": "#f8f9fa",
        "text_secondary": "#adb5bd",
        "text_muted": "#6c757d",
        "success": "#10b981",         # Success green
        "success_bg": "#064e3b",
        "warning": "#f59e0b",
        "warning_bg": "#78350f",
        "danger": "#ef4444",          # Failure red
        "danger_bg": "#7f1d1d",
        "card_bg": "#1e1e24",
        "chart_grid": "#2a2a35",
        "chart_line": "#6366f1",
        "chart_fill": "rgba(99, 102, 241, 0.15)"
    },
    "light": {
        "bg_primary": "#f3f4f6",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e5e7eb",
        "sidebar_bg": "#f9fafb",
        "accent": "#4f46e5",
        "accent_hover": "#4338ca",
        "text_primary": "#111827",
        "text_secondary": "#4b5563",
        "text_muted": "#9ca3af",
        "success": "#10b981",
        "success_bg": "#d1fae5",
        "warning": "#f59e0b",
        "warning_bg": "#fef3c7",
        "danger": "#ef4444",
        "danger_bg": "#fee2e2",
        "card_bg": "#ffffff",
        "chart_grid": "#e5e7eb",
        "chart_line": "#4f46e5",
        "chart_fill": "rgba(79, 70, 229, 0.15)"
    }
}

FONT_FAMILY = "Segoe UI"

def get_font(size=12, weight="normal", underline=False):
    if underline:
        return (FONT_FAMILY, size, (weight, "underline"))
    return (FONT_FAMILY, size, weight)

def get_color(color_name):
    mode = ctk.get_appearance_mode().lower()
    if mode not in ["dark", "light"]:
        mode = "dark"
    return THEME_COLORS[mode].get(color_name, "#ffffff")

def get_current_theme():
    mode = ctk.get_appearance_mode().lower()
    if mode not in ["dark", "light"]:
        mode = "dark"
    return THEME_COLORS[mode]
