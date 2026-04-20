from datetime import timedelta, datetime, date
from random import choice
from typing import *

import discord

import main
import settings


class Van:
    def __init__(self, bot : main.Pardina, name: str, channel_id : int, msg_id: int, exp: date):
        self.bot = bot
        self.name = name
        self.channel_id = channel_id
        self.msg_id = msg_id
        self.exp = exp

    @classmethod
    async def create(cls, bot : main.Pardina, name : str, channel : discord.abc.Messageable) -> Van:
        msg = await channel.send(f'[Van] **{name}**')

        await msg.add_reaction(choice(settings.Settings.van_emojis))

        exp = datetime.now().date() + timedelta(days=2)

        van = cls(bot, name, msg.channel.id, msg.id, exp)

        return van

    @property
    async def msg(self) -> discord.Message | None:
        channel = await self.bot.fetch_channel(self.channel_id)

        if not isinstance(channel, discord.abc.Messageable):
            return None

        return await channel.fetch_message(self.msg_id)

    @property
    async def reactions(self) -> List[discord.Reaction]:
        msg = await self.msg

        if msg is None:
            return []

        return msg.reactions


    async def update(self) -> None:
        names = set()

        for reaction in await self.reactions:
            if reaction.emoji in settings.Settings.van_emojis:
                async for user in reaction.users():
                    client = self.bot.user
                    if client is None:
                        return
                    if user.id == client.id:
                        continue

                    alias = settings.Settings.get_alias(user.id)
                    if alias is not None:
                        names.add(alias)
                    else:
                        names.add(user.name)

        msg = await self.msg

        if msg is None:
            return

        if len(names) == 0:
            await msg.edit(content=f'[Van] **{self.name}**')
        else:
            await msg.edit(content=f'[Van] **{self.name}**, holding for **{', '.join(names)}**')

    def serialize(self) -> Dict:
        return {
            'name': self.name,
            'channel_id': self.channel_id,
            'msg_id': self.msg_id,
            'exp': self.exp.isoformat()
        }

    @classmethod
    def deserialize(cls, bot : main.Pardina, data : Dict) -> Van:
        return cls(
            bot = bot,
            name = data['name'],
            channel_id = data['channel_id'],
            msg_id = data['msg_id'],
            exp = date.fromisoformat(data['exp']),
        )