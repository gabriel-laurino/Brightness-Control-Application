import threading
from PIL import Image, ImageDraw
import pystray


class TrayService:
    def __init__(self, show_window_callback, exit_app_callback, lang_strings):
        self.show_window_callback = show_window_callback
        self.exit_app_callback = exit_app_callback
        self.lang_strings = lang_strings
        self.tray_icon = None
        self.tray_thread = None

    def create_tray_icon(self):
        # Ensure to destroy the previous tray icon if it exists
        self.destroy_tray_icon()

        # Create tray icon image
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill="yellow", outline="orange", width=3)

        # Use language string for the icon text
        icon_text = self.lang_strings.get("MSG_04", "Brightness Control")

        # Define tray menu options
        menu = pystray.Menu(
            pystray.MenuItem(
                self.lang_strings.get("MSG_12", "Open"),
                lambda: self.on_menu_item_click('open'),
                default=True
            ),
            pystray.MenuItem(
                self.lang_strings.get("MSG_13", "Exit"),
                lambda: self.on_menu_item_click('exit')
            )
        )

        # Create tray icon instance
        self.tray_icon = pystray.Icon(icon_text, image, icon_text, menu=menu)

        # Run tray icon in a separate thread
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def destroy_tray_icon(self):
        # Safely destroy the tray icon
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            if self.tray_thread and self.tray_thread.is_alive():
                self.tray_thread.join(timeout=1)
            self.tray_thread = None

    def hide_tray_icon(self):
        # Hide tray icon
        if self.tray_icon:
            self.tray_icon.visible = False

    def show_tray_icon(self):
        # Show tray icon
        if self.tray_icon:
            self.tray_icon.visible = True

    def update_tray_icon(self, lang_strings):
        # Update tray icon with new language strings
        self.lang_strings = lang_strings
        self.create_tray_icon()

    def on_menu_item_click(self, action):
        # Handle menu item click events
        if action == 'open':
            self.show_window_callback()
            self.hide_tray_icon()
        elif action == 'exit':
            self.exit_app_callback()
