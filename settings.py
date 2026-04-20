from typing import *
import json

import discord

import van

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

    ch_van_holds = 1265860905544192101
    alias_channels = [1265860905544192101]

    alias_path = 'data/alias.json'
    vans_path = 'data/vans.json'

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
    def load_vans(cls, bot : discord.Client) -> List[van.Van]:
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