# naming_patterns.py
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

from datetime import datetime
from pathlib import Path

# Filename pattern presets
FILENAME_PRESETS = {
    "YYYYMMDD-HHmmss-MS": "YYYYMMDD-HHmmss-MS",
    "YYYYMMDDHHmmss_MS": "YYYYMMDDHHmmss_MS",
    "YYYY-MM-DD_HH.mm.ss": "YYYY-MM-DD_HH.mm.ss",
    "YYYYMMDD_HHmmss": "YYYYMMDD_HHmmss",
    "IMG_YYYYMMDD_HHmmss": "IMG_YYYYMMDD_HHmmss",
    "Photo_YYYY-MM-DD": "Photo_YYYY-MM-DD",
}

# Folder pattern presets
FOLDER_PRESETS = {
    "YYYY/MM": "YYYY/MM",
    "YYYY/MM-DD": "YYYY/MM-DD",
    "YYYY/MM-Month": "YYYY/MM-Month",
    "YYYY/MM Month": "YYYY/MM Month",
    "YYYY/Month": "YYYY/Month",
    "YYYY/MM-Month YYYY": "YYYY/MM-Month YYYY",
    "Photos/YYYY/MM": "Photos/YYYY/MM",
}

class NamingPatterns:
    """Handles custom naming patterns for files and folders"""

    def __init__(self):
        self.filename_pattern = "YYYYMMDD-HHmmss-MS"
        self.folder_pattern = "YYYY/MM-Month"

    def generate_filename(self, dt: datetime, milliseconds: str, extension: str, pattern: str = None) -> str:
        """
        Generate filename based on pattern

        Available tokens:
        - YYYY: 4-digit year
        - YY: 2-digit year
        - MM: 2-digit month
        - DD: 2-digit day
        - HH: 2-digit hour (24-hour)
        - mm: 2-digit minute
        - ss: 2-digit second
        - MS: milliseconds (3 digits)
        - ext: file extension
        """
        if pattern is None:
            pattern = self.filename_pattern

        # Create replacement mapping
        replacements = {
            'YYYY': f"{dt.year:04d}",
            'MM': f"{dt.month:02d}",
            'DD': f"{dt.day:02d}",
            'HH': f"{dt.hour:02d}",
            'mm': f"{dt.minute:02d}",
            'ss': f"{dt.second:02d}",
            'MS': milliseconds,
            'YY': f"{dt.year:02d}",
            'ext': extension,
        }

        # Apply replacements - sort tokens by length (longest first) to prevent partial replacements
        result = pattern
        for token in sorted(replacements.keys(), key=len, reverse=True):
            result = result.replace(token, replacements[token])

        # If pattern doesn't include ext token, append the extension
        if 'ext' not in pattern and extension:
            result += extension

        return result

    def generate_folder_path(self, dt: datetime, pattern: str = None) -> str:
        """
        Generate folder path based on pattern

        Available tokens:
        - YYYY: 4-digit year
        - YY: 2-digit year
        - MM: 2-digit month
        - DD: 2-digit day
        - Month: Full month name (January, February, etc.)
        - Mon: 3-letter month abbreviation (Jan, Feb, etc.)
        """
        if pattern is None:
            pattern = self.folder_pattern

        # Create replacement mapping - order matters! Replace longer tokens first
        replacements = {
            'Month': dt.strftime('%B'),
            'YYYY': f"{dt.year:04d}",
            'MM': f"{dt.month:02d}",
            'DD': f"{dt.day:02d}",
            'Mon': dt.strftime('%b'),
            'YY': f"{dt.year:02d}",
        }

        # Apply replacements - sort tokens by length (longest first) to prevent partial replacements
        result = pattern
        for token in sorted(replacements.keys(), key=len, reverse=True):
            result = result.replace(token, replacements[token])

        return result

    def validate_pattern(self, pattern: str, is_filename: bool = True) -> tuple[bool, str]:
        """
        Validate a pattern string

        Returns:
            tuple: (is_valid, error_message)
        """
        if not pattern or not pattern.strip():
            return False, "Pattern cannot be empty"

        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*'] if is_filename else ['<', '>', ':', '"', '|', '?', '*', '/']

        for char in invalid_chars:
            if char in pattern:
                return False, f"Pattern contains invalid character: {char}"

        # Check for valid tokens
        if is_filename:
            valid_tokens = ['YYYY', 'YY', 'MM', 'DD', 'HH', 'mm', 'ss', 'MS', 'ext']
        else:
            valid_tokens = ['YYYY', 'YY', 'MM', 'DD', 'Month', 'Mon']

        # Extract tokens from pattern (handle both uppercase and lowercase)
        import re
        tokens = re.findall(r'[A-Za-z]+', pattern)

        invalid_tokens = [token for token in tokens if token not in valid_tokens]
        if invalid_tokens:
            return False, f"Invalid tokens: {', '.join(invalid_tokens)}"

        return True, ""

    def get_filename_pattern_help(self) -> str:
        return """Available filename tokens:
• YYYY - 4-digit year (2025)
• YY - 2-digit year (25)
• MM - 2-digit month (01-12)
• DD - 2-digit day (01-31)
• HH - 2-digit hour (00-23)
• mm - 2-digit minute (00-59)
• ss - 2-digit second (00-59)
• MS - milliseconds (000-999)
• ext - file extension (.jpg)

Examples:
• YYYYMMDD-HHmmss-MS → 20250115-143025-123.jpg
• YYYY-MM-DD_HH.mm.ss → 2025-01-15_14.30.25.jpg
• IMG_YYYYMMDD_HHmmss → IMG_20250115_143025.jpg"""

    def get_directory_pattern_help(self) -> str:
        """Get help text for pattern tokens"""

        return """Available folder tokens:
• YYYY - 4-digit year (2025)
• YY - 2-digit year (25)
• MM - 2-digit month (01-12)
• DD - 2-digit day (01-31)
• Month - Full month name (January)
• Mon - 3-letter month (Jan)

Examples:
• YYYY/MM → 2025/01
• YYYY/MM-Month → 2025/01-January
• YYYY/MM Month → 2025/01 January
• Photos/YYYY/MM → Photos/2025/01"""

