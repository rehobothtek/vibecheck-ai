import csv, json
from pathlib import Path
from .models import validate_review

def import_reviews(path):
    """Return accepted reviews and visible per-record rejections; never partially mutates state."""
    path = Path(path)
    try:
        if path.suffix.lower() == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, list): raise ValueError("JSON root must be a list")
        elif path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle: raw = list(csv.DictReader(handle))
        else: raise ValueError("input must be .csv or .json")
    except (UnicodeDecodeError, json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"could not read dataset: {exc}") from exc
    accepted, rejected, ids = [], [], set()
    for index, record in enumerate(raw, 1):
        try:
            review = validate_review(record)
            if review.id in ids: raise ValueError("duplicate id")
            ids.add(review.id); accepted.append(review)
        except ValueError as exc: rejected.append({"row": index, "error": str(exc)})
    return accepted, rejected
