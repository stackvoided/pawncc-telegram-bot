# Pawn Compiler & Decompiler Bot

A high-performance asynchronous Telegram bot built with Python (**aiogram 3.x**) for compiling and decompiling Pawn scripts (`.pwn` / `.amx`) directly via a messaging interface.

Tailored for SA-MP, CR-MP, and open.mp server developers who need fast script builds and seamless dependency management on a Linux host.

## Key Features ⚡

- **One-Click Build & Decompile**
  - `.pwn` ➔ `.amx` (Compilation via `pawncc`)
  - `.amx` ➔ `.pwn` (Disassembly / code recovery)
- **Batch Include Manager (`/include`)**
  - Multi-file `.inc` upload straight into the compiler's include directory without breaking state flow.
- **Privacy & Clean Output**
  - Temporary source code and binary files are immediately deleted upon completion.
  - Absolute server directory paths are automatically stripped from compilation logs — users only see filenames and line numbers.
- **Smart Navigation**
  - Invalid commands automatically invoke an interactive inline menu to keep user workflows uninterrupted.

## System Requirements 🛠

- **OS:** Linux (x86 / x86_64 with 32-bit architecture support like `ia32-libs` or `lib32stdc++6` required by `pawncc`).
- **Python:** 3.10+
- **Dependencies:** `aiogram >= 3.0.0`

## Project Structure 📂

```text
pawn_compiler_bot/
├── config.py         # Path configurations and environment variables
├── compiler.py       # Subprocess wrapper for pawncc and disasm
├── handlers.py       # Command, document, and FSM handlers
├── keyboards.py      # Inline keyboard layouts
├── bot.py             # Entry point and async event loop
└── requirements.txt
```

## 🚀 Quick Start

### 1. Prepare Pawn Environment

Ensure your `pawncc` binary is executable and located in the configured path (default: `/pawn-compiler/pawno/`):

```bash
chmod +x /pawn-compiler/pawno/pawncc
```

### 2. Install Dependencies

```bash
git clone https://github.com/your-username/pawn-compiler-bot.git
cd pawn-compiler-bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuration & Run

Set your Telegram Bot Token in `config.py` or export it as an environment variable:

```bash
export BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyZ"
python bot.py
```

## 🤖 Usage

| Command | Description |
|---|---|
| `/gamemodes` | Waits for a `.pwn` file (for compilation) or an `.amx` file (for decompilation). |
| `/include` | Enables batch mode to upload custom `.inc` dependencies into `pawno/include/`. |

Sending an invalid or unrecognized command will bring up the interactive main menu.
