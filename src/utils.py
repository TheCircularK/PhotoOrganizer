import argparse
import os
import shutil
from pathlib import Path
from exif import Image
from datetime import datetime

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

def build_filename(dt: datetime, milliseconds: str, ext: str):
    return f"{dt.strftime('%Y%m%d%H%M%S')}-{milliseconds}{ext}"

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
                target_dir = organize_dir / str(dt.year) / f"{dt.year}-{dt.month:02d}"
                target_path = target_dir / target_name
            else:
                target_dir = full_image_path.parent
                target_path = target_dir / target_name

            if dry_run:
                action_description = f"[DRY-RUN] Would move: {full_image_path} -> {target_path}"
            else:
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(full_image_path), str(target_path))
                    action_description = f"Moved: {full_image_path} -> {target_path}"
                except Exception as e:
                    action_description = f"Skipping {full_image_path}: {e}"

            logger(action_description)

