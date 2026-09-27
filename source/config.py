import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "your_token")
PAWN_DIR = "/pawn-compiler"
PAWNO_DIR = os.path.join(PAWN_DIR, "pawno")
PAWNCC_PATH = os.path.join(PAWNO_DIR, "pawncc")
DISASM_PATH = os.path.join(PAWNO_DIR, "pawndisasm")
INCLUDE_DIR = os.path.join(PAWNO_DIR, "include")
os.makedirs(INCLUDE_DIR, exist_ok=True)
