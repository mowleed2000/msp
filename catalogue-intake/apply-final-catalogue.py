#!/usr/bin/env python3
"""Recategorise, clean titles, merge flavours, and add remaining photographed products."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path("/workspace")
DATA = ROOT / "catalogue-data.js"
IMG_DIR = ROOT / "catalogue-images"
SRC_NEW = Path("/tmp/final-products")

CORE_30 = [
    "Blueberry Raspberry", "Blue Razz Cherry", "Blueberry Ice", "Cherry Cola",
    "Grape Ice", "Lemon Lime", "Mango Ice", "Mixed Berry", "Peach Ice",
    "Pineapple Ice", "Pink Lemonade", "Raspberry Lemonade", "Sour Apple Ice",
    "Strawberry Ice", "Triple Mango", "Watermelon Ice", "Blueberry Sour Raspberry",
    "Cherry Ice", "Cola Ice", "Grape Raspberry", "Strawberry Kiwi",
    "Watermelon Lemonade", "Kiwi Passion Fruit Guava", "Peach Mango Pineapple",
    "Blueberry Fusion", "Cherry Lemonade", "Cotton Candy Ice", "Mango Peach",
    "Strawberry Raspberry Cherry", "Blueberry Cotton Candy",
]

IVG_2400 = [
    "Blue Raspberry Ice", "Strawberry Watermelon", "Pink Lemonade",
    "Fresh Menthol Mojito", "Strawberry Ice", "Polar Mint", "Classic Menthol",
    "Lemon Lime", "Mango", "Passionfruit", "Pineapple Ice", "Ruby Orange",
    "Spearmint", "Tropical Berry", "Vanilla Custard", "Watermelon",
]

IVG_PRO = [
    "Strawberry Ice", "Kiwi Passionfruit Guava", "Sour Cherry Watermelon",
    "Tobacco", "Blue Raspberry Ice", "Blueberry Mint", "Pineapple Ice",
    "Strawberry Raspberry Cherry", "Fresh Menthol Mojito", "Pink Lemonade",
    "Blue Razz Lemonade", "Strawberry Watermelon", "Cherry Cola",
    "Watermelon Ice", "Lemon Lime", "Triple Mango", "Grape Ice", "Peach Ice",
]

MARYLIQ = [
    "Triple Mango", "Watermelon Ice", "Double Apple", "Peach Ice",
    "Blackcurrant Apple", "Lemon Lime", "Blueberry Sour Raspberry",
    "Blueberry Raspberry", "Cherry Ice", "Strawberry Ice", "Pineapple Ice",
    "Grape Ice", "Pink Lemonade", "Fresh Mint", "Kiwi Passion Fruit Guava",
    "Strawberry Raspberry Cherry", "Sour Apple", "Cola", "Menthol", "Miami Mint",
]

ELFLIQ = [
    "Banana Ice", "Blue Razz Lemonade", "Cherry", "Cream Tobacco", "Grape",
    "Pineapple Ice", "Sour Apple", "Spearmint", "Strawberry Raspberry Cherry",
    "Tobacco", "Blueberry Sour Raspberry", "Cola", "Elfbull",
    "Kiwi Passion Fruit Guava", "Lemon Lime", "Mango", "Peach Ice",
    "Pink Grapefruit", "Strawberry Ice", "Watermelon",
]

BAR_JUICE = [
    "Apple Peach", "Banana Ice", "Blue Razz Lemonade", "Cherry Cola", "Cherry Ice",
    "Fresh Mint", "Gummy Bear", "Peach Ice", "Pineapple Ice", "Pink Lemonade",
    "Strawberry Cherry Raspberry", "Strawberry Ice", "Watermelon",
    "Blueberry Sour Raspberry", "Fizzy Cherry", "Grape Ice", "Lemon Lime",
    "Menthol", "Triple Mango", "Watermelon Ice",
]

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

SKE_CRYSTAL = [
    "Blueberry Sour Raspberry", "Cherry Cola", "Fresh Mint", "Grape Ice",
    "Kiwi Passion Fruit Guava", "Lemon Lime", "Mango Ice", "Peach Ice",
    "Pineapple Ice", "Pink Lemonade", "Sour Apple Ice", "Strawberry Ice",
    "Strawberry Raspberry Cherry", "Triple Mango", "Watermelon Ice",
    "Blue Razz Lemonade", "Cola Ice", "Menthol", "Mr Blue", "Fizzy Cherry",
]

NIC_DRIP = [
    "Blueberry Sour Raspberry", "Strawberry Ice", "Watermelon Ice", "Lemon Lime",
    "Fresh Mint", "Grape Ice", "Mango Ice", "Peach Ice", "Pineapple Ice",
    "Pink Lemonade", "Cherry Ice", "Cola", "Menthol", "Triple Mango",
    "Strawberry Raspberry Cherry", "Kiwi Passion Fruit Guava",
]

LOST_MARY_5MG = [
    "Blueberry Sour Raspberry", "Triple Mango", "Watermelon Ice", "Strawberry Ice",
    "Cherry Ice", "Pineapple Ice", "Pink Lemonade", "Lemon Lime", "Fresh Mint",
    "Double Apple", "Grape Ice", "Peach Ice", "Miami Mint", "Cola",
    "Strawberry Raspberry Cherry", "Kiwi Passion Fruit Guava",
]

DINNER_LADY = [
    "Lemon Tart", "Apple Sours", "Bubble Trouble", "Cool Mint Ice", "Raspberry Sherbet",
    "Strawberry Macaroon", "Tuck Shop", "Watermelon Slices", "Blackberry Crumble",
    "Heisenberg", "Pink Soul", "Sunshine Chaser", "Tropic Thunder", "Berry Blast",
    "Lemon Sherbet", "Mint Tobacco",
]

DONUT_KING = [
    "Glazed", "Blueberry", "Strawberry Jam", "Chocolate Custard", "Lemon Drizzle",
    "Maple", "Boston Cream", "Cinnamon", "Raspberry Iced", "Vanilla Custard",
    "Cookies & Cream", "Caramel",
]

DK_CAKES = [
    "Victoria Sponge", "Lemon Drizzle", "Chocolate Fudge", "Red Velvet",
    "Carrot Cake", "Battenberg", "Coffee Cake", "Vanilla Slice",
]

DK_FRUITS = [
    "Strawberry", "Blueberry", "Mango", "Watermelon", "Mixed Berry",
    "Pineapple", "Grape", "Peach", "Apple", "Cherry",
]

BAZOOKA = [
    "Green Apple", "Blue Raspberry", "Strawberry", "Watermelon", "Grape", "Cherry",
    "Sour Straws", "Tropical",
]

DOUBLE_DRIP = [
    "Venom", "Cravin", "Dodge City", "Rodeo", "TNT", "Oasis", "Carnival",
    "Strawberry Ice", "Lemon Sherbet", "Menthol",
]

JB_JUICE = [
    "Blueberry Sour Raspberry", "Strawberry Ice", "Watermelon Ice", "Lemon Lime",
    "Fresh Mint", "Grape Ice", "Mango Ice", "Peach Ice", "Pineapple Ice",
    "Pink Lemonade", "Cherry Cola", "Fizzy Cherry", "Triple Mango",
    "Strawberry Raspberry Cherry", "Kiwi Passion Fruit Guava", "Mr Blue",
    "Cola", "Menthol", "Banana Ice", "Gummy Bear",
]

OHM_BREW = [
    "Shortfill Blend", "Blue Slush", "Strawberry Storm", "Mango Tahiti",
    "Lemon Lime", "Grape Ice", "Menthol", "Tobacco", "Cola", "Peach Ice",
]

STRAPPED = [
    "Proper Punch", "Strawberry Soda", "Blue Raspberry Soda", "Cherry Cola",
    "Lemon Sherbet", "Tropical Soda", "Grape Soda", "Orange Soda",
]

TASTY_FRUITY = [
    "Mixed Fruit", "Strawberry", "Blueberry", "Mango", "Watermelon",
    "Pineapple", "Grape", "Peach", "Apple", "Cherry", "Lemon Lime", "Berry Blast",
]

VAPOUR_LIFE = [
    "Menthol", "Tobacco", "Strawberry", "Blueberry", "Mango", "Watermelon",
    "Lemon Lime", "Grape", "Mint", "Cola", "Vanilla", "Cherry",
]

PUFF_STUFF = [
    "British Tobacco", "USA Mix", "Virginia Tobacco", "Menthol Tobacco",
    "Cuban Tobacco", "RY4",
]

CBD_FLAVOURS = ["Lemon", "Natural", "Berry", "Mint", "Orange"]
VITALITY_CBD = ["Natural", "Mint", "Berry", "Citrus", "Vanilla"]

KIT_COLOURS = ["Black", "Silver", "Blue", "Red", "Green", "Gold"]
XROS_COLOURS = ["Black", "Silver", "Blue", "Green", "Pink", "Gold"]
CALIBURN_COLOURS = ["Black", "Grey", "Blue", "Red", "Gold", "Purple"]
SMOK_COLOURS = ["Black", "Silver", "Red", "Blue", "Prism"]
COIL_OHMS = ["0.3Ω", "0.6Ω", "0.8Ω", "1.0Ω", "1.2Ω"]
POD_OHMS = ["0.8Ω", "1.0Ω", "1.2Ω"]

DROP_NAMES = {
    "Samsung SAMSNG S10",
    "Samsung SAMSNG S20 (5G)",
    "Samsung Samsung S20 (5G)",
    "Samsung SAMSNG S20 PLUS A",
    "Samsung Samsung S20 Plus A",
    "PS5 DualSense Controller",
    "asus 10th gen",
}

RENAME = {
    "ASUS ASUS": "ASUS Core i7 10th Gen Laptop",
    "DELL Dell Laptop": "Dell Laptop",
    "HP ELITEBOOK 850 G7": "HP EliteBook 850 G7",
    "HP PROBOOK 440 G7": "HP ProBook 440 G7",
    "Samsung SAMSUNG S20 ULTRA 5G": "Samsung Galaxy S20 Ultra 5G",
    "Samsung SAMSUNG S22 PLUS": "Samsung Galaxy S22 Plus",
    "Samsung SAMSUNG S22 ULTRA": "Samsung Galaxy S22 Ultra",
    "Samsung Samsung S20 FE A": "Samsung Galaxy S20 FE",
    "Pro Fizzy Cherry Smart Pod": "Fizzy Cherry Smart Pod",
    "5000Mah Power Bank Built In Cables Digital Display": "5000mAh Power Bank with Built-In Cables",
    "Slim 20000Mah Power Bank White": "Slim 20000mAh Power Bank",
    "Cat5E Rj45 Ethernet Cable 5M": "Cat5e RJ45 Ethernet Cable 5m",
    "Hp Usb C Universal Dock G2": "HP USB-C Universal Dock G2",
    "Gw 600 Rechargeable Wireless Mouse Black": "GW-600 Rechargeable Wireless Mouse",
    "Az E02 Lightning Earphones": "AZ E02 Lightning Earphones",
    "AZ wired optical office mouse comfort feel": "AZ Wired Optical Office Mouse",
    "M Tk Tb2028 2 In 1 Usb Type C Card Reader": "MTK TB2028 2-in-1 USB-C Card Reader",
    "M Tk Usb Wall Charger Plug With Lightning Cable": "MTK USB Wall Charger with Lightning Cable",
    "budi 15W wireless charger stand yellow": "Budi 15W Wireless Charger Stand",
    "dual port 20W PD fast charger UK plug white": "Dual-Port 20W PD Fast Charger",
    "retractable 240W USB C to USB C cable": "Retractable 240W USB-C to USB-C Cable",
    "white TWS wireless earbuds": "White TWS Wireless Earbuds",
    "Usb 2.0 To Rj45 Ethernet Lan Network Adapter": "USB 2.0 to RJ45 Ethernet LAN Adapter",
    "Lightning To Usb Female Otg Cable Adapter Blue": "Lightning to USB OTG Adapter",
    "Lightning To 3.5Mm Headphone Adapter Short Cable": "Lightning to 3.5mm Headphone Adapter",
    "Universal All In One Travel Adaptor Usb Type C": "Universal All-in-One Travel Adapter USB-C",
    "Wireless Carplay Android Auto Usb Adapter Dongle": "Wireless CarPlay / Android Auto Adapter",
    "3 In 1 Wireless Fast Charging Dock Station Black": "3-in-1 Wireless Fast Charging Dock",
    "4 in 1 OTG micro SD TF card reader USB C lightning": "4-in-1 OTG USB-C / Lightning Card Reader",
    "4 In 1 Foldable Wireless Charging Stand": "4-in-1 Foldable Wireless Charging Stand",
    "Go Des Gd G026 Phone Ring Holder Bracket": "Go Des GD-G026 Phone Ring Holder",
    "K 06 2.4G Wireless Keyboard And Mouse Set White": "K06 2.4G Wireless Keyboard and Mouse Set",
    "Newrixing Nr 3026M Wireless Speaker": "Newrixing NR-3026M Wireless Speaker",
    "Speed Flash Microsd Memory Card With Adapter 32Gb": "Speed Flash microSD Card 32GB",
    "Speed Flash Microsd Memory Card With Adapter 64Gb": "Speed Flash microSD Card 64GB",
    "Gerlax P115 10000mah power bank": "Gerlax P115 10000mAh Power Bank",
    "NCC 10000mah power bank": "NCC 10000mAh Power Bank",
    "140W multi port USB C desktop fast charger": "140W Multi-Port USB-C Desktop Fast Charger",
    "10000mAh magnetic wireless power bank with stand": "10000mAh Magnetic Wireless Power Bank with Stand",
    "5000mAh mini portable power bank with built in plug": "5000mAh Mini Power Bank with Built-In Plug",
    "65W GaN 3 port USB C fast charger black": "65W GaN 3-Port USB-C Fast Charger",
    "65W retractable cable car charger dual ports": "65W Retractable Dual-Port Car Charger",
    "GaN 30W dual USB C wall charger UK plug": "GaN 30W Dual USB-C Wall Charger",
    "Apple 60W USB C woven charge cable 1m": "Apple 60W USB-C Woven Charge Cable 1m",
    "CSR 4.0 USB bluetooth dongle adapter": "CSR 4.0 USB Bluetooth Dongle",
    "Earldom W35 lightning to hdmi cable 2k": "Earldom W35 Lightning to HDMI Cable",
    "Earldom honeycomb rgb wired gaming mouse": "Earldom Honeycomb RGB Wired Gaming Mouse",
    "Samsung 15W travel adapter USB C white": "Samsung 15W USB-C Travel Adapter",
    "Samsung Galaxy Note 10 type c to type c cable": "Samsung Galaxy Note 10 USB-C to USB-C Cable",
    "Samsung micro usb data cable white": "Samsung Micro USB Data Cable",
    "Yesido CA186 240W Dual Type-C Cable 2m": "Yesido CA186 240W Dual USB-C Cable 2m",
    "leather wallet phone case Samsung Galaxy A13 5G": "Samsung Galaxy A13 5G Leather Wallet Case",
    "iMaxx magsafe anti shock clear case iPhone": "iMaxx MagSafe Anti-Shock Clear iPhone Case",
    "iMaxx silicone phone case iPhone yellow": "iMaxx Silicone iPhone Case — Yellow",
    "Apple MacBook Pro 13\"": "Apple MacBook Pro 13-inch",
    "Microsoft Surface Business Laptop": "Microsoft Surface Laptop",
}

MOVE_TO = {
    "Google Pixel 8 Pro": "Smartphones",
    "Motorola Moto G6": "Smartphones",
    "Nokia G21": "Smartphones",
    "Samsung Galaxy A54 5G": "Smartphones",
    "Samsung Galaxy S10": "Smartphones",
    "Samsung Galaxy S20 Plus": "Smartphones",
    "Samsung Galaxy S23 FE 5G": "Smartphones",
    "Samsung Galaxy S23 Ultra 5G": "Smartphones",
    "Samsung Galaxy S24 Ultra 5G": "Smartphones",
    "Samsung Galaxy S20 Ultra 5G": "Smartphones",
    "Samsung Galaxy S22 Plus": "Smartphones",
    "Samsung Galaxy S22 Ultra": "Smartphones",
    "Samsung Galaxy S20 FE": "Smartphones",
    "Xiaomi Redmi Note 13 Pro 5G": "Smartphones",
    "TCL 403": "Smartphones",
    "TCL 405": "Smartphones",
    "IMO Q2 Pro": "Smartphones",
    "HP Pavilion 13th Gen": "Laptops",
    "HP ZBook Studio G5": "Laptops",
    "ASUS Core i7 10th Gen Laptop": "Laptops",
    "Hopestar P61 Portable Mini Speaker": "Tech Accessories",
    "Yesido GaN 67W Retractable Charger YC146": "Tech Accessories",
    "Universal Laptop AC Power Adapters": "Tech Accessories",
    "Fizzy Cherry Smart Pod": "Vape Kits",
    "Privacy Tempered Glass Screen Protector": "Protection & Cases",
    "Borofone Bike Phone Mount": "Tech Accessories",
    "Yesido Vacuum Lock Electric Car Phone Mount": "Tech Accessories",
}

TOKEN = {
    "usb": "USB", "usb-c": "USB-C", "usbc": "USB-C", "gan": "GaN", "pd": "PD",
    "rgb": "RGB", "tws": "TWS", "hdmi": "HDMI", "ssd": "SSD", "ram": "RAM",
    "led": "LED", "otg": "OTG", "tf": "TF", "rj45": "RJ45", "4g": "4G", "5g": "5G",
    "hp": "HP", "asus": "ASUS", "dell": "Dell", "mtk": "MTK", "ncc": "NCC",
    "az": "AZ", "wifi": "Wi-Fi", "lan": "LAN", "sd": "SD", "sata": "SATA",
    "qc": "QC", "magsafe": "MagSafe", "hd": "HD", "gb": "GB", "tb": "TB",
    "mah": "mAh", "cat5e": "Cat5e", "microsd": "microSD", "type-c": "USB-C",
    "typec": "USB-C", "rgb": "RGB", "anc": "ANC", "sim": "SIM", "uk": "UK",
    "eu": "EU", "pc": "PC", "macbook": "MacBook", "iphone": "iPhone",
    "ipad": "iPad", "ps5": "PS5", "ps4": "PS4", "jbl": "JBL", "ssd": "SSD",
}

SMALL = {"a", "an", "and", "or", "the", "of", "for", "to", "with", "in", "on"}


def polish_title(name: str) -> str:
    name = RENAME.get(name, name)
    name = re.sub(r"(?i)(\d+)\s*mah\b", r"\1mAh", name)
    name = re.sub(r"(?i)\b(\d+)\s*in\s*(\d+)\b", r"\1-in-\2", name)
    name = name.replace("Type C", "USB-C").replace("Type-C", "USB-C")
    name = name.replace("type c", "USB-C").replace("type-c", "USB-C")
    parts = name.split()
    out = []
    for i, part in enumerate(parts):
        prefix = ""
        suffix = ""
        core = part
        while core and core[0] in "([":
            prefix += core[0]
            core = core[1:]
        while core and core[-1] in ")].,/":
            suffix = core[-1] + suffix
            core = core[:-1]
        key = re.sub(r"[^A-Za-z0-9+]", "", core).lower()
        if re.fullmatch(r"\d+mah", key):
            word = re.sub(r"(?i)mah", "mAh", core)
        elif key in TOKEN:
            word = TOKEN[key]
        elif core.lower() in ("iphone", "ipad", "imaxx"):
            word = "i" + core[1:].capitalize() if len(core) > 1 else core
        elif i > 0 and key in SMALL:
            word = key
        elif core.isupper() and len(core) > 3 and key not in TOKEN:
            word = core.title()
        elif core.islower() and len(core) > 1:
            word = core.capitalize()
        elif core[:1].islower() and core.lower() not in ("iPhone", "iPad"):
            if key in ("iphone", "ipad", "imaxx"):
                word = "i" + core[1:].capitalize()
            else:
                word = core[:1].upper() + core[1:]
        else:
            word = core
        out.append(prefix + word + suffix)
    cleaned = " ".join(out)
    cleaned = cleaned.replace("Usb-C", "USB-C").replace("Usb C", "USB-C")
    cleaned = cleaned.replace("IPhone", "iPhone").replace("IPad", "iPad")
    cleaned = cleaned.replace("IMaxx", "iMaxx").replace("Macbook", "MacBook")
    cleaned = cleaned.replace("Magsafe", "MagSafe")
    return cleaned


def merge_flavors(*lists):
    seen = set()
    out = []
    for lst in lists:
        for item in lst or []:
            text = " ".join(str(item).replace("/", " / ").split())
            text = text.strip(" ,")
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            # Title-case unless it already has mixed brand punctuation
            if text != text.upper() and text != text.lower():
                out.append(text)
            else:
                out.append(text.title().replace("'S", "'s").replace("N'", "n'"))
    return out


def card(name, category, image, variants=None, flavors=None):
    return {
        "name": name,
        "category": category,
        "badge_text": "ENQUIRE FOR PRICE",
        "action_type": "call",
        "action_btn_text": "Call Store for Price & Stock",
        "action_link": "tel:+442080011639",
        "image": image,
        "variants": variants or [],
        "flavors": flavors or [],
    }


def copy_new(filename: str, dest_name: str | None = None) -> str:
    src = SRC_NEW / filename
    dest_name = dest_name or filename
    if dest_name.endswith(".png.png"):
        dest_name = dest_name[:-4]
    dest = IMG_DIR / dest_name
    if src.exists():
        shutil.copy2(src, dest)
    return f"catalogue-images/{dest_name}"


def load_products():
    text = DATA.read_text()
    start = text.find("[")
    end = text.rfind("]")
    return json.loads(text[start : end + 1])


def write_products(products):
    payload = json.dumps(products, indent=2, ensure_ascii=False)
    DATA.write_text("const productsData = " + payload + ";\n")


def flavour_merge_for(name: str, existing):
    n = name.lower()
    extra = []
    if "hayati pro ultra" in n:
        extra = CORE_30
    elif "hayati pro max" in n:
        extra = CORE_30
    elif "hayati" in n and "6k" in n:
        extra = CORE_30
    elif "ske 35k" in n or "ske bar 15" in n:
        extra = CORE_30
    elif "ivg 2400" in n:
        extra = IVG_2400
    elif "ivg smart 5500" in n:
        extra = IVG_2400
    elif "ivg 600" in n:
        extra = IVG_2400
    elif "ivg pro" in n:
        extra = IVG_PRO
    elif "maryliq" in n:
        extra = MARYLIQ
    elif "elfliq" in n:
        extra = ELFLIQ
    elif "bar juice" in n:
        extra = BAR_JUICE
    elif "ramillion" in n:
        extra = RAMILLION
    elif "elux" in n:
        extra = ELUX
    elif "pod salt core" in n:
        extra = POD_CORE
    elif "pod salt origin" in n:
        extra = POD_ORIGIN
    elif "lost mary bm600" in n or "lost mary 30k" in n:
        extra = CORE_30
    elif "lost mary" in n:
        extra = CORE_30
    elif "fizzy" in n:
        extra = CORE_30
    elif "crown bar" in n:
        extra = CORE_30
    if extra or existing:
        return merge_flavors(existing, extra)
    return existing or []


NEW_PRODUCTS = [
    # --- kits ---
    ("Aspire Minican Plus", "Vape Kits",
     "Aspire Minican Plus kit box transparent png.jpg",
     KIT_COLOURS + POD_OHMS, []),
    ("Dojo Blast 2000", "Vape Kits",
     "Dojo Blast 2000 vape kit transparent png.jpg",
     ["Up to 2000 puffs", "Rechargeable"], CORE_30),
    ("Geekvape Aegis Pod Kit", "Vape Kits",
     "Geekvape Aegis pod kit box transparent png.jpg",
     KIT_COLOURS + ["IP67"], []),
    ("Geekvape Max100 Kit", "Vape Kits",
     "Geekvape Max100 kit box transparent png.jpg",
     ["100W", "Dual 18650"], COIL_OHMS),
    ("HorizonTech Falcon Legend Tank", "Vape Kits",
     "HorizonTech Falcon Legend tank box transparent png.jpg",
     COIL_OHMS, []),
    ("Innokin Endura T18E Starter Kit", "Vape Kits",
     "Innokin Endura T18E starter kit box transparent png.jpg",
     KIT_COLOURS, []),
    ("Lost Vape Thelema Elite 40", "Vape Kits",
     "Lost Vape Thelema Elite 40 kit box transparent png.jpg",
     KIT_COLOURS + ["40W"], POD_OHMS),
    ("Lost Vape Ursa Cap Pro", "Vape Kits",
     "Lost Vape Ursa Cap Pro kit box transparent png.jpg",
     KIT_COLOURS, POD_OHMS),
    ("Mevol 14K Pod Kit", "Vape Kits",
     "Mevol 14K pod kit box transparent png.jpg",
     ["Up to 14,000 puffs"], CORE_30),
    ("OXVA Xlim Pro", "Vape Kits",
     "OXVA Xlim Pro kit box transparent png.jpg",
     XROS_COLOURS + POD_OHMS, []),
    ("OXVA Xlim SE", "Vape Kits",
     "OXVA Xlim SE kit box transparent png.png",
     XROS_COLOURS + POD_OHMS, []),
    ("SKE Bar 15K Pod Kit", "Vape Kits",
     "SKE Bar 15K pod kit box transparent png.jpg",
     ["Up to 15,000 puffs", "Rechargeable"], CORE_30),
    ("Smok A-Priv Kit", "Vape Kits",
     "Smok A-Priv kit box transparent png.jpg",
     SMOK_COLOURS, COIL_OHMS),
    ("Smok Arco Digi Kit", "Vape Kits",
     "Smok Arco Digi kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok Mag Pod Kit", "Vape Kits",
     "Smok Mag Pod kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok Mag V8 Kit", "Vape Kits",
     "Smok Mag V8 kit box transparent png.jpg",
     SMOK_COLOURS, COIL_OHMS),
    ("Smok Nfix Pro", "Vape Kits",
     "Smok Nfix Pro kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok Nord 4", "Vape Kits",
     "Smok Nord 4 kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok Nord 50W", "Vape Kits",
     "Smok Nord 50W kit box transparent png.jpg",
     SMOK_COLOURS + ["50W"], POD_OHMS),
    ("Smok Nord Pro", "Vape Kits",
     "Smok Nord Pro kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok Novo 2", "Vape Kits",
     "Smok Novo 2 kit box transparent png.jpg",
     SMOK_COLOURS, POD_OHMS),
    ("Smok RPM 5", "Vape Kits",
     "Smok RPM 5 kit box transparent png.jpg",
     SMOK_COLOURS, COIL_OHMS),
    ("Teslacigs I-KIT", "Vape Kits",
     "Teslacigs I-KIT box transparent png.jpg",
     KIT_COLOURS, COIL_OHMS),
    ("Uwell Caliburn G2", "Vape Kits",
     "Uwell Caliburn G2 kit box transparent png.jpg",
     CALIBURN_COLOURS + POD_OHMS, []),
    ("Uwell Caliburn Tenet KOKO", "Vape Kits",
     "Uwell Caliburn Tenet Koko kit box transparent png.jpg",
     CALIBURN_COLOURS + POD_OHMS, []),
    ("Uwell Caliburn X", "Vape Kits",
     "Uwell Caliburn X kit box transparent png.jpg",
     CALIBURN_COLOURS + POD_OHMS, []),
    ("Vaporesso Eco Nano", "Vape Kits",
     "Vaporesso Eco Nano kit box transparent png.jpg",
     XROS_COLOURS, POD_OHMS),
    ("Vaporesso Luxe Q", "Vape Kits",
     "Vaporesso Luxe Q kit box transparent png.jpg",
     XROS_COLOURS, POD_OHMS),
    ("Vaporesso Vibe SE", "Vape Kits",
     "Vaporesso Vibe SE kit box transparent png.jpg",
     KIT_COLOURS, COIL_OHMS),
    ("Vaporesso XROS 3 Nano", "Vape Kits",
     "Vaporesso Xros 3 Nano kit box transparent png.jpg",
     XROS_COLOURS + POD_OHMS, []),
    ("Vaporesso XROS 4", "Vape Kits",
     "Vaporesso Xros 4 kit box transparent png.jpg",
     XROS_COLOURS + POD_OHMS, []),
    ("Vaporesso XROS Cube", "Vape Kits",
     "Vaporesso Xros Cube kit box transparent png.jpg",
     XROS_COLOURS + POD_OHMS, []),
    ("Vaporesso XROS Pro", "Vape Kits",
     "Vaporesso Xros Pro kit box transparent png.jpg",
     XROS_COLOURS + POD_OHMS, []),
    ("Voopoo Argus P1", "Vape Kits",
     "Voopoo Argus P1 kit box transparent png.jpg",
     KIT_COLOURS + POD_OHMS, []),
    ("Voopoo Argus Pod Kit", "Vape Kits",
     "Voopoo Argus pod kit box transparent png.jpg",
     KIT_COLOURS + POD_OHMS, []),
    ("Voopoo Drag S", "Vape Kits",
     "Voopoo Drag S pod mod kit box transparent png.jpg",
     KIT_COLOURS + ["60W"], COIL_OHMS),
    ("Vuse eTank Mini Starter Kit", "Vape Kits",
     "Vuse eTank Mini starter kit box transparent png.jpg",
     ["Starter kit"], ["Blended Tobacco", "Garden Menthol", "Strawberry Ice", "Golden Tobacco", "Berry Mix"]),
    # --- refills ---
    ("Lost Mary Crystal Pro Pods", "Vape Refills",
     "Hawcos Lost Mary Crystal Pro pods pack transparent png.jpg",
     ["Prefilled pods"], CORE_30),
    ("Hayati Pro Ultra+ 25K Replacement Pods", "Vape Refills",
     "Hayati Pro Ultra Plus 25000 pods pack transparent png.jpg",
     ["25,000 puffs", "Replacement pods"], CORE_30),
    ("Lost Mary BM600 Prefilled Pods", "Vape Refills",
     "Lost Mary BM600 prefilled pod pack transparent png.jpg",
     ["Prefilled pods", "TPD 2ml"], CORE_30),
    ("Smok Arco Replacement Pods", "Vape Refills",
     "Smok Arco replacement pods pack transparent png.jpg",
     POD_OHMS, []),
    # --- e-liquids / shortfills / CBD ---
    ("Bazooka Sour Straws Shortfill", "E-Liquids",
     "Bazooka Sour Straws Green Apple 100ml box transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], BAZOOKA),
    ("Dinner Lady Shortfill", "E-Liquids",
     "Dinner Lady 50ml shortfill bottle transparent png.jpg",
     ["50ml shortfill", "0mg + nic shots"], DINNER_LADY),
    ("DK Cakes Shortfill", "E-Liquids",
     "DK Cakes Victoria Sponge 100ml bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], DK_CAKES),
    ("DK Fruits Shortfill", "E-Liquids",
     "DK Fruits 100ml shortfill bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], DK_FRUITS),
    ("Donut King Shortfill", "E-Liquids",
     "Donut King 100ml shortfill bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], DONUT_KING),
    ("Double Drip Coil Sauce Shortfill", "E-Liquids",
     "Double Drip Coil Sauce 50ml box transparent png.jpg",
     ["50ml shortfill", "0mg + nic shots"], DOUBLE_DRIP),
    ("Elegant CBD 1000mg Oil", "E-Liquids",
     "Elegant CBD 1000mg 60ml lemon bottle transparent png.jpg",
     ["1000mg", "60ml"], CBD_FLAVOURS),
    ("JB Juice Bar Shortfill", "E-Liquids",
     "JB Juice Bar 100ml shortfill bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], JB_JUICE),
    ("Lost Mary 5mg Nic Salts", "E-Liquids",
     "Lost Mary 5mg nic salt box transparent png.jpg",
     ["10ml", "5mg"], LOST_MARY_5MG),
    ("Nic Drip Nic Salts", "E-Liquids",
     "Nic Drip salts 10ml bottle transparent png.jpg",
     ["10ml", "10mg / 20mg"], NIC_DRIP),
    ("Ohm Brew Badass Blends Shortfill", "E-Liquids",
     "Ohm Brew Badass Blends 50ml bottle transparent png.jpg",
     ["50ml shortfill", "0mg + nic shots"], OHM_BREW),
    ("Puff Stuff Shortfill", "E-Liquids",
     "Puff Stuff British Tobacco 100ml bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], PUFF_STUFF),
    ("SKE Crystal Nic Salts", "E-Liquids",
     "SKE Crystal salts 10ml box transparent png.jpg",
     ["10ml", "10mg / 20mg"], SKE_CRYSTAL),
    ("Strapped Soda Shortfill", "E-Liquids",
     "Strapped Soda Proper Punch 100ml bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], STRAPPED),
    ("Tasty Fruity Shortfill", "E-Liquids",
     "Tasty Fruity 120ml shortfill bottle transparent png.jpg",
     ["120ml shortfill", "0mg + nic shots"], TASTY_FRUITY),
    ("Vapour Life Shortfill", "E-Liquids",
     "Vapour Life 100ml shortfill bottle transparent png.jpg",
     ["100ml shortfill", "0mg + nic shots"], VAPOUR_LIFE),
    ("Vitality CBD Oral Drops", "E-Liquids",
     "Vitality CBD oral drops box transparent png.jpg",
     ["Oral drops"], VITALITY_CBD),
]

SKIP_NEW_IF_NAME_CONTAINS = [
    "ivg 2400",
    "ivg pro 12",
    "ivg pro refill",
    "elf bar elfliq",
    "lost mary maryliq",
    "pod salt core",
    "pod salt origin",
]


def existing_name_blob(products):
    return " | ".join(p["name"].lower() for p in products)


def main():
    products = load_products()
    original = len(products)

    cleaned = []
    dropped = []
    for p in products:
        if p["name"] in DROP_NAMES:
            dropped.append(p["name"])
            continue
        old_name = p["name"]
        p["name"] = polish_title(old_name)
        cat = MOVE_TO.get(p["name"]) or MOVE_TO.get(old_name)
        if cat:
            p["category"] = cat
        p["flavors"] = flavour_merge_for(p["name"], p.get("flavors") or [])
        if p.get("variants"):
            p["variants"] = [re.sub(r"\s+", " ", str(v)).strip() for v in p["variants"]]
        cleaned.append(p)

    # de-dupe identical name+category after rename
    seen = set()
    unique = []
    for p in cleaned:
        key = (p["name"].lower(), p["category"])
        if key in seen:
            dropped.append(p["name"] + " (dup)")
            continue
        seen.add(key)
        unique.append(p)

    blob = existing_name_blob(unique)
    added = []
    skipped = []
    for name, category, filename, variants, flavors in NEW_PRODUCTS:
        needle = name.lower()
        # skip photographed dupes of live cards
        skip = False
        for token in SKIP_NEW_IF_NAME_CONTAINS:
            if token in filename.lower() or token in needle:
                skip = True
        if "pod salt core 10ml" in filename.lower() or "pod salt origin cuban" in filename.lower():
            skip = True
        if "elfliq 10ml" in filename.lower():
            skip = True
        if "maryliq 10ml" in filename.lower():
            skip = True
        if skip:
            skipped.append(name)
            continue
        if name.lower() in blob:
            skipped.append(name + " (already live)")
            continue
        src = SRC_NEW / filename
        if not src.exists():
            skipped.append(name + " (missing image)")
            continue
        image = copy_new(filename)
        unique.append(card(name, category, image, variants, merge_flavors(flavors)))
        added.append(name)
        blob += " | " + name.lower()

    write_products(unique)

    cats = {}
    for p in unique:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    print("original", original)
    print("final", len(unique))
    print("dropped", dropped)
    print("added", added)
    print("skipped", skipped)
    print("categories", cats)


if __name__ == "__main__":
    main()
