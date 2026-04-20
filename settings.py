from typing import *
import json

import discord

import auto_van
import main
import schedule
import van
import location

class Settings:
    json_indent = 4

    van_emojis: List[str] = [
        '🚌',
        '🚐',
        '🚎',
        '🚍',
        '🦈',
        '🕴️',
        '✈️',
    ]

    locations : Dict[str | None, location.Location] = {
        '🧑‍✈️': location.Location('the lot at 158 Mass Ave'),
        '🇦🇱': location.Location('Albany Street Garage', 'holds between buildings 39 and 24'),
        '🗽': location.Location('beneath Stata'),
        '❓': location.Location('a mystery location'),
        None: location.Location('a mystery location'),
    }

    floor_emojis : List[List[str]] = [
        ['🐪', '🔂', '☝️', '💧', '🌩️', '🥇', '🔉'],
        ['💕', '🐫', '🌱', '✌️', '🧦', '👯', '🍒', '🥂', '🥢', '🥈', '🩰', '🎭', '‼️', '🔰', '👀'],
        ['🍡', '☘️', '🇮🇲', '🤟', '🚦', '💦', '🫧', '🫐', '🧆', '🍢', '🍨', '🫘', '🥉', '☢️', '☣️', '♨️', '♻️', '💤', '🎶', '🔊', '⚧'],
        ['🍀', '☠️', '💅', '🦋', '✨', '🪟', '🌥️', '☔', '🛟', '🎛️', '💢', '❌', '❎', '💐'],
        ['💫', '🖐️', '🌟', '🇻🇳', '🌿', '⭐', '⛅', '🛞', '💮', '🇲🇲', '🇭🇰', '🏳️‍⚧️', '🇸🇨', '🎼'],
        ['✡️', '❄️', '🌨️', '🔯', '*️⃣', '🍕', '⚛️', '🏳️‍🌈'],
        ['🌧️', '🍇', '🎰', '🐞', '🧬', '📏'],
        ['✳️', '❇️', '🪢', '🕸️', '☀️', '🎱', '🚨', '☸️', '🛑', '🔅', '🔆', '🔝', '🇲🇰']
    ]

    ch_van_holds = 1265860905544192101
    alias_channels = [1265860905544192101]
    quotesirl_link = f'https://discord.com/channels/684865442107359277/685208858427523139/'

    alias_path = 'data/alias.json'
    vans_path = 'data/vans.json'
    auto_van_path = 'data/auto_vans.json'
    schedule_path = 'data/schedule.json'

    quotes_done_path = 'data/quotes_done.txt'
    quotesirl_path = 'data/quotesirl.csv'

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
    def load_vans(cls, bot : main.Pardina) -> List[van.Van]:
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
    def save_vans(cls, vans : List[van.Van]):
        with open(cls.vans_path, 'w+') as f:
            json.dump([i.serialize() for i in vans], f, indent=cls.json_indent)

    @classmethod
    def load_auto_vans(cls, bot : main.Pardina) -> List[auto_van.AutoVan]:
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
    def save_auto_vans(cls, vans : List[auto_van.AutoVan]):
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
    def save_schedule(cls, vans : List[schedule.Schedule]):
        with open(cls.schedule_path, 'w+') as f:
            json.dump([i.serialize() for i in vans], f, indent=cls.json_indent)