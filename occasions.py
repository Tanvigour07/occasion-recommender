"""Curated occasion knowledge base.

Each occasion maps to weighted keywords describing what people typically gift.
Unknown occasions fall back to the raw query terms (plus a generic gifting vocabulary)
so the system still degrades gracefully.
"""

OCCASIONS = {
    "birthday": ["birthday", "chocolate", "cake", "teddy", "plushies", "perfume", "watch", "personalized",
                 "toys", "card", "flower", "bouquet", "gift box", "gift set", "bundle"],
    "wedding": ["wedding", "engagement", "couple", "bride", "groom", "luxury", "hamper", "jewellery", "necklace",
                "bracelet", "earrings", "saree", "suit", "gift set", "bundle", "elegant", "festive", "perfume"],
    "anniversary": ["anniversary", "couple", "romantic", "love", "rose", "flower", "bouquet", "chocolate", "perfume",
                    "forever", "personalized", "star map", "story book", "watch", "jewellery", "candle"],
    "valentine": ["valentine", "romantic", "love", "couple", "rose", "flower", "bouquet", "chocolate", "forever rose",
                  "perfume", "candle", "teddy", "bracelet", "letters", "heart", "personalized", "star map"],
    "diwali": ["diwali", "festive", "festival", "hamper", "dry fruits", "luxury", "candle", "diya", "sweets", "jewellery",
               "necklace", "earrings", "suit", "kurti", "saree", "ethnic", "traditional", "gift box", "decor", "marigold"],
    "holi": ["holi", "festival of colors", "festive", "hamper", "dry fruits", "colors", "snacks", "luxury", "ethnic", "kurti"],
    "christmas": ["christmas", "festive", "hamper", "dry fruits", "luxury", "candle", "teddy", "gift box", "card",
                  "seasonal", "chocolate", "wrapping", "plushies"],
    "office party": ["office", "corporate", "professional", "pen", "notebook", "journal", "kit", "wellness", "fitness",
                     "watch", "executive", "self-care", "team", "employee", "desk", "shirt", "gift set", "hamper"],
    "corporate": ["corporate", "office", "employee", "pen", "executive", "wellness", "kit", "watch", "notebook",
                  "professional", "gift set", "hamper", "fitness"],
    "housewarming": ["housewarming", "home", "decor", "plant", "planter", "candle", "bamboo", "natural", "jute",
                     "new home", "bundle", "hamper", "indoor", "sustainable"],
    "baby shower": ["baby", "newborn", "shower", "soft", "plush", "teddy", "toys", "gentle", "keepsake", "kids"],
    "kids": ["kids", "children", "toy", "plush", "teddy", "kit", "diy", "slime", "paint", "music", "xylophone", "fun"],
    "mothers day": ["mother", "mom", "self-care", "skincare", "organic", "flower", "bouquet", "perfume", "jewellery",
                    "necklace", "tea", "herbal", "candle", "bath", "wellness", "saree", "kurti"],
    "fathers day": ["father", "dad", "watch", "pen", "executive", "wellness", "fitness", "shirt", "polo", "wallet",
                    "chocolate", "snacks", "personalized"],
    "raksha bandhan": ["rakhi", "brother", "sister", "sweets", "dry fruits", "chocolate", "hamper", "festive",
                       "bracelet", "gift box", "traditional", "watch"],
    "graduation": ["graduation", "achievement", "pen", "notebook", "journal", "watch", "personalized", "card",
                   "executive", "keepsake", "congratulations"],
    "get well": ["wellness", "self-care", "herbal", "tea", "flower", "bouquet", "comfort", "organic", "mental", "calm"],
    "thank you": ["thank", "appreciation", "chocolate", "flower", "card", "hamper", "gift set", "candle", "tea", "pen"],
}

ALIASES = {
    "valentines": "valentine", "valentine's": "valentine", "valentines day": "valentine", "valentine's day": "valentine",
    "bday": "birthday", "b'day": "birthday", "shaadi": "wedding", "marriage": "wedding",
    "deepavali": "diwali", "diwali gifts": "diwali", "festival": "diwali",
    "xmas": "christmas", "party": "office party", "team party": "office party", "work": "corporate",
    "new home": "housewarming", "griha pravesh": "housewarming", "baby": "baby shower", "newborn": "baby shower",
    "mother's day": "mothers day", "mom": "mothers day", "father's day": "fathers day", "dad": "fathers day",
    "rakhi": "raksha bandhan", "rakshabandhan": "raksha bandhan", "kid": "kids", "children": "kids",
    "engagement": "wedding", "convocation": "graduation",
}

GENERIC = ["gift", "hamper", "set", "premium"]
