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
from datetime import datetime
from .utils import handle_files

@Gtk.Template(resource_path='/com/thecirculark/photoorganizer/ui/main.ui')
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

        # Log window
        log_win = PoLogWindow(application=self.get_application())
        log_win.present()

        def run_with_completion():
            handle_files(
                source_folder=Path(source_dir),
                rename_enabled=rename_active,
                organize_enabled=organize_active,
                organize_dir=Path(target_dir),
                dry_run=dry_run_active,
                logger=log_win.log
            )
            log_win.log_end()

        thread = threading.Thread(
            target=run_with_completion,
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
            new_path = folder.get_path()
            self.source_dir_input.set_text(new_path)
            self.destination_dir_input.set_text(new_path)
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

@Gtk.Template(resource_path='/com/thecirculark/photoorganizer/ui/po_log_window.ui')
class PoLogWindow(Adw.ApplicationWindow):
    __gtype_name__ = "PoLogWindow"

    textview = Gtk.Template.Child()
    save_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.buffer = self.textview.get_buffer()
        self.end_mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.file_count = 0
        self.start_time = datetime.now()

        self.save_button.connect("clicked", self.on_save_clicked)

        self._append_text("====================")
        self._append_text("Starting")
        self._append_text(f"Time started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._append_text("====================")
        self._append_text("")

    def log(self, message: str):
        self.file_count += 1
        GLib.idle_add(self._append_text, message)

    def log_end(self):
        GLib.idle_add(self._append_end_message)

    def _append_end_message(self):
        end_time = datetime.now()
        duration = end_time - self.start_time

        self._append_text("")
        self._append_text("====================")
        self._append_text("Done")
        self._append_text(f"Time ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._append_text(f"Total time taken: {duration}")
        self._append_text(f"Processed {self.file_count} files")
        self._append_text("====================")

    def on_save_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Save Log File")
        filename = f"photo_organizer_log_{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        dialog.set_initial_name(filename)

        dialog.save(self, None, self.on_save_finished)

    def on_save_finished(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                start_iter = self.buffer.get_start_iter()
                end_iter = self.buffer.get_end_iter()
                text = self.buffer.get_text(start_iter, end_iter, True)

                with open(file.get_path(), 'w') as f:
                    f.write(text)

        except GLib.Error:
            pass

    def _append_text(self, message: str):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, message + "\n")
        self.textview.scroll_to_mark(self.end_mark, 0.0, True, 0.0, 1.0)
        return False


