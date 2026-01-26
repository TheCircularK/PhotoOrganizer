import argparse
import os
import shutil
from pathlib import Path
from exif import Image
from datetime import datetime
from gi.repository import Gio

def parse_datetime_with_milliseconds(img: Image):
    """
    Returns a datetime object and milliseconds string from EXIF image.
    Priority: datetime_original + subsec_time_original,
              datetime_digitized + subsec_time_digitized,
              datetime + subsec_time
    """
    dt_str = None
    ms_str = "000"

    def subsec_to_ms(subsec: str) -> str:
        return subsec.rjust(3, "0")[:3]

    if hasattr(img, "datetime_original") and img.datetime_original:
        dt_str = img.datetime_original
        if hasattr(img, "subsec_time_original") and img.subsec_time_original:
            ms_str = subsec_to_ms(img.subsec_time_original)
    elif hasattr(img, "datetime_digitized") and img.datetime_digitized:
        dt_str = img.datetime_digitized
        if hasattr(img, "subsec_time_digitized") and img.subsec_time_digitized:
            ms_str = subsec_to_ms(img.subsec_time_digitized)
    elif hasattr(img, "datetime") and img.datetime:
        dt_str = img.datetime
        if hasattr(img, "subsec_time") and img.subsec_time:
            ms_str = subsec_to_ms(img.subsec_time)

    if not dt_str:
        return None, None

    dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
    return dt, ms_str

def get_image_datetime_taken(image_path: Path):
    try:
        with open(image_path, "rb") as f:
            img = Image(f)
            if not img.has_exif:
                return None, None
            return parse_datetime_with_milliseconds(img)
    except Exception:
        return None, None

def build_filename(dt: datetime, milliseconds: str, ext: str, pattern: str = None):
    """Build filename using custom pattern or default"""
    if pattern is None:
        # Try to get pattern from settings, fall back to default
        try:
            settings = Gio.Settings.new('com.thecirculark.photoorganizer')
            pattern = settings.get_string('filename-pattern')
        except:
            pattern = "YYYYMMDD-HHmmss-MS"

    # Apply pattern - order matters! Replace longer tokens first
    replacements = {
        'YYYY': f"{dt.year:04d}",
        'MM': f"{dt.month:02d}",
        'DD': f"{dt.day:02d}",
        'HH': f"{dt.hour:02d}",
        'mm': f"{dt.minute:02d}",
        'ss': f"{dt.second:02d}",
        'MS': milliseconds,
        'YY': f"{dt.year:02d}",
        'ext': ext,
    }

    result = pattern
    # Sort tokens by length (longest first) to prevent partial replacements
    for token in sorted(replacements.keys(), key=len, reverse=True):
        result = result.replace(token, replacements[token])

    # If pattern doesn't include ext token, append the extension
    if 'ext' not in pattern and ext:
        result += ext

    return result

def build_folder_path(dt: datetime, pattern: str = None) -> str:
    """Build folder path using custom pattern or default"""
    if pattern is None:
        # Try to get pattern from settings, fall back to default
        try:
            settings = Gio.Settings.new('com.thecirculark.photoorganizer')
            pattern = settings.get_string('folder-pattern')
        except:
            pattern = "YYYY/MM-Month"

    # Apply pattern - order matters! Replace longer tokens first
    replacements = {
        'Month': dt.strftime('%B'),
        'YYYY': f"{dt.year:04d}",
        'MM': f"{dt.month:02d}",
        'DD': f"{dt.day:02d}",
        'Mon': dt.strftime('%b'),
        'YY': f"{dt.year:02d}",
    }

    result = pattern
    # Sort tokens by length (longest first) to prevent partial replacements
    for token in sorted(replacements.keys(), key=len, reverse=True):
        result = result.replace(token, replacements[token])

    return result

def resolve_collision(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    counter = 1

    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def handle_files(source_folder: Path, rename_enabled: bool, organize_enabled: bool, organize_dir: Path, dry_run: bool, logger=print):
    for root, _, files in os.walk(source_folder, topdown=True):
        for name in files:
            full_image_path = Path(root) / name
            action_description = ""

            dt, ms = get_image_datetime_taken(full_image_path)
            if not dt:
                action_description = f"Skipping (no EXIF datetime): {full_image_path}"
                logger(action_description)
                continue

            if rename_enabled:
                target_name = build_filename(dt, ms, full_image_path.suffix.lower())
            else:
                target_name = full_image_path.name

            if organize_enabled:
                folder_path = build_folder_path(dt)
                target_dir = organize_dir / folder_path
                target_path = target_dir / target_name
            else:
                target_dir = full_image_path.parent
                target_path = target_dir / target_name

            if dry_run:
                final_path = resolve_collision(target_path)
                action_description = f"[DRY-RUN] Would move: {full_image_path} -> {final_path}"
            else:
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    final_path = resolve_collision(target_path)
                    shutil.move(str(full_image_path), str(final_path))
                    action_description = f"Moved: {full_image_path} -> {final_path}"
                except Exception as e:
                    action_description = f"Skipping {full_image_path}: {e}"

            logger(action_description)


