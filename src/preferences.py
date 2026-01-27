# preferences.py
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

from gi.repository import Adw, Gtk, Gio, GLib
from .naming_patterns import NamingPatterns, FILENAME_PRESETS, FOLDER_PRESETS

@Gtk.Template(resource_path='/com/thecirculark/photoorganizer/ui/preferences.ui')
class PhotoOrganizerPreferences(Adw.PreferencesDialog):
    __gtype_name__ = 'PhotoOrganizerPreferences'

    # File name pattern widgets
    filename_combo = Gtk.Template.Child()
    filename_entry = Gtk.Template.Child()
    filename_preview = Gtk.Template.Child()

    # Folder pattern widgets
    folder_combo = Gtk.Template.Child()
    folder_entry = Gtk.Template.Child()
    folder_preview = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.naming_patterns = NamingPatterns()
        self.settings = Gio.Settings.new('com.thecirculark.photoorganizer')

        try:
            self._setup_filename_patterns()
            self._setup_folder_patterns()
            self._load_settings()
            self._update_previews()
        except Exception as e:
            print(f"Error initializing preferences: {e}")
            import traceback
            traceback.print_exc()
            # Try to set fallback values if widgets exist
            if hasattr(self, 'filename_entry') and self.filename_entry:
                self.filename_entry.set_text("YYYYMMDD-HHmmss-MS")
            if hasattr(self, 'folder_entry') and self.folder_entry:
                self.folder_entry.set_text("YYYY/MM-Month")

    @Gtk.Template.Callback()
    def on_filename_help_clicked(self, button):
        """Show filename pattern help dialog"""
        dialog = Adw.AlertDialog(
            heading="Filename Pattern Help",
            body=self.naming_patterns.get_pattern_help(is_filename=True),
            default_response="ok"
        )
        dialog.add_response("ok", "OK")
        dialog.present()

    @Gtk.Template.Callback()
    def on_folder_help_clicked(self, button):
        """Show folder pattern help dialog"""
        dialog = Adw.AlertDialog(
            heading="Folder Pattern Help",
            body=self.naming_patterns.get_pattern_help(is_filename=False),
            default_response="ok"
        )
        dialog.add_response("ok", "OK")
        dialog.present()

    def _setup_filename_patterns(self):
        """Setup filename pattern dropdown"""
        store = Gtk.ListStore(str, str)  # display name, pattern
        for preset_name, pattern in FILENAME_PRESETS.items():
            store.append([preset_name, pattern])

        self.filename_combo.set_model(store)
        renderer = Gtk.CellRendererText()
        self.filename_combo.pack_start(renderer, True)
        self.filename_combo.add_attribute(renderer, 'text', 0)

        self.filename_combo.connect('changed', self._on_filename_preset_changed)
        self.filename_entry.connect('changed', self._on_pattern_changed)

    def _setup_folder_patterns(self):
        """Setup folder pattern dropdown"""
        store = Gtk.ListStore(str, str)  # display name, pattern
        for preset_name, pattern in FOLDER_PRESETS.items():
            store.append([preset_name, pattern])

        self.folder_combo.set_model(store)
        renderer = Gtk.CellRendererText()
        self.folder_combo.pack_start(renderer, True)
        self.folder_combo.add_attribute(renderer, 'text', 0)

        self.folder_combo.connect('changed', self._on_folder_preset_changed)
        self.folder_entry.connect('changed', self._on_pattern_changed)

    def _load_settings(self):
        """Load saved settings"""
        filename_pattern = self.settings.get_string('filename-pattern')
        folder_pattern = self.settings.get_string('folder-pattern')

        # Remove file extensions from filename pattern (but keep it for folder pattern)
        clean_filename_pattern = self._clean_pattern(filename_pattern)

        self.filename_entry.set_text(clean_filename_pattern)
        self.folder_entry.set_text(folder_pattern)

        # Set combo selections
        self._set_combo_by_pattern(self.filename_combo, clean_filename_pattern)
        self._set_combo_by_pattern(self.folder_combo, folder_pattern)

    def _set_combo_by_pattern(self, combo, pattern):
        """Set combo selection based on pattern"""
        store = combo.get_model()
        for i, row in enumerate(store):
            if row[1] == pattern:
                combo.set_active(i)
                return
        combo.set_active(-1)  # Custom pattern

    def _on_filename_preset_changed(self, combo):
        """Handle filename preset selection"""
        active = combo.get_active()
        if active >= 0:
            store = combo.get_model()
            pattern = store[active][1]
            self.filename_entry.set_text(pattern)

    def _on_folder_preset_changed(self, combo):
        """Handle folder preset selection"""
        active = combo.get_active()
        if active >= 0:
            store = combo.get_model()
            pattern = store[active][1]
            self.folder_entry.set_text(pattern)

    def _on_pattern_changed(self, entry):
        """Handle manual pattern changes"""
        self._update_previews()
        self._save_settings()

    def _update_previews(self):
        """Update preview labels"""
        from datetime import datetime

        # Sample datetime for preview
        sample_dt = datetime(2025, 1, 15, 14, 30, 25)
        sample_ms = "123"

        filename_pattern = self.filename_entry.get_text()
        folder_pattern = self.folder_entry.get_text()

        try:
            # Always use the pattern from entry field and add .jpg extension for preview
            filename_preview = self.naming_patterns.generate_filename(
                sample_dt, sample_ms, ".jpg", filename_pattern
            )
            self.filename_preview.set_text(filename_preview)
        except Exception as e:
            self.filename_preview.set_text(f"Error: {str(e)}")

        try:
            folder_preview = self.naming_patterns.generate_folder_path(
                sample_dt, folder_pattern
            )
            self.folder_preview.set_text(folder_preview)
        except Exception as e:
            self.folder_preview.set_text(f"Error: {str(e)}")

    def _clean_pattern(self, pattern):
        """Remove file extensions from pattern"""
        if not pattern:
            return pattern

        # Remove common file extensions from the end
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        clean_pattern = pattern
        for ext in extensions:
            if clean_pattern.endswith(ext):
                clean_pattern = clean_pattern[:-len(ext)]
                break
        return clean_pattern

    def _save_settings(self):
        """Save settings to GSettings"""
        # Save clean pattern (without extension) for filename
        clean_filename_pattern = self._clean_pattern(self.filename_entry.get_text())
        self.settings.set_string('filename-pattern', clean_filename_pattern)
        self.settings.set_string('folder-pattern', self.folder_entry.get_text())


