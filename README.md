# Occasion-Based Product Recommender

Enter an occasion (Birthday, Diwali, Wedding, Valentine's Day, Office Party, ...) and get a ranked grid of matching products from the catalog, shown directly below the input.

## Setup
```bash
pip install -r requirements.txt
python -m uvicorn main:app
# open http://127.0.0.1:8000
```
Catalog lives in `data/products.json`.

## API
`GET /api/recommend?occasion=Diwali&limit=12` returns `{occasion, matched_as, results:[{product_id, title, category, description, image, price, score, matched_terms}]}`.
`GET /api/occasions` lists the known occasions (shown as quick chips in the UI).

## Approach (hybrid)
If `sentence-transformers` + `faiss-cpu` are installed, the engine adds a **semantic layer**: products are embedded with `all-MiniLM-L6-v2` and searched through a FAISS cosine index, then fused with TF-IDF and keyword scores. If they are missing (or the model can't download), it silently falls back to the lexical pipeline below.

1. **Normalisation** - accepts both the assignment's payload fields (`product_id`, `title`, `files`, ...) and the catalog's fields (`id`, `name`, `mainImage`, ...). Only ACTIVE, approved, non-deleted products are indexed (104 of 110).
2. **Occasion expansion** - `occasions.py` maps each occasion (plus aliases like "bday", "Valentine's", "Deepavali") to the vocabulary people associate with it. Unknown occasions fall back to the user's own words.
3. **Scoring** = 0.55 x TF-IDF cosine (uni+bigrams, title double-weighted) + 0.35 x keyword score (title hits > description hits) + a boost when the occasion is named directly in the product. Products themed for a *different* occasion (e.g. a Holi hamper for "Diwali") are down-weighted. Unknown occasions with no lexical overlap return nothing, which triggers the UI's empty state.
4. **Category** - the catalog only has opaque category IDs, so a human-readable label is inferred from title/description with whole-word rules.

Why this approach: the catalog is small (~100 items), so TF-IDF is fast, explainable (the UI shows matched terms) and needs no GPU or API key. The natural upgrade is sentence-transformer embeddings with FAISS/Qdrant in place of TF-IDF, behind the same `Recommender.recommend` interface.

## Libraries
FastAPI, Uvicorn, scikit-learn, NumPy.

## AI usage
This project was built with assistance from Claude (Anthropic).

## Note on images
The catalog's image host (`s3aws.emilo.in`) currently returns `NoSuchBucket`, so product images cannot load. The UI reads `mainImage`/`files` and shows them when reachable; otherwise it shows a category placeholder.
