from BaseClasses import Item
from .game_id import jak2_name, jak2_max

class Jak2Item(Item):
    game: str = jak2_name

class Jak2ItemData:
    id: int
    name: str
    symbol: str
    
    def __init__(self, item_id: int, name: str, symbol: str) -> None:
        self.item_id = item_id
        self.name = name
        self.symbol = symbol

# ID Range Constants for Item Classification
# These constants define the boundaries for different item types
ITEM_ID_KEY_START = 1           # Key/progression items start at ID 1
ITEM_ID_KEY_END = 33            # Key/progression items end at ID 33
ITEM_ID_FILLER_START = 34       # Filler items start at ID 34 (Dark Eco Pill)
ITEM_ID_FILLER_END = 50         # Standard filler items end here (room for expansion)

# Unified Item Table - Single source of truth for all items
# Every item is organized by classification using ID ranges defined above
item_table = {
    # ========== KEY/PROGRESSION ITEMS (IDs 1-33) ==========
    
    # Morph Gun Weapons and Upgrades (IDs 1-7)
    1: Jak2ItemData(item_id=1, name="Scatter Gun", symbol="gun-red"),
    2: Jak2ItemData(item_id=2, name="Blaster", symbol="gun-yellow"),
    3: Jak2ItemData(item_id=3, name="Vulcan Fury", symbol="gun-blue"),
    4: Jak2ItemData(item_id=4, name="Peacemaker", symbol="gun-dark"),
    5: Jak2ItemData(item_id=5, name="Morph Gun Ammo Upgrade", symbol="gun-upgrade-ammo"),
    6: Jak2ItemData(item_id=6, name="Morph Gun Fire Rate Upgrade", symbol="gun-upgrade-speed"),
    7: Jak2ItemData(item_id=7, name="Morph Gun Damage Upgrade", symbol="gun-upgrade-damage"),
    
    # Movement Items (IDs 8)
    8: Jak2ItemData(item_id=8, name="JET-Board", symbol="board"),
    
    # Dark Jak Powers (IDs 9-13)
    9: Jak2ItemData(item_id=9, name="Dark Jak", symbol="darkjak"),
    10: Jak2ItemData(item_id=10, name="Dark Bomb", symbol="darkjak-bomb0"),
    11: Jak2ItemData(item_id=11, name="Dark Blast", symbol="darkjak-bomb1"),
    12: Jak2ItemData(item_id=12, name="Dark Giant", symbol="darkjak-giant"),
    13: Jak2ItemData(item_id=13, name="Dark Invincibility", symbol="darkjak-invinc"),
    
    # Security Passes (IDs 14-19)
    14: Jak2ItemData(item_id=14, name="Red Security Pass", symbol="pass-red"),
    15: Jak2ItemData(item_id=15, name="Yellow Security Pass", symbol="pass-yellow"),
    16: Jak2ItemData(item_id=16, name="Green Security Pass", symbol="pass-green"),
    17: Jak2ItemData(item_id=17, name="Purple Security Pass", symbol="pass-purple"),
    18: Jak2ItemData(item_id=18, name="Black Security Pass", symbol="pass-black"),
    19: Jak2ItemData(item_id=19, name="Air Train Pass", symbol="pass-air-train"),
    
    # Mountain Temple Items (IDs 20-22)
    20: Jak2ItemData(item_id=20, name="Lens", symbol="lens"),
    21: Jak2ItemData(item_id=21, name="Gear", symbol="gear"),
    22: Jak2ItemData(item_id=22, name="Shard", symbol="shard"),
    
    # Miscellaneous Important Items (IDs 23-33)
    23: Jak2ItemData(item_id=23, name="Ruby Key", symbol="ruby-key"),
    24: Jak2ItemData(item_id=24, name="Heart of Mar", symbol="heart-of-mar"),
    25: Jak2ItemData(item_id=25, name="Time Map", symbol="time-map"),
    26: Jak2ItemData(item_id=26, name="Precursor Stone", symbol="precursor-stone"),
    27: Jak2ItemData(item_id=27, name="Life Seed", symbol="life-seed"),
    28: Jak2ItemData(item_id=28, name="Titan Suit", symbol="titan-suit"),
    29: Jak2ItemData(item_id=29, name="Gunpod", symbol="gun-turret"),
    30: Jak2ItemData(item_id=30, name="Seal Piece #1", symbol="seal-piece-1"),
    31: Jak2ItemData(item_id=31, name="Seal Piece #2", symbol="seal-piece-2"),
    32: Jak2ItemData(item_id=32, name="Seal Piece #3", symbol="seal-piece-3"),
    33: Jak2ItemData(item_id=33, name="Rift Rider", symbol="rift-rider"),
    
    # ========== FILLER ITEMS ==========
    # Standard Filler Items (IDs 34+)
    34: Jak2ItemData(item_id=34, name="Dark Eco Pill", symbol="dark-eco-pill"),
    35: Jak2ItemData(item_id=35, name="Health Pack", symbol="health-pack"),
    36: Jak2ItemData(item_id=37, name="Scatter Gun Ammo", symbol="ammo-red"),
    37: Jak2ItemData(item_id=38, name="Blaster Ammo", symbol="ammo-yellow"),
    38: Jak2ItemData(item_id=39, name="Vulcan Fury Ammo", symbol="ammo-blue"),
    39: Jak2ItemData(item_id=40, name="Peacemaker Ammo", symbol="ammo-dark")
}