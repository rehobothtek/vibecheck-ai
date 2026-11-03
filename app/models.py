from dataclasses import dataclass, asdict
from datetime import date
from hashlib import sha256

SENTIMENTS = {"positive", "negative", "neutral", "mixed"}
TOPICS = {"sound", "food", "queue", "staff", "pricing", "safety", "venue", "other"}
SCHEMA_VERSION = "1.0"

@dataclass(frozen=True)
class Review:
    id: str
    event: str
    text: str
    created_at: str

    @property
    def source_hash(self):
        return sha256(self.text.encode("utf-8")).hexdigest()

    def to_dict(self): return asdict(self)

def validate_review(raw):
    if not isinstance(raw, dict): raise ValueError("record must be an object")
    values = {k: str(raw.get(k, "")).strip() for k in ("id", "event", "text", "created_at")}
    if not values["id"]: raise ValueError("missing id")
    if not values["event"]: raise ValueError("missing event")
    if not 5 <= len(values["text"]) <= 500: raise ValueError("text must be 5–500 characters")
    try: date.fromisoformat(values["created_at"])
    except ValueError: raise ValueError("created_at must be YYYY-MM-DD")
    return Review(**values)
