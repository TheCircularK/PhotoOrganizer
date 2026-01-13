# window.py
#
# Copyright 2026 Andrew
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from pathlib import Path
import threading
from .utils import handle_files

@Gtk.Template(resource_path='/com/titanexperts/photoorganizer/ui/main.ui')
class PhotoOrganizerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PhotoOrganizerWindow'

    # Source directory inputs
    source_dir_button = Gtk.Template.Child()
    source_dir_input = Gtk.Template.Child()

    # Organize toggle
    organize_toggle = Gtk.Template.Child()

    # Destination directory inputs
    destination_dir_button = Gtk.Template.Child()
    destination_dir_input = Gtk.Template.Child()

    # Rename toggle
    rename_toggle = Gtk.Template.Child()

    # Dry run toggle
    dry_run_toggle = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.source_dir_button.connect(
            "clicked",
            self.on_source_dir_clicked
        )

        self.destination_dir_button.connect(
            "clicked",
            self.on_destination_dir_clicked
        )

        run_action = Gio.SimpleAction.new("run", None)
        run_action.connect("activate", self.on_run)
        self.add_action(run_action)

        self.get_application().set_accels_for_action(
            "win.run",
            ["<primary>Return"]
        )

    def on_run(self, action, param):
        source_dir = self.source_dir_input.get_text()
        target_dir = self.destination_dir_input.get_text()

        organize_active = self.organize_toggle.get_active()
        rename_active = self.rename_toggle.get_active()
        dry_run_active = self.dry_run_toggle.get_active()

        print(f"Source Directory: {source_dir}")
        print(f"Target Directory: {target_dir}")
        print(f"Organize: {organize_active}")
        print(f"Rename: {rename_active}")
        print(f"Dry run: {dry_run_active}")

        # Log window
        log_win = PoLogWindow(application=self.get_application())
        log_win.present()

        thread = threading.Thread(
            target=handle_files,
            kwargs={
                "source_folder": Path(source_dir),
                "rename_enabled": rename_active,
                "organize_enabled": organize_active,
                "organize_dir": Path(target_dir),
                "dry_run": dry_run_active,
                "logger": log_win.log
            },
            daemon=True
        )

        thread.start()

    def on_source_dir_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Source Directory")

        dialog.select_folder(
            self,
            None,
            self.on_source_dir_selected
        )

    def on_source_dir_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            self.source_dir_input.set_text(folder.get_path())
        except GLib.Error:
            pass

    def on_destination_dir_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Destination Directory")

        dialog.select_folder(
            self,
            None,
            self.on_destination_dir_selected
        )

    def on_destination_dir_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            self.destination_dir_input.set_text(folder.get_path())
        except GLib.Error:
            pass

@Gtk.Template(resource_path='/com/titanexperts/photoorganizer/ui/po_log_window.ui')
class PoLogWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PoLogWindow"

    textview = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buffer = self.textview.get_buffer()

    def log(self, message: str):
        """Append a line to the log in the TextView safely in the GTK main loop."""
        GLib.idle_add(self._append_text, message)

    def _append_text(self, message: str):
        end_iter = self.buffer.get_end_iter()
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), True)
        self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        return False


