import os
import shutil

appdata_path = os.path.join(os.environ.get('APPDATA', ''), 'MetaQuotes', 'Terminal')
if os.path.exists(appdata_path):
    for folder_name in os.listdir(appdata_path):
        folder_path = os.path.join(appdata_path, folder_name)
        if len(folder_name) == 32 and os.path.isdir(folder_path):
            cache_dir = os.path.join(folder_path, "Tester", "cache")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
                print(f"Cleared {cache_dir}")
