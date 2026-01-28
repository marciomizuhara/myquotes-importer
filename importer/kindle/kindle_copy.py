import shutil
import time
from pathlib import Path
import win32com.client

from importer.config import INPUT_DIR, INPUT_FILE, BACKUP_DIR


def find_kindle_file():
    print("🔍 Procurando o Kindle conectado...")

    possible_drives = [f"{chr(c)}:" for c in range(65, 91)]
    for drive in possible_drives:
        kindle_path = Path(f"{drive}\\documents\\My Clippings.txt")
        if kindle_path.exists():
            print(f"📗 Kindle detectado via unidade ({drive})")
            return kindle_path

    shell = win32com.client.Dispatch("Shell.Application")
    for item in shell.NameSpace(17).Items():
        if "Kindle" in item.Name:
            print(f"📘 Kindle detectado via MTP: {item.Name}")
            try:
                kindle_ns = item.GetFolder
                docs_folder = kindle_ns.ParseName("Internal storage").GetFolder
                documents = docs_folder.ParseName("documents").GetFolder
                my_clippings = documents.ParseName("My Clippings.txt")
                if my_clippings:
                    print("✅ Arquivo My Clippings.txt encontrado (modo MTP)!")
                    return my_clippings
            except Exception:
                pass

    print("⚠️ Kindle não encontrado.")
    return None


def copy_from_kindle():
    print("📥 Iniciando obtenção do My Clippings.txt...\n")
    print(f"📌 INPUT_DIR = {INPUT_DIR}")
    print(f"📌 INPUT_FILE = {INPUT_FILE}")
    print(f"📌 BACKUP_DIR = {BACKUP_DIR}\n")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    backup_path = BACKUP_DIR / "My Clippings.txt"

    kindle_item = find_kindle_file()

    # ─────────────────────────────────────────────
    # 🟢 CASO 1: Kindle conectado → usar Kindle
    # ─────────────────────────────────────────────
    if kindle_item:
        try:
            if isinstance(kindle_item, Path):
                shutil.copy2(kindle_item, INPUT_FILE)
                shutil.copy2(kindle_item, backup_path)
                print(f"✅ Copiado via unidade: {kindle_item}")

            else:
                shell = win32com.client.Dispatch("Shell.Application")
                target_ns = shell.NameSpace(str(INPUT_DIR))

                print("📄 Copiando via MTP (isso pode levar alguns segundos)...")
                target_ns.CopyHere(kindle_item, 16)

                found = None
                for _ in range(30):  # ~15s
                    candidates = list(INPUT_DIR.glob("My Clippings*.txt"))
                    if candidates:
                        found = max(candidates, key=lambda p: p.stat().st_mtime)
                        break
                    time.sleep(0.5)

                if not found or not found.exists():
                    raise FileNotFoundError("Falha ao copiar via MTP (arquivo não apareceu no INPUT_DIR)")

                if found.resolve() != INPUT_FILE.resolve():
                    if INPUT_FILE.exists():
                        INPUT_FILE.unlink()
                    found.replace(INPUT_FILE)

                shutil.copy2(INPUT_FILE, backup_path)

            print(f"✅ Backup atualizado em: {backup_path}")
            print(f"✅ Arquivo atualizado no INPUT_DIR: {INPUT_FILE}")
            print("📚 Usando arquivo do Kindle.\n")
            return True

        except Exception as e:
            print(f"❌ Erro ao copiar do Kindle: {e}")
            return False

    # ─────────────────────────────────────────────
    # 🟡 CASO 2: Kindle ausente → usar BACKUP
    # ─────────────────────────────────────────────
    if backup_path.exists():
        try:
            shutil.copy2(backup_path, INPUT_FILE)
            print("📂 Kindle não conectado.")
            print(f"✅ Usando backup existente: {backup_path}")
            print(f"✅ Arquivo copiado para INPUT_DIR: {INPUT_FILE}")
            print("📚 Prosseguindo com arquivo de backup.\n")
            return True
        except Exception as e:
            print(f"❌ Erro ao usar backup: {e}")
            return False

    # ─────────────────────────────────────────────
    # 🔴 CASO 3: Nenhuma fonte disponível
    # ─────────────────────────────────────────────
    print("❌ Nenhum Kindle conectado e nenhum backup encontrado.")
    print("➡️ Conecte o Kindle ou forneça um My Clippings.txt no BACKUP_DIR.")
    return False
