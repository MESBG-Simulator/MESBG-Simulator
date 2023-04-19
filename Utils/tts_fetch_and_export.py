import subprocess
from pathlib import Path


if __name__ == '__main__':
    tts_path = Path(Path.home(), 'OneDrive', 'Documents', 'My Games', 'Tabletop Simulator')
    json_dir_path = Path(tts_path, 'Mods', 'Workshop')
    json_filename_list = ['2078698608.json', '2051317170.json', '2078610179.json', '2078618079.json']
    json_file_path_list = [Path(json_dir_path, x) for x in json_filename_list]
    zip_dir_path = Path(Path.home(), 'OneDrive', 'Gaming', 'MESBG', 'MESBG-Simulator', 'Models')
    zip_filename_list = ['mesbg_models_lotr_good.zip', 'mesbg_models_lotr_evil.zip', 'mesbg_models_hobbit_good.zip', 'mesbg_models_hobbit_evil.zip']
    zip_file_path_list = [Path(zip_dir_path, x) for x in zip_filename_list]
    # out_root = 
    for json_file_path, zip_file_path in zip(json_file_path_list, zip_file_path_list):
        subprocess.call(['tts-prefetch', json_file_path, '--gamedata', str(tts_path)])
        subprocess.call(['tts-backup', json_file_path, '--gamedata', str(tts_path), '-o', str(zip_file_path)])
