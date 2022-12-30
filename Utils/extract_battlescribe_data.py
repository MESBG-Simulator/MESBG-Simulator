import os
import shutil
import json
import json_fix
from bs4 import BeautifulSoup

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


SOURCE_DIR = os.path.join('C:\\Users', os.environ.get('USERNAME'),
                          'BattleScribe\\data\\Middle-Earth Strategy Battle Game')
TARGET_DIR = os.path.join(os.getcwd(), 'Data', 'BattleScribe')
JSON_PATH = os.path.join('Data', 'battlescribe_data.json')


class Model():
    def __init__(self, name='', movement=0, fight=0, shoot=0, strength=0, defense=0, attack_fight=0, wounds=0, courage=0, keywords='') -> None:
        self.name = name
        self.movement = movement
        self.fight = fight
        self.shoot = shoot
        self.strength = strength
        self.defense = defense
        self.attack = attack_fight
        self.wounds = wounds
        self.courage = 0
        self.keywords = ''


class Hero(Model):
    def __init__(self, name='', movement=0, fight=0, shoot=0, strength=0, defense=0, attack=0, wounds=0, courage=0, might=0, fate=0, will=0):
        self.name = name
        self.movement = movement
        self.fight = fight
        self.shoot = shoot
        self.strength = strength
        self.defense = defense
        self.attack = attack
        self.wounds = wounds
        self.courage = courage
        self.might = might
        self.will = will
        self.fate = fate
        self.keywords = ''

    def __json__(self):
        return self.__dict__


class RosterCrawler():
    def __init__(self, in_file, master_roster=None):
        self.in_file = in_file
        self.master_roster = master_roster

    def read_roster(self):
        with open(self.in_file, encoding='utf-8') as f:
            data = f.read()
            bs_data = BeautifulSoup(data, 'xml')
        if not self.master_roster:
            roster = Roster('Master Roster')
        else:
            cat_tag = bs_data.find('catalogue')
            roster = Roster(cat_tag.get('name'))

        hero_tags = bs_data.find_all('profile', {'typeName': 'Hero'})
        for hero_tag in hero_tags:
            h = Hero(name=hero_tag.get('name'))
            print(roster.name, '->', h.name)
            characteristics_tag = hero_tag.find('characteristics')
            characteristics_list = ['movement', 'fight', 'strength', 'defense',
                                    'attack', 'wounds', 'courage', 'might', 'will', 'fate']

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
                        if value[0] == '?':
                            h.fight = -1
                            h.shoot = -1
                        else:
                            h.fight = int(value[0])
                            h.shoot = int(value[1][0])
                    else:
                        setattr(h, characteristic, value)

            except IndexError:
                pass
            
            roster.add_hero(h)

        if self.master_roster:
            all_entryLink_tags = bs_data.find_all('entryLink')
            for entryLink_tag in all_entryLink_tags:
                hero_name = entryLink_tag.get('name')
                if hero_name in self.master_roster.heroes.keys():
                    h = self.master_roster.heroes[hero_name]
                    roster.add_hero(h)

        return roster


class Roster():
    def __init__(self, name):
        self.name = name
        self.heroes = {}

    def add_hero(self, hero):
        print(f'Adding {hero.name} to {self.name}')
        self.heroes[hero.name] = hero

    def get_json(self):
        return json.dumps({self.name: self.heroes})

    def __json__(self):
        return self.get_json()


def list_all_files(file_dir=SOURCE_DIR):
    for f_name in os.listdir(file_dir):
        print(f_name)


def unzip_all_files(src_dir=SOURCE_DIR, tgt_dir=TARGET_DIR):
    for f_name in os.listdir(src_dir):
        shutil.unpack_archive(os.path.join(src_dir, f_name), tgt_dir, 'zip')


def build_rosters():
    rosters = []
    master_roster_name = 'Middle-Earth_Strategy_Battle_Game.gst'
    rc = RosterCrawler(os.path.join(TARGET_DIR, master_roster_name))
    master_roster = rc.read_roster()
    for f_name in os.listdir(os.path.join(TARGET_DIR)):
        if f_name != master_roster_name:
            rc = RosterCrawler(os.path.join(TARGET_DIR, f_name), master_roster)
            roster = rc.read_roster()
            rosters.append({'name': roster.name, 'heroes': roster.heroes})

    return json.dumps(rosters, indent=4, sort_keys=True)


if __name__ == '__main__':
    unzip_all_files()
    out_json = build_rosters()
    with open(JSON_PATH, 'w') as f:
        f.write(out_json)
