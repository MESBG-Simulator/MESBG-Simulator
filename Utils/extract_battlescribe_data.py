import os
import shutil
import json
import typing
import json_fix
from bs4 import BeautifulSoup
from pathlib import Path

# notes:
# get roster name from catalogue node, name attribute

# search dom trees for selectionEntry
# check for child node profiles and profile id
#   from profile id, check for type=hero
#   if type=hero, register name and add hero
# if there is no profile child node, search for entryLinks and entryLink
#   use the name attribute in entryLink
#   check masterRoster for hero with same name
#   if name is found, add the hero

ROOT_DIR = Path('.').absolute()
SOURCE_DIR = Path(Path.home(), 'BattleScribe\\data\\Middle-Earth Strategy Battle Game')
TARGET_DIR = Path(ROOT_DIR, 'Data', 'BattleScribe')
JSON_PATH1 = Path(ROOT_DIR, 'Data', 'battlescribe_data_1.json')
JSON_PATH2 = Path(ROOT_DIR, 'Data', 'battlescribe_data_2.json')


class Warrior():
    def __init__(self) -> None:
        self.name = ''
        self.movement = -1
        self.fight = -1
        self.shoot = -1
        self.strength = -1
        self.defense = -1
        self.attack = -1
        self.wounds = -1
        self.courage = -1
        self.keywords = ''

    def __json__(self):
        return self.__dict__


class Hero(Warrior):
    def __init__(self):
        self.name = ''
        self.movement = -1
        self.fight = -1
        self.shoot = -1
        self.strength = -1
        self.defense = -1
        self.attack = -1
        self.wounds = -1
        self.courage = -1
        self.might = -1
        self.will = -1
        self.fate = -1
        self.keywords = ''


class Roster():
    def __init__(self, name):
        self.name = name
        self.heroes = {}
        self.warriors = {}
        self.profiles_schema_db = {}
        self.profiles_db = {}

    def add_hero(self, hero):
        print(f'Adding {hero.name} to {self.name}')
        self.heroes[hero.name] = hero

    def add_warrior(self, warrior):
        print(f'Adding {warrior.name} to {self.name}')
        self.warriors[warrior.name] = warrior

    def get_json(self):
        return json.dumps({self.name: self.heroes})

    def __json__(self):
        return self.get_json()


class RosterCrawler():
    def __init__(self, in_file, master_roster: typing.Optional[Roster]=None):
        self.in_file = in_file
        self.master_roster = master_roster
        self.warrior_characteristics_list = ['movement', 'fight', 'strength', 'defense',
                                             'attack', 'wounds', 'courage']
        self.hero_characteristics_list = ['movement', 'fight', 'strength', 'defense',
                                          'attack', 'wounds', 'courage', 'might', 'will', 'fate']

    def characteristics_filler(self, model_tag, model=Warrior):
        if isinstance(model, Hero):
            characteristics_list = self.hero_characteristics_list
        else:
            characteristics_list = self.warrior_characteristics_list

        model.name = model_tag.get('name')

        characteristics_tag = model_tag.find('characteristics')
        try:
            for characteristic in characteristics_list:
                characteristic_tag = characteristics_tag.find(
                    'characteristic', {'name': characteristic.capitalize()})
                value = characteristic_tag.contents[0]
                try:
                    value = int(value)
                except:
                    pass

                if characteristic == 'movement':
                    try:
                        value = int(characteristic_tag.contents[0][:-1])
                    except:
                        value = -1

                if characteristic == 'fight':
                    value = characteristic_tag.contents[0].split('/')
                    if value[0] in ['?', "-"]:
                        model.fight = -1
                        model.shoot = -1
                    else:
                        model.fight = int(value[0])
                        if value[1][0] == '-':
                            model.shoot = -1
                        else:
                            model.shoot = int(value[1][0])
                else:
                    setattr(model, characteristic, value)

        except IndexError:
            pass

    def read_roster(self):

        with open(self.in_file, encoding='utf-8') as f:
            data = f.read()
            bs_data = BeautifulSoup(data, 'xml')

        if not self.master_roster:
            roster = Roster('Master Roster')

            # Here we create a DataBase of profile types and the characteristics they contain
            # This is only done in the master roaster reading phase
            roster.profiles_schema_db = {}
            for profile_type in bs_data.find_all('profileType'):
                profile_db = {'characteristics': [x['name'] for x in profile_type.find_all('characteristicType')]}
                roster.profiles_schema_db[profile_type['name']] = profile_db
        else:
            cat_tag = bs_data.find('catalogue')
            roster = Roster(cat_tag.get('name'))
            roster.profiles_schema_db = self.master_roster.profiles_schema_db

        roster.profiles_db = {}
        for profile_name in roster.profiles_schema_db:
            profile_characteristics = roster.profiles_schema_db[profile_name]['characteristics']
            profile_db_list = []
            for profile_tag in bs_data.find_all('profile', {'typeName': profile_name}):
                profile_db = {'name': profile_tag.get('name')}
                characteristics_tag = profile_tag.find('characteristics')
                for profile_characteristic in profile_characteristics:
                    characteristic_tag = characteristics_tag.find('characteristic', {'name': profile_characteristic})
                    if len(characteristic_tag.contents):
                        profile_db[profile_characteristic] = characteristic_tag.contents[0]
                profile_db_list.append(profile_db)
            roster.profiles_db[profile_name] = profile_db_list

        warrior_tags = bs_data.find_all('profile', {'typeName': 'Warrior'})
        for warrior_tag in warrior_tags:
            w = Warrior()
            self.characteristics_filler(warrior_tag, w)
            roster.add_warrior(w)

        hero_tags = bs_data.find_all('profile', {'typeName': 'Hero'})
        for hero_tag in hero_tags:
            h = Hero()
            self.characteristics_filler(hero_tag, h)
            roster.add_hero(h)

        if self.master_roster:
            all_entryLink_tags = bs_data.find_all('entryLink')
            for entryLink_tag in all_entryLink_tags:
                
                miniature_name = entryLink_tag.get('name')
                if miniature_name in self.master_roster.heroes.keys():
                    h = self.master_roster.heroes[miniature_name]
                    roster.add_hero(h)
                elif miniature_name in self.master_roster.warriors.keys():
                    w = self.master_roster.warriors[miniature_name]
                    roster.add_warrior(w)
                
                # for profile_type in self.master_roster.profiles_db:
                #     if miniature_name in self.master_roster.profiles_db[profile_type].keys():
                #         break


        return roster





def list_all_files(file_dir=SOURCE_DIR):
    for f_name in os.listdir(file_dir):
        print(f_name)


def unzip_all_files(src_dir=SOURCE_DIR, tgt_dir=TARGET_DIR):
    for f_name in os.listdir(src_dir):
        shutil.unpack_archive(Path(src_dir, f_name), tgt_dir, 'zip')


def build_rosters():
    rosters = []
    rosters_db = []
    master_roster_path = Path(TARGET_DIR, 'Middle-Earth_Strategy_Battle_Game.gst')
    master_roster_crawler = RosterCrawler(master_roster_path)
    master_roster = master_roster_crawler.read_roster()
    rosters_db.append({master_roster.name: master_roster.profiles_db})
    for catalogue_path in TARGET_DIR.glob('*.cat'):
        catalogue_roster_crawler = RosterCrawler(Path(TARGET_DIR, catalogue_path), master_roster)
        catalogue_roster = catalogue_roster_crawler.read_roster()
        rosters.append({'name': catalogue_roster.name, 'heroes': catalogue_roster.heroes,
                       'warriors': catalogue_roster.warriors})
        rosters_db.append({catalogue_roster.name: catalogue_roster.profiles_db})

    return json.dumps(rosters, indent=4), json.dumps(rosters_db, indent=4)


if __name__ == '__main__':
    unzip_all_files()
    out_json1, out_json2 = build_rosters()
    with open(JSON_PATH1, 'w') as f:
        f.write(out_json1)
    with open(JSON_PATH2, 'w') as f:
        f.write(out_json2)
