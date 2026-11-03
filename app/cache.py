import json
from pathlib import Path
from .models import SCHEMA_VERSION

def load_cache(path):
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}

def save_cache(path, cache): Path(path).parent.mkdir(parents=True, exist_ok=True); Path(path).write_text(json.dumps(cache, indent=2), encoding="utf-8")
def valid_cached(cache, review, model):
    item = cache.get(review.id)
    return item if item and item.get("source_hash") == review.source_hash and item.get("model") == model and item.get("schema_version") == SCHEMA_VERSION else None
