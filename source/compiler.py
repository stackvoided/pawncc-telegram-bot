import asyncio
import os
import shutil
import tempfile
from config import PAWN_DIR, PAWNO_DIR, PAWNCC_PATH, DISASM_PATH

def sanitize_logs(text: str) -> str:
    if not text:
        return ""
    text = text.replace(PAWN_DIR + "/", "").replace(PAWN_DIR, "")
    text = text.replace(PAWNO_DIR + "/", "").replace(PAWNO_DIR, "")
    return text

async def compile_pawn(source_path: str, filename_no_ext: str) -> tuple[bool, str, str | None]:
    temp_dir = tempfile.mkdtemp()
    target_pwn = os.path.join(temp_dir, f"{filename_no_ext}.pwn")
    target_amx = os.path.join(temp_dir, f"{filename_no_ext}.amx")
    
    shutil.copyfile(source_path, target_pwn)

    cmd = f"LD_LIBRARY_PATH=. {PAWNCC_PATH} \"{target_pwn}\" -o\"{target_amx}\""

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PAWNO_DIR
    )

    stdout, stderr = await proc.communicate()
    
    raw_logs = stdout.decode('cp1251', errors='replace') + stderr.decode('cp1251', errors='replace')
    clean_logs = sanitize_logs(raw_logs.strip())

    amx_exists = os.path.exists(target_amx) and os.path.getsize(target_amx) > 0

    if amx_exists:
        out_amx_path = os.path.join(os.path.dirname(source_path), f"{filename_no_ext}.amx")
        shutil.move(target_amx, out_amx_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True, clean_logs, out_amx_path

    shutil.rmtree(temp_dir, ignore_errors=True)
    return False, clean_logs, None

async def decompile_pawn(source_path: str, filename_no_ext: str) -> tuple[bool, str, str | None]:
    temp_dir = tempfile.mkdtemp()
    target_amx = os.path.join(temp_dir, f"{filename_no_ext}.amx")
    target_pwn = os.path.join(temp_dir, f"{filename_no_ext}.pwn")
    
    shutil.copyfile(source_path, target_amx)

    if os.path.exists(DISASM_PATH):
        cmd = f"LD_LIBRARY_PATH=. {DISASM_PATH} \"{target_amx}\" \"{target_pwn}\""
    else:
        cmd = f"LD_LIBRARY_PATH=. {PAWNCC_PATH} \"{target_amx}\" -o\"{target_pwn}\" -d3"

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PAWNO_DIR
    )

    stdout, stderr = await proc.communicate()
    
    raw_logs = stdout.decode('cp1251', errors='replace') + stderr.decode('cp1251', errors='replace')
    clean_logs = sanitize_logs(raw_logs.strip())

    pwn_exists = os.path.exists(target_pwn) and os.path.getsize(target_pwn) > 0

    if pwn_exists:
        out_pwn_path = os.path.join(os.path.dirname(source_path), f"{filename_no_ext}_decompiled.pwn")
        shutil.move(target_pwn, out_pwn_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True, clean_logs, out_pwn_path

    shutil.rmtree(temp_dir, ignore_errors=True)
    return False, clean_logs, None
