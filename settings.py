import json
from datetime import time
from typing import *

import auto_van
import location
import main
import schedule
import van


class Settings:
    json_indent = 4

    settings_path = 'data/settings.json'

    settings = json.load(open(settings_path, 'r', encoding='utf-8'))

    token: str = settings['token']

    alias_path: str = settings['alias_path']
    vans_path: str = settings['vans_path']
    auto_van_path: str = settings['auto_van_path']
    schedule_path: str = settings['schedule_path']

    quotes_done_path: str = settings['quotes_done_path']
    quotesirl_path: str = settings['quotesirl_path']

    buffalo_path: str = settings['buffalo_path']

    log_path: str = settings['log_path']

    van_emojis: List[str] = settings['van_emojis']
    floor_emojis: List[List[str]] = settings['floor_emojis']

    locations: Dict[str | None, location.Location] = {i[0]: location.Location(i[1], i[2]) for i in
                                                      settings['locations']}

    ch_van_holds: int = settings['ch_van_holds']
    ch_chat_games: int = settings['ch_chat_games']
    ch_botspam: int = settings['ch_botspam']
    ch_people_visiting: int = settings['ch_people_visiting']

    quotes_time = time.fromisoformat(settings['quotes_time'])

    quotesirl_link: str = settings['quotesirl_link']

    aliases: Dict[int, str] = {}

    @classmethod
    def load_aliases(cls):
        try:
            with open(cls.alias_path, 'r') as f:
                data = json.load(f)
                cls.aliases = {int(k): v for k, v in data.items()}
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass

    @classmethod
    def add_alias(cls, user_id, name):
        cls.load_aliases()

        cls.aliases[user_id] = name

        with open(cls.alias_path, 'w+') as f:
            json.dump(cls.aliases, f, indent=cls.json_indent)

    @classmethod
    def get_alias(cls, user_id):
        cls.load_aliases()

        return cls.aliases.get(user_id)

    @classmethod
    def load_vans(cls, bot: main.Pardina) -> List[van.Van]:
        vans = []

        try:
            with open(cls.vans_path, 'r') as f:
                data = json.load(f)
                for i in data:
                    vans.append(van.Van.deserialize(bot, i))
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass

        return vans

    @classmethod
    def save_vans(cls, vans: List[van.Van]):
        with open(cls.vans_path, 'w+') as f:
            json.dump([i.serialize() for i in vans], f, indent=cls.json_indent)

    @classmethod
    def load_auto_vans(cls, bot: main.Pardina) -> List[auto_van.AutoVan]:
        vans = []

        try:
            with open(cls.auto_van_path, 'r') as f:
                data = json.load(f)
                for i in data:
                    vans.append(auto_van.AutoVan.deserialize(bot, i))
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass

        return vans

    @classmethod
    def save_auto_vans(cls, vans: List[auto_van.AutoVan]):
        with open(cls.auto_van_path, 'w+') as f:
            json.dump([i.serialize() for i in vans], f, indent=cls.json_indent)

    @classmethod
    def load_schedule(cls) -> List[schedule.Schedule]:
        vans = []

        try:
            with open(cls.schedule_path, 'r') as f:
                data = json.load(f)
                for i in data:
                    vans.append(schedule.Schedule.deserialize(i))
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass

        return vans

    @classmethod
    def save_schedule(cls, vans: List[schedule.Schedule]):
        with open(cls.schedule_path, 'w+') as f:
            json.dump([i.serialize() for i in vans], f, indent=cls.json_indent)
