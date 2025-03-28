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
        self.destroy_tray_icon()

        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill="yellow", outline="orange", width=3)

        icon_text = self.lang_strings.get("MSG_04", "Brightness Control")

        menu = pystray.Menu(
            pystray.MenuItem(
                self.lang_strings.get("MSG_12", "Open"),
                lambda icon, item: self.on_menu_item_click('open'),
                default=True
            ),
            pystray.MenuItem(
                self.lang_strings.get("MSG_13", "Exit"),
                lambda icon, item: self.on_menu_item_click('exit')
            )
        )

        self.tray_icon = pystray.Icon(icon_text, image, icon_text, menu=menu)

        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def destroy_tray_icon(self):
        if self.tray_icon:
            # Remove tray icon visibility to avoid interaction
            self.tray_icon.visible = False
            self.tray_icon.stop()
            self.tray_icon = None
            # Do not join if we are on the same thread to avoid RuntimeError
            if threading.current_thread() != self.tray_thread and self.tray_thread.is_alive():
                self.tray_thread.join(timeout=1)
            self.tray_thread = None

    def hide_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.visible = False

    def show_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.visible = True

    def update_tray_icon(self, lang_strings):
        self.lang_strings = lang_strings
        self.create_tray_icon()

    def on_menu_item_click(self, action):
        if action == 'open':
            self.show_window_callback()
            self.hide_tray_icon()
        elif action == 'exit':
            self.exit_app_callback()

    def set_tray_icon_visibility(self, visible):
        if self.tray_icon:
            self.tray_icon.visible = visible
