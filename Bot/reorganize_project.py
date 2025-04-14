import os
import shutil
import re
from datetime import datetime

ROOT_DIR = os.getcwd()
BOT_DIR = os.path.join(ROOT_DIR, 'bot')
BACKUP_DIR = os.path.join(ROOT_DIR, 'backup_py_files')
EXCLUDE_FILES = {'main.py', 'app.py', 'reorganize_project.py'}

# Step 1: Create necessary folders
os.makedirs(BOT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Step 2: Move and back up Python logic files into bot/
internal_modules = set()
for file in os.listdir(ROOT_DIR):
    if file.endswith('.py') and file not in EXCLUDE_FILES:
        module_name = file.replace('.py', '')
        internal_modules.add(module_name)

        src = os.path.join(ROOT_DIR, file)
        dst = os.path.join(BOT_DIR, file)
        shutil.copy2(src, os.path.join(BACKUP_DIR, file))  # backup
        shutil.move(src, dst)
        print(f"📦 Moved and backed up: {file}")

# Step 3: Ensure bot/ is a package
init_file = os.path.join(BOT_DIR, '__init__.py')
if not os.path.exists(init_file):
    open(init_file, 'w').close()
    print("🔧 Created __init__.py to make 'bot' a package")


# Step 4: Update imports in app.py and main.py
def update_imports(file_path, module_names):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        original_line = line
        for mod in module_names:
            if re.search(rf'\bfrom {mod}\b', line):
                line = line.replace(f'from {mod}', f'from bot.{mod}')
            elif re.search(rf'\bimport {mod}\b', line):
                line = line.replace(f'import {mod}', f'import bot.{mod}')
        new_lines.append(line)
        if original_line != line:
            print(f"🔄 Updated import: {original_line.strip()} → {line.strip()}")

    # Backup and save
    backup_name = f"{os.path.basename(file_path)}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(file_path, os.path.join(BACKUP_DIR, backup_name))

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"✅ Imports updated in {os.path.basename(file_path)}")


# Apply updates to main.py and app.py
for target in ['main.py', 'app.py']:
    path = os.path.join(ROOT_DIR, target)
    if os.path.exists(path):
        update_imports(path, internal_modules)

print("\n🚀 Project successfully restructured and import-safe.")
