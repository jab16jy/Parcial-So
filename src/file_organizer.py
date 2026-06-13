"""File Organizer module.

Categorise files in a user-specified folder by extension into
Documents, Images, Videos, and Others subdirectories.
"""

import shutil
from pathlib import Path

from rich.prompt import Prompt
from rich.progress import Progress

from utils.helpers import console, error_handler, log_event

# Extension → category mapping
EXTENSION_MAP: dict[str, str] = {
    # Documents
    ".pdf": "Documents/PDF",
    ".doc": "Documents/WORD",
    ".docx": "Documents/WORD",
    ".xls": "Documents/EXCEL",
    ".xlsx": "Documents/EXCEL",
    ".csv": "Documents/EXCEL",
    # Images
    ".jpg": "Images/JPG",
    ".jpeg": "Images/JPG",
    ".png": "Images/Others",
    ".gif": "Images/Others",
    ".bmp": "Images/Others",
    ".webp": "Images/Others",
    # Videos
    ".mp4": "Videos/MP4",
    ".mov": "Videos/MP4",
    ".avi": "Videos/AVI",
    ".mkv": "Videos/AVI",
}


def get_category(ext: str) -> str:
    """Return the target subfolder name for a given file extension.

    Args:
        ext: File extension including the dot (e.g. '.pdf').

    Returns:
        Category folder name, e.g. 'Documents/PDF'.
    """
    return EXTENSION_MAP.get(ext.lower(), "Others")


def _resolve_dest(dest_dir: Path, filename: str) -> Path:
    """Return a unique path inside *dest_dir*, appending a numeric suffix
    if a file with the same name already exists.

    Args:
        dest_dir: Target directory.
        filename: Original file name.

    Returns:
        A non-colliding Path.
    """
    dest = dest_dir / filename
    if not dest.exists():
        return dest

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


@error_handler
def organize_folder(folder_path: str | Path) -> dict:
    """Scan *folder_path*, move every file into its category subfolder.

    Args:
        folder_path: Path to the directory to organise.

    Returns:
        Summary dict with keys: files_moved, by_category.
    """
    folder = Path(folder_path)

    if not folder.exists():
        console.print(f"[error]Source directory not found: {folder}[/error]")
        log_event("organize_folder", {"folder": str(folder), "status": "not_found"})
        return {"files_moved": 0, "by_category": {}}

    if not folder.is_dir():
        console.print(f"[error]Not a directory: {folder}[/error]")
        return {"files_moved": 0, "by_category": {}}

    # Collect only regular files (skip subdirectories)
    files = [f for f in folder.iterdir() if f.is_file()]

    if not files:
        console.print("[warning]No files to organize[/warning]")
        log_event("organize_folder", {"folder": str(folder), "files_moved": 0})
        return {"files_moved": 0, "by_category": {}}

    # Group files by category
    grouped: dict[str, list[Path]] = {}
    for f in files:
        cat = get_category(f.suffix)
        grouped.setdefault(cat, []).append(f)

    files_moved = 0
    by_category: dict[str, int] = {}

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Organizing files...", total=len(files)
        )

        for category, cat_files in grouped.items():
            target_dir = folder / category
            target_dir.mkdir(parents=True, exist_ok=True)

            for src_file in cat_files:
                dest = _resolve_dest(target_dir, src_file.name)
                try:
                    shutil.move(str(src_file), str(dest))
                    files_moved += 1
                    by_category[category] = by_category.get(category, 0) + 1
                except PermissionError:
                    console.print(
                        f"[warning]Permission denied: {src_file.name} — skipping[/warning]"
                    )
                except OSError as e:
                    console.print(
                        f"[warning]Could not move {src_file.name}: {e} — skipping[/warning]"
                    )

                progress.advance(task)

    console.print(f"[success]Organized {files_moved} files[/success]")
    for cat, count in sorted(by_category.items()):
        console.print(f"  [info]{cat}:[/info] {count} files")

    log_event("organize_folder", {
        "folder": str(folder),
        "files_moved": files_moved,
        "by_category": by_category,
    })

    return {"files_moved": files_moved, "by_category": by_category}
