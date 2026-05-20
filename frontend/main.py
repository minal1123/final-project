# Frontend Entry Point for API Load Testing Dashboard
import os
import sys
import customtkinter as ctk

# Add project root directory to path to resolve imports properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.pages.main_window import APILoadTesterApp

def main():
    # Initialize customtkinter parameters
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    print("[Frontend] Starting CustomTkinter graphical client...")
    app = APILoadTesterApp()
    app.mainloop()

if __name__ == '__main__':
    main()
