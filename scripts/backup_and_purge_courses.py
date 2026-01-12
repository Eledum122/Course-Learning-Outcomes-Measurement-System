import os
import zipfile
import datetime
import glob

SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses')
DEST_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'backups')
SRC_DIR = os.path.abspath(SRC_DIR)
DEST_DIR = os.path.abspath(DEST_DIR)

os.makedirs(DEST_DIR, exist_ok=True)

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
zip_path = os.path.join(DEST_DIR, f'courses_backup_{ts}.zip')

files = glob.glob(os.path.join(SRC_DIR, '*.json'))
count = 0
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        zf.write(f, os.path.basename(f))
        count += 1

# remove files only if any were added to zip
if count > 0:
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to remove {f}: {e}")

print(f"Deleted {count} files")
print(f"Backup created: {zip_path}")
