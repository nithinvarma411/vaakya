from fastapi import FastAPI, HTTPException
from src.app.app_launcher.models import OpenRequest, OpenResponse
from src.app.app_launcher.scanner import apps, folders
from sentence_transformers import SentenceTransformer, util
import numpy as np
import os
import json
import re

app = FastAPI(title="System Scanner API")

# -----------------------------
# Config
# -----------------------------
CACHE_FILE = "src/app/app_launcher/apps_cache.json"
SEMANTIC_THRESHOLD = 0.30   # tuned for recall; raise if you get false positives
WEIGHTS = {
    "semantic": 0.65,
    "jaccard": 0.20,
    "substring": 0.10,
    "exact": 0.05
}

# -----------------------------
# Helpers
# -----------------------------
def normalize_name(name: str) -> str:
    """Lowercase + collapse multiple spaces."""
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    return name

def tokens_of(text: str):
    """Return word tokens for simple Jaccard/overlap calculations."""
    return set(re.findall(r"\w+", normalize_name(text)))

def find_sensible_exe_in_dir(dirpath: str, prefer_name: str = None):
    """Search immediate dir for a sensible .exe. Prefer matches that contain prefer_name tokens."""
    if not os.path.isdir(dirpath):
        return None
    try:
        files = [f for f in os.listdir(dirpath) if f.lower().endswith(".exe")]
    except Exception:
        return None
    if not files:
        return None

    # filter out installers/uninstallers
    files = [f for f in files if not re.search(r"(uninstall|setup|update|installer)", f, re.I)]
    if not files:
        return None

    prefer_tokens = tokens_of(prefer_name) if prefer_name else set()
    # Score files by token overlap with prefer_name and pick best
    best = None
    best_score = -1
    for f in files:
        fname = os.path.splitext(f)[0].lower()
        f_tokens = set(re.findall(r"\w+", fname))
        score = len(f_tokens & prefer_tokens)
        if score > best_score:
            best = f
            best_score = score

    return os.path.join(dirpath, best if best else files[0])

# -----------------------------
# Load apps (with cache)
# -----------------------------
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            installed_apps = json.load(f)
    except json.JSONDecodeError:
        installed_apps = apps.get_installed_apps()
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(installed_apps, f, indent=2)
else:
    installed_apps = apps.get_installed_apps()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(installed_apps, f, indent=2)

# -----------------------------
# Load user folders
# -----------------------------
user_folders = folders.get_user_folders()

# -----------------------------
# Build items + alias labels
# -----------------------------
items = []                # each item: dict{name, path, type, tokens, exe_basename}
candidate_labels = []     # list of alias strings
candidate_to_item = []    # map index -> item_index

# Apps: installed_apps maps shortcut_name -> exe_path
for name, path in installed_apps.items():
    norm_name = normalize_name(name)
    basename = os.path.basename(path) if path else ""
    exe_basename = os.path.splitext(basename)[0] if basename else ""
    item = {
        "name": norm_name,
        "path": path,
        "type": "app",
        "tokens": tokens_of(norm_name),
        "exe_basename": normalize_name(exe_basename)
    }
    item_idx = len(items)
    items.append(item)

    # create aliases for semantic matching
    aliases = set()
    # full name + exe basename
    aliases.add(norm_name)
    if exe_basename:
        aliases.add(normalize_name(exe_basename))
    # no-space versions
    aliases.add(norm_name.replace(" ", ""))
    if exe_basename:
        aliases.add(normalize_name(exe_basename).replace(" ", ""))
    # individual tokens (helps with short user inputs)
    for t in item["tokens"]:
        if len(t) > 1:
            aliases.add(t)
            aliases.add(t.replace(" ", ""))  # no-space token

    for a in aliases:
        candidate_labels.append(a)
        candidate_to_item.append(item_idx)


# Folders + immediate subfolders
for main_name, info in user_folders.items():
    main_norm = normalize_name(main_name)
    item = {
        "name": main_norm,
        "path": info["path"],
        "type": "folder",
        "tokens": tokens_of(main_norm),
        "exe_basename": ""
    }
    main_idx = len(items)
    items.append(item)

    aliases = set([main_norm, main_norm.replace(" ", "")])
    for t in item["tokens"]:
        if len(t) > 1:
            aliases.add(t)

    for a in aliases:
        candidate_labels.append(a)
        candidate_to_item.append(main_idx)

    # immediate child folders (we add them as separate items so user can open them)
    for sub in info.get("folders", []):
        nsub = normalize_name(sub)
        item_idx = len(items)
        items.append({
            "name": nsub,
            "path": os.path.join(info["path"], sub),
            "type": "folder",
            "tokens": tokens_of(nsub),
            "exe_basename": ""
        })
        aliases = set([nsub, nsub.replace(" ", "")])
        for t in tokens_of(nsub):
            if len(t) > 1:
                aliases.add(t)
        for a in aliases:
            candidate_labels.append(a)
            candidate_to_item.append(item_idx)

# -----------------------------
# Load model & compute embeddings for aliases
# -----------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# compute embeddings for candidate_labels (one vector per alias)
candidate_embeddings = model.encode(candidate_labels, convert_to_tensor=True, normalize_embeddings=True)

# -----------------------------
# Endpoint: open
# -----------------------------
@app.post("/open", response_model=OpenResponse)
def get_path(request: OpenRequest):
    query_raw = request.text or ""
    query = normalize_name(query_raw)
    if not query:
        raise HTTPException(status_code=400, detail="Empty request")

    # semantic similarity to all candidate aliases
    q_emb = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(q_emb, candidate_embeddings)[0].cpu().numpy()  # shape = (num_candidates,)

    # convert candidate scores -> per-item max semantic score
    n_items = len(items)
    sem_max = np.full(n_items, -1.0, dtype=float)
    for i, cand_score in enumerate(sims):
        item_idx = candidate_to_item[i]
        if cand_score > sem_max[item_idx]:
            sem_max[item_idx] = float(cand_score)

    # surface signals
    q_tokens = tokens_of(query)
    combined_scores = []
    for idx, item in enumerate(items):
        sem_score = float(sem_max[idx]) if sem_max[idx] >= 0 else 0.0
        # jaccard
        union = len(item["tokens"] | q_tokens)
        jaccard = (len(item["tokens"] & q_tokens) / union) if union > 0 else 0.0
        # substring/exact
        substring = 1.0 if (query in item["name"] or query in item.get("exe_basename", "")) else 0.0
        exact = 1.0 if (query == item["name"] or query == item.get("exe_basename", "")) else 0.0

        score = (
            WEIGHTS["semantic"] * sem_score +
            WEIGHTS["jaccard"] * jaccard +
            WEIGHTS["substring"] * substring +
            WEIGHTS["exact"] * exact
        )
        combined_scores.append(score)

    best_idx = int(np.argmax(combined_scores))
    best_score = float(combined_scores[best_idx])
    best_item = items[best_idx]

    if best_score < SEMANTIC_THRESHOLD:
        raise HTTPException(status_code=404, detail="No matching app or folder found")

    best_path = best_item["path"]

    # Special-case: prefer code.exe if query mentions code
    if "code" in query or "visual studio" in query:
        for it in items:
            if it["type"] == "app" and it["path"].lower().endswith("code.exe"):
                best_item = it
                best_path = it["path"]
                break

    # Try to open app or folder
    try:
        if best_item["type"] == "app":
            # if path is file and exe -> open directly
            if os.path.isfile(best_path) and best_path.lower().endswith(".exe"):
                os.startfile(best_path)
            else:
                # sometimes scanner returns a folder or .lnk target missing; try to find exe
                if os.path.isdir(best_path):
                    exe_try = find_sensible_exe_in_dir(best_path, prefer_name=best_item.get("exe_basename") or best_item["name"])
                    if exe_try:
                        os.startfile(exe_try)
                        best_path = exe_try
                    else:
                        # fallback: open folder
                        os.startfile(best_path)
                else:
                    raise HTTPException(status_code=500, detail="App path invalid")
        else:
            # folder: open
            os.startfile(best_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open: {str(e)}")

    return OpenResponse(name=best_item["name"], path=best_path, type=best_item["type"])


# -----------------------------
# Endpoint: list_system
# -----------------------------
@app.get("/list_system")
def list_system():
    return {
        "apps": installed_apps,
        "folders": user_folders,
    }
