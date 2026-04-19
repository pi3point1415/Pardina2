from datetime import timedelta, datetime, date, time
from random import choice
from typing import *

import discord

from settings import Settings


class Van:
    def __init__(self, bot : discord.Client, name: str, msg : discord.Message):
        self.bot = bot
        self.name = name
        self.channel_id = msg.channel.id
        self.msg_id = msg.id
        self.exp = datetime.now().date() + timedelta(days=2)

    @classmethod
    async def create(cls, bot : discord.Client, name : str, channel : discord.abc.Messageable) -> Van:
        msg = await channel.send(f'[Van] **{name}**')

        await msg.add_reaction(choice(Settings.van_emojis))

        van = cls(bot, name, msg)

        return van

    @property
    async def msg(self) -> discord.Message:
        channel = await self.bot.fetch_channel(self.channel_id)
        return await channel.fetch_message(self.msg_id)

    @property
    async def reactions(self) -> List[discord.Reaction]:
        msg = await self.msg
        return msg.reactions


    async def update(self) -> None:
        names = set()

        for reaction in await self.reactions:
            if reaction.emoji in Settings.van_emojis:
                async for user in reaction.users():
                    if user.id == self.bot.user.id:
                        continue

                    names.add(user.name)
                    # TODO add alias
                    # if user.id in self.alias:
                    #     names.add(self.alias[user.id])
                    # else:
                    #     names.add(user.name)

        msg = await self.msg

        if len(names) == 0:
            await msg.edit(content=f'[Van] **{self.name}**')
        else:
            await msg.edit(content=f'[Van] **{self.name}**, holding for **{', '.join(names)}**')