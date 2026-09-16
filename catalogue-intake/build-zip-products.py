#!/usr/bin/env python3
"""Add photographed zip products onto the live catalogue. Keep existing cards."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path("/workspace")
ZIP_PATH = ROOT / "catalogue-intake" / "msp_images.zip"
IMG_DIR = ROOT / "catalogue-images"
DATA = ROOT / "catalogue-data.js"
EXTRACT = Path("/tmp/msp-images")

SKIP_FILES = {
    "Amazon Fire 7 tablet back black transparent png.jpg",
    "Apple iPad 9th gen space grey back transparent png.jpg",
    "Apple iPhone 11 black back transparent png.jpg",
    "Apple iPhone 12 green back transparent png.jpg",
    "Apple iPhone 12 mini blue back transparent png.jpg",
    "Apple iPhone 13 green back transparent png.jpg",
    "Apple iPhone 14 Pro Max deep purple back transparent png.jpg",
    "Apple iPhone 15 Plus pink back transparent png.jpg",
    "Apple iPhone 15 pink back transparent png.jpg",
    "Apple iPhone 8 product red back transparent png.jpg",
    "Apple iPhone SE 2020 black back transparent png.jpg",
    "iPhone 14 box transparent png.jpg",
    "iPhone 17 Pro Max box transparent png.jpg",
    "Bar Juice 5000 Banana Ice 10ml box transparent png.jpg",
    "Bar Juice 5000 Fresh Mint 10ml box transparent png.jpg",
    "lost-mary-maryliq-raspberry-peach-nic-salts-e-liquid.webp",
    "charcoal-for-hookah-coconut-shell-cubes.webp",
    "Pod Salt Core Lychee Ice 10ml box transparent png.jpg",
    "Samsung Galaxy S23 Ultra transparent png.jpg",
    "Samsung Galaxy Tab box transparent png.jpg",
}

RAMILLION = [
    "Banana Ice", "Berry Blaze", "Blueberry Razz Lemonade", "Blueberry Sour Raspberry",
    "Double Apple", "Fizzy Cherry", "Fresh Mint", "Grape Berry", "Grape Ice",
    "Hazelnut Tobacco", "Kiwi Passion Fruit Guava", "Lemon Lime", "Lime Jelly Ice Cream",
    "Lychee Ice", "Menthol", "Mint Gum", "Peach Ice", "Pineapple Ice", "Pink Lemonade",
    "Strawberry Ice", "Strawberry Raspberry Cherry", "Strawberry Watermelon Bubblegum",
    "Triple Mango", "Watermelon Ice",
]
ELUX = [
    "Blueberry Bubblegum", "Blueberry Cherry Cranberry", "Blueberry Sour Raspberry",
    "Cola", "Double Apple", "Fizzy Cherry", "Grape", "Grape Berry", "Gummy Bear",
    "Kiwi Passionfruit Guava", "Lemon & Lime", "Menthol", "Mr Blue", "Pink Lemonade",
    "Strawberry Watermelon Bubblegum", "Triple Mango", "Watermelon Ice",
]
ELFLIQ = [
    "Banana Ice", "Blue Razz Lemonade", "Cherry", "Cream Tobacco", "Grape",
    "Pineapple Ice", "Sour Apple", "Spearmint", "Strawberry Raspberry Cherry", "Tobacco",
]
POD_CORE = [
    "Apple", "Banana Ice", "Blackjack", "Blackcurrant Menthol", "Blue Berg", "Blue Ice",
    "Blueberry Pomegranate", "Cantaloupe Ice", "Cherry Ice", "Cigarette", "Fresh Mint",
    "Grape Ice", "Havana Gold", "Ice Menthol", "Lemon & Lime Ice", "Lychee Ice",
    "Mango Ice", "Mixed Berries", "Mixed Berries Ice", "Peach Ice", "Pineapple Ice",
    "Red Apple Ice", "Spearmint", "Vanilla", "Watermelon Breeze",
]
POD_ORIGIN = [
    "Cuban Crème", "Liquor Tobacco", "Menthol Tobacco", "Royal Tobacco",
    "True Tobacco", "Virginia Gold",
]
POD_NEXUS = [
    "Coco Sun", "Fuji Apple Peach", "Lime Raspberry Grapefruit",
    "Pineapple Passion Lime", "Rainbow", "Super Loe", "White Grape Cucumber Apple",
]
BAR_JUICE_EXTRA = [
    "Apple Peach", "Banana Ice", "Blue Razz Lemonade", "Cherry Cola", "Cherry Ice",
    "Fresh Mint", "Gummy Bear", "Peach Ice", "Pineapple Ice", "Pink Lemonade",
    "Strawberry Cherry Raspberry", "Strawberry Ice", "Watermelon",
]

# filename -> overrides
DETAILS = {
    "Pod Salt Cali Greens amnesia mango 10ml box transparent png.jpg": {
        "name": "Pod Salt Cali Greens Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "20mg/ml"],
        "flavors": ["Amnesia Mango"],
    },
    "Pod Salt Core Blue Berg 10ml box transparent png.jpg": {
        "name": "Pod Salt Core Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "11mg / 20mg", "50/50 VG/PG"],
        "flavors": POD_CORE,
    },
    "Pod Salt Nexus blueberry blackberry lemonade 10ml box transparent png.jpg": {
        "name": "Pod Salt Nexus Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "10mg / 20mg"],
        "flavors": POD_NEXUS,
    },
    "Pod Salt Origin Menthol Tobacco 10ml box transparent png.jpg": {
        "name": "Pod Salt Origin Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "11mg / 20mg"],
        "flavors": POD_ORIGIN,
    },
    "pod-salt-reds-apple-blue-razapple-ice-nic-salts-e-liquid.webp": {
        "name": "Pod Salt Reds Apple Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "20mg/ml"],
        "flavors": ["Blue Razapple Ice"],
    },
    "pod-salt-big-tasty-cola-with-lime-nic-salts-e-liquid.webp": {
        "name": "Pod Salt The Big Tasty Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "20mg/ml"],
        "flavors": ["Cola with Lime"],
    },
    "Ramillion nic salts fresh mint 10ml box transparent png.jpg": {
        "name": "Ramillion Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "10mg / 20mg"],
        "flavors": RAMILLION,
    },
    "Elux Legend mr blue nic salt 10ml box transparent png.jpg": {
        "name": "Elux Legend Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "10mg / 20mg"],
        "flavors": ELUX,
    },
    "elfliq-cherry-nic-salts-e-liquid.webp": {
        "name": "ELFLIQ by Elf Bar Nic Salts",
        "category": "E-Liquids",
        "variants": ["10ml", "10mg / 20mg"],
        "flavors": ELFLIQ,
    },
    "iqos-iluma-one-heated-tobacco-kit.webp": {
        "name": "IQOS Iluma One",
        "category": "Vape Kits",
        "variants": ["Heated tobacco kit"],
        "flavors": [],
    },
    "nokia-106-4g-feature-phone.webp": {
        "name": "Nokia 106 4G",
        "category": "Smartphones",
        "variants": ["Feature phone", "4G"],
        "flavors": [],
    },
    "zen-coconut-shell-coal-cubes-for-hookah.webp": {
        "name": "Zen Coconut Charcoal Cubes",
        "category": "Tech Accessories",
        "variants": ["Coconut shell cubes"],
        "flavors": [],
    },
    "kingston-datatraveler-70-usb-c-flash-drive-128gb.webp": {
        "name": "Kingston DataTraveler 70 USB-C",
        "category": "Tech Accessories",
        "variants": ["128GB", "USB-C"],
        "flavors": [],
    },
    "kingston-datatraveler-exodia-usb-3-2-flash-drive-128gb.webp": {
        "name": "Kingston DataTraveler Exodia USB 3.2",
        "category": "Tech Accessories",
        "variants": ["128GB", "USB 3.2"],
        "flavors": [],
    },
    "Apple iPhone 16 Pro black titanium back transparent png.jpg": {
        "name": "iPhone 16 Pro",
        "category": "Smartphones",
        "variants": ["128GB", "Unlocked", "Black Titanium"],
        "flavors": [],
    },
    "Apple iPhone 13 mini blue back transparent png.jpg": {
        "name": "iPhone 13 Mini",
        "category": "Smartphones",
        "variants": ["128GB", "256GB", "Unlocked"],
        "flavors": [],
    },
    "Apple iPhone 7 matte black back transparent png.png": {
        "name": "iPhone 7",
        "category": "Smartphones",
        "variants": ["128GB", "Unlocked", "Matte Black"],
        "flavors": [],
    },
    "Apple iPhone 8 Plus space grey back transparent png.jpg": {
        "name": "iPhone 8 Plus",
        "category": "Smartphones",
        "variants": ["64GB", "Unlocked", "Space Grey"],
        "flavors": [],
    },
    "Apple iPhone X space grey back transparent png.png": {
        "name": "iPhone X",
        "category": "Smartphones",
        "variants": ["64GB", "Unlocked", "Space Grey"],
        "flavors": [],
    },
    "Apple iPhone XS Max gold back transparent png.jpg": {
        "name": "iPhone XS Max",
        "category": "Smartphones",
        "variants": ["64GB", "Unlocked", "Gold"],
        "flavors": [],
    },
    "Samsung Galaxy S21 FE 5G transparent png.jpg": {
        "name": "Samsung Galaxy S21 FE 5G",
        "category": "Smartphones",
        "variants": ["128GB", "Unlocked"],
        "flavors": [],
    },
    "M-TK 7 in 1 gamepad controller box transparent png.jpg": {
        "name": "M-TK 7 in 1 Game Pad",
        "category": "Gaming",
        "variants": ["Wireless", "Dual analog"],
        "flavors": [],
    },
    "K8 wireless microphone for iPhone lightning transparent png.jpg": {
        "name": "K8 Wireless Lavalier Microphone for iPhone",
        "category": "Tech Accessories",
        "variants": ["Lightning", "Plug and play"],
        "flavors": [],
    },
    "Thomson 14 inch notebook white transparent png.jpg": {
        "name": "Thomson 14-inch Windows 10 Laptop",
        "category": "Laptops",
        "variants": ["Windows 10"],
        "flavors": [],
    },
    "TWS wireless earbuds with charging case red box transparent png.jpg": {
        "name": "TWS Wireless Earbuds with Charging Case",
        "category": "Tech Accessories",
        "variants": ["Bluetooth", "In-ear"],
        "flavors": [],
    },
    "Doro 1380 mobile phone box transparent png.jpg": {
        "name": "Doro 1380",
        "category": "Smartphones",
        "variants": ["Unlocked", "Big button"],
        "flavors": [],
    },
    "Samsung Galaxy A05s light violet retail box transparent png.jpg": {
        "name": "Samsung Galaxy A05s",
        "category": "Smartphones",
        "variants": ["128GB", "Unlocked"],
        "flavors": [],
    },
    "Samsung Galaxy A34 5G awesome lime retail box transparent png.jpg": {
        "name": "Samsung Galaxy A34 5G",
        "category": "Smartphones",
        "variants": ["5G", "Unlocked"],
        "flavors": [],
    },
    "Samsung Galaxy Note 3 white handset transparent png.jpg": {
        "name": "Samsung Galaxy Note 3",
        "category": "Smartphones",
        "variants": ["White"],
        "flavors": [],
    },
    "Samsung Galaxy Buds 3 Pro black box transparent png.jpg": {
        "name": "Samsung Galaxy Buds 3 Pro",
        "category": "Tech Accessories",
        "variants": ["Bluetooth", "ANC"],
        "flavors": [],
    },
    "Apple EarPods with lightning connector box transparent png.jpg": {
        "name": "Apple EarPods with Lightning Connector",
        "category": "Tech Accessories",
        "variants": ["Lightning", "In-ear"],
        "flavors": [],
    },
    "Apple 35W dual USB C port compact power adapter box transparent png.jpg": {
        "name": "Apple 35W Dual USB-C Power Adapter",
        "category": "Tech Accessories",
        "variants": ["35W", "Dual USB-C"],
        "flavors": [],
    },
    "JBL Tune 130NC TWS box transparent png.jpg": {
        "name": "JBL Tune 130NC TWS Earbuds",
        "category": "Tech Accessories",
        "variants": ["ANC", "Bluetooth"],
        "flavors": [],
    },
    "Bose Ultra Open Earbuds box transparent png.jpg": {
        "name": "Bose Ultra Open Earbuds",
        "category": "Tech Accessories",
        "variants": ["Open earbuds"],
        "flavors": [],
    },
    "Samsung 45W PD power adapter with type c cable box transparent png.jpg": {
        "name": "Samsung 45W PD Power Adapter",
        "category": "Tech Accessories",
        "variants": ["45W PD", "USB-C cable"],
        "flavors": [],
    },
    "Apple MacBook Air 13.6 M2 midnight transparent png.jpg": {
        "name": "Apple MacBook Air 13.6 M2",
        "category": "Laptops",
        "variants": ["8GB RAM", "256GB SSD", "Midnight"],
        "flavors": [],
    },
    "Apple iPad 2 silver back transparent png.jpg": {
        "name": "Apple iPad 2",
        "category": "Tablets",
        "variants": ["16GB", "Wi-Fi"],
        "flavors": [],
    },
    "Apple iPad Mini silver back transparent png.jpg": {
        "name": "Apple iPad Mini",
        "category": "Tablets",
        "variants": ["16GB", "Wi-Fi"],
        "flavors": [],
    },
    "Apple iPad Mini 3 silver back transparent png.jpg": {
        "name": "Apple iPad Mini 3",
        "category": "Tablets",
        "variants": ["16GB", "Wi-Fi"],
        "flavors": [],
    },
    "Apple iPad 7th generation silver back transparent png.jpg": {
        "name": "Apple iPad 7th Gen 10.2",
        "category": "Tablets",
        "variants": ["128GB", "Wi-Fi"],
        "flavors": [],
    },
}


def extract_zip() -> None:
    EXTRACT.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for info in zf.infolist():
            name = Path(info.filename.replace("\\", "/")).name
            if not name:
                continue
            with zf.open(info) as src, open(EXTRACT / name, "wb") as dest:
                dest.write(src.read())


def clean_name(filename: str) -> str:
    stem = re.sub(r"\.(webp|jpg|jpeg|png)$", "", filename, flags=re.I)
    stem = re.sub(r"\btransparent png\b", "", stem, flags=re.I)
    stem = stem.replace("-", " ").replace("_", " ")
    stem = re.sub(r"\b(box|retail|back|handset)\b", "", stem, flags=re.I)
    stem = re.sub(r"\s+", " ", stem).strip()
    if stem.lower() == stem or "-" in filename:
        return stem.title()
    return stem


def guess_category(filename: str, name: str) -> str:
    s = (filename + " " + name).lower()
    if any(x in s for x in ["nic salt", "pod salt", "bar juice", "elfliq", "elux", "ramillion", "maryliq"]):
        return "E-Liquids"
    if "iqos" in s:
        return "Vape Kits"
    if any(x in s for x in ["case", "glass", "protector", "wallet", "armor", "imaxx", "king kong"]):
        return "Protection & Cases"
    if "microphone" in s or "earphone" in s or "earbuds" in s:
        if "quilted" in s or "leather airpods" in s or "silicone quilted" in s:
            return "Protection & Cases"
        return "Tech Accessories"
    if any(x in s for x in [
        "iphone", "galaxy a0", "galaxy a1", "galaxy a2", "galaxy a3", "galaxy a5",
        "galaxy note 3", "doro", "honor", "huawei", "oppo", "redmi a2", "vodafone",
        "nokia", "galaxy s20", "galaxy s21",
    ]) and not any(x in s for x in ["case", "cable", "adapter", "buds", "charger", "watch", "microphone"]):
        return "Smartphones"
    if "thomson" in s or "notebook" in s:
        return "Laptops"
    if any(x in s for x in ["ipad", "galaxy tab"]):
        return "Tablets"
    if "macbook" in s:
        return "Laptops"
    if "game" in s and "pad" in s:
        return "Gaming"
    return "Tech Accessories"


def make_product(filename: str) -> dict:
    over = DETAILS.get(filename, {})
    name = over.get("name") or clean_name(filename)
    category = over.get("category") or guess_category(filename, name)
    return {
        "name": name,
        "category": category,
        "badge_text": "ENQUIRE FOR PRICE",
        "action_type": "call",
        "action_btn_text": "Call Store for Price & Stock",
        "action_link": "tel:+442080011639",
        "image": "catalogue-images/" + filename,
        "variants": over.get("variants") or [],
        "flavors": over.get("flavors") or [],
    }


def load_existing() -> list:
    text = DATA.read_text()
    m = re.search(r"const productsData = (\[.*\]);?\s*$", text, re.S)
    return json.loads(m.group(1))


def merge_flavors(existing: list) -> None:
    extra = {x.lower(): x for x in BAR_JUICE_EXTRA}
    for p in existing:
        if p["name"] == "Bar Juice 5000 E-Liquids":
            have = {x.lower(): x for x in p.get("flavors") or []}
            for key, label in extra.items():
                if key not in have:
                    have[key] = label
            p["flavors"] = list(have.values())


def main() -> None:
    extract_zip()
    IMG_DIR.mkdir(exist_ok=True)
    existing = load_existing()
    merge_flavors(existing)
    live_names = {p["name"].lower() for p in existing}

    files = sorted(p.name for p in EXTRACT.iterdir() if p.is_file())
    added = []
    skipped = []
    for filename in files:
        dest = IMG_DIR / filename
        shutil.copy2(EXTRACT / filename, dest)
        if filename in SKIP_FILES:
            skipped.append(filename)
            continue
        product = make_product(filename)
        if product["name"].lower() in live_names:
            skipped.append(filename + " (name exists)")
            continue
        live_names.add(product["name"].lower())
        added.append(product)

    combined = existing + added
    DATA.write_text("const productsData = " + json.dumps(combined, ensure_ascii=False, indent=2) + ";\n")
    print("existing", len(existing))
    print("added", len(added))
    print("skipped", len(skipped))
    print("total", len(combined))
    from collections import Counter
    print(dict(Counter(p["category"] for p in combined)))
    Path("/workspace/catalogue-intake/zip-load-report.txt").write_text(
        "Added {0} products from zip. Skipped {1} files (already live or extra flavour shot).\nTotal cards: {2}\n\nADDED\n{3}\n\nSKIPPED\n{4}\n".format(
            len(added),
            len(skipped),
            len(combined),
            "\n".join(p["category"] + "\t" + p["name"] for p in added),
            "\n".join(skipped),
        )
    )


if __name__ == "__main__":
    main()
