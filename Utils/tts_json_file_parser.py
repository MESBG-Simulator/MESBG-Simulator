import json
from pathlib import Path
import pandas as pd


if __name__ == '__main__':
    tts_path = Path(Path.home(), 'OneDrive', 'Documents', 'My Games', 'Tabletop Simulator')
    json_dir_path = Path(tts_path, 'Mods', 'Workshop')
    json_filename_list = ['2078698608.json', '2051317170.json', '2078610179.json', '2078618079.json']
    json_filename_list = ['2078698608.json']
    json_file_path_list = [Path(json_dir_path, x) for x in json_filename_list]

    # zip_filename_list = ['mesbg_models_lotr_good.zip', 'mesbg_models_lotr_evil.zip', 'mesbg_models_hobbit_good.zip', 'mesbg_models_hobbit_evil.zip']
    for json_file_path in json_file_path_list:
        print(json_file_path)
        with json_file_path.open('r') as f:
            data = json.load(f)
            df = pd.json_normalize(data['ObjectStates'])
