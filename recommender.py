"""Hybrid occasion-based recommender: curated occasion expansion + TF-IDF cosine + keyword boost."""
import json, re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from occasions import OCCASIONS, ALIASES, GENERIC

try:  # optional semantic layer (pip install sentence-transformers faiss-cpu)
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_SEMANTIC = True
except Exception:
    HAS_SEMANTIC = False

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Human-readable category labels inferred from text (the catalog only holds opaque category IDs).
CATEGORY_RULES = [
    ("Flowers", ["flower", "bouquet", "lilies", "tulips", "rose", "marigold", "forever rose"]),
    ("Chocolates & Food", ["chocolate", "dry fruits", "snacks", "tea", "infusions"]),
    ("Fragrance & Candles", ["perfume", "candle", "soap", "body oil"]),
    ("Jewellery", ["necklace", "bracelet", "earrings", "jewel", "choker"]),
    ("Watches & Pens", ["watch", "pen"]),
    ("Apparel", ["shirt", "tshirt", "t shirt", "pants", "jeans", "cargo", "kurti", "saree", "suit", "office wear"]),
    ("Wellness & Eco", ["self-care", "wellness", "health"]),
    ("Toys & Kids", ["toy", "plush", "teddy", "slime", "xylophone", "guitar", "drums", "diy", "craft kits", "coloring kits"]),
    ("Gift Cards & Accessories", ["gift card", "greeting", "wax seal", "gift box", "wrapping", "gift sets"]),
    ("Hampers & Celebrations", ["hamper", "engagement", "housewarming", "baby shower"]),
    ("Wellness & Eco", ["skincare", "bath", "bamboo", "recycled", "upcycled", "planter", "natural fiber", "wellness", "self-care"]),
    ("Personalized & Couples", ["couple", "personalized", "star map", "letters", "mugs", "touch"]),
]

THEMED = ["diwali", "holi", "christmas", "engagement", "housewarming", "baby shower", "valentine"]
_ws = re.compile(r"\s+")


def _norm(text):
    return _ws.sub(" ", re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())).strip()


def normalize_payload(p: dict) -> dict:
    """Map either spec-style or catalog-style fields onto a common shape."""
    title = p.get("title") or p.get("name") or ""
    desc = p.get("description", "") or ""
    short = p.get("shortDescription", "") or ""
    image = p.get("mainImage")
    files = p.get("files") or ([image] if image else [])
    return {
        "product_id": p.get("product_id") or p.get("productId") or p.get("id"),
        "vendor_id": p.get("vendor_id") or p.get("vendorId") or p.get("shopId"),
        "vendor_category": p.get("vendor_category") or p.get("categoryId"),
        "vendor_category_desc": p.get("vendor_category_desc") or "",
        "title": title.strip(),
        "description": (desc or short).replace("\r\n", " ").strip(),
        "short_description": short.strip(),
        "brand": p.get("brand", "") or "",
        "files": files,
        "price": p.get("price"),
        "discount": p.get("discountPercentage"),
        "active": p.get("status", "ACTIVE") == "ACTIVE" and p.get("isApproved", True) and not p.get("deletedAt"),
    }


def infer_category(item) -> str:
    text = _norm(f"{item['title']} {item['vendor_category_desc']} {item['short_description']}")
    padded = f" {text} "
    for label, kws in CATEGORY_RULES:
        # whole-word match (so "pen" does not match "open")
        if any(re.search(rf"\b{re.escape(_norm(k))}s?\b", padded) for k in kws):
            return label
    return item["vendor_category_desc"] or "General Gifts"


def resolve_occasion(query: str):
    """Return (canonical occasion or None, expansion terms)."""
    q = _norm(query)
    if q in OCCASIONS:
        return q, OCCASIONS[q]
    if q in ALIASES:
        k = ALIASES[q]
        return k, OCCASIONS[k]
    for alias, k in ALIASES.items():           # substring match e.g. "diwali party"
        if _norm(alias) in q:
            return k, OCCASIONS[k]
    for k in OCCASIONS:
        if k in q:
            return k, OCCASIONS[k]
    return None, [w for w in q.split() if len(w) > 2]


class Recommender:
    def __init__(self, path: Path, only_active: bool = True):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        items = [normalize_payload(p) for p in raw]
        self.items = [i for i in items if i["active"]] if only_active else items
        for i in self.items:
            i["category"] = infer_category(i)
            i["_text"] = _norm(f"{i['title']} {i['title']} {i['brand']} {i['category']} {i['short_description']} {i['description']}")
            i["_title"] = _norm(i["title"])
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        self.matrix = self.vec.fit_transform([i["_text"] for i in self.items])
        self.semantic = False
        if HAS_SEMANTIC:
            try:
                self.model = SentenceTransformer(MODEL_NAME)
                docs = [f"{i['title']}. {i['category']}. {i['description']}" for i in self.items]
                emb = self.model.encode(docs, normalize_embeddings=True, show_progress_bar=False).astype("float32")
                self.index = faiss.IndexFlatIP(emb.shape[1])   # inner product on unit vectors = cosine
                self.index.add(emb)
                self.semantic = True
            except Exception as e:  # model download failed / offline -> TF-IDF only
                print(f"[recommender] semantic layer disabled: {e}")

    def recommend(self, query: str, limit: int = 12):
        query = (query or "").strip()
        if not query:
            return {"occasion": None, "matched_as": None, "results": []}
        canon, terms = resolve_occasion(query)
        # Query text: occasion name weighted by repetition + expansion terms.
        qtext = _norm(" ".join([query] * 3 + terms))
        sims = cosine_similarity(self.vec.transform([qtext]), self.matrix).ravel()

        sem = np.zeros(len(self.items), dtype="float32")
        if self.semantic:
            q = f"gift ideas for {query}: " + ", ".join(terms[:10])
            qv = self.model.encode([q], normalize_embeddings=True).astype("float32")
            scores, ids = self.index.search(qv, len(self.items))
            sem[ids[0]] = scores[0]
            sem = np.clip((sem - sem.min()) / (np.ptp(sem) + 1e-9), 0, 1)  # min-max to 0..1

        scored = []
        for idx, item in enumerate(self.items):
            # Keyword score: title hits count more than description hits.
            hits_title = [t for t in terms if _norm(t) in item["_title"]]
            hits_text = [t for t in terms if _norm(t) in item["_text"]]
            kw = min(1.0, 0.25 * len(hits_title) + 0.08 * len(hits_text))
            # Direct mention of the occasion itself (e.g. "Diwali Luxury Gift Hampers") is a strong signal.
            direct = 0.5 if _norm(query) in item["_text"] else 0.0
            if self.semantic:   # hybrid: semantic + lexical + keyword
                score = 0.45 * sem[idx] + 0.25 * sims[idx] + 0.25 * kw + direct * 0.3
            else:
                score = 0.55 * sims[idx] + 0.35 * kw + direct * 0.4
            # Penalise products explicitly themed for a *different* occasion (e.g. Holi hamper for Diwali).
            if canon and any(o in item["_title"] and o != canon and o not in canon for o in THEMED):
                score *= 0.5
            if not canon and not hits_text:      # unknown occasion with zero lexical overlap -> no match
                continue
            if score > (0.2 if self.semantic else 0.08):
                scored.append((score, idx, sorted(set(hits_title + hits_text))[:4]))
        scored.sort(reverse=True)
        top = scored[0][0] if scored else 1
        out = []
        for score, idx, why in scored[:limit]:
            it = self.items[idx]
            out.append({
                "product_id": it["product_id"], "title": it["title"], "category": it["category"],
                "brand": it["brand"], "description": it["description"], "image": (it["files"] or [None])[0],
                "price": it["price"], "discount": it["discount"],
                "score": round(float(score / top), 3), "matched_terms": why,
            })
        return {"occasion": query, "matched_as": canon, "results": out}
