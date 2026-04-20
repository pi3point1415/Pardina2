import asyncio
from typing import *
from datetime import time, datetime
from random import choice

import discord

import settings

import van

import main


class AutoVan:
    def __init__(
            self, bot: main.Pardina,
            name: str,
            day: int,
            where_time: time | None,
            van_time : time,
            channel_id : int | None = None,
            msg_id : int | None = None,
        ):
        self.bot = bot
        self.name = name
        self.day = day
        self.where_time = where_time
        self.van_time = van_time

        self.channel_id = channel_id
        self.msg_id = msg_id

    async def queue_where(self):
        if self.where_time is None:
            await self.queue_van()
            return

        now = datetime.now()

        where_time = now.replace(
            hour=self.where_time.hour,
            minute=self.where_time.minute,
            second=self.where_time.second,
            microsecond=0
        )

        if where_time < now:
            await self.queue_van()
            return

        delay = (where_time - now).total_seconds()

        await asyncio.sleep(delay)

        channel = await self.bot.fetch_channel(settings.Settings.ch_van_holds)

        if not isinstance(channel, discord.abc.Messageable):
            return

        msg = await channel.send('Where is the van?')

        for loc in settings.Settings.locations.keys():
            if loc is None:
                continue
            await msg.add_reaction(loc)

        for floor in settings.Settings.floor_emojis:
            await msg.add_reaction(choice(floor))

        self.channel_id = msg.channel.id
        self.msg_id = msg.id

        settings.Settings.save_auto_vans(self.bot.auto_vans)

        await self.queue_van()

    async def queue_van(self):
        now = datetime.now()

        van_time = now.replace(
            hour=self.van_time.hour,
            minute=self.van_time.minute,
            second=self.van_time.second,
            microsecond=0
        )

        if van_time < now:
            self.remove()
            return

        delay = (van_time - now).total_seconds()

        await asyncio.sleep(delay)

        if self.where_time is not None and self.msg_id is not None and self.channel_id is not None:
            channel = await self.bot.fetch_channel(self.channel_id)

            if not isinstance(channel, discord.abc.Messageable):
                return

            where = await channel.fetch_message(self.msg_id)
            reactions = where.reactions

            emoji : str | None = None
            floor : int = -1

            for i in reactions:
                if i.count >= 2:
                    if i.emoji in settings.Settings.locations:
                        emoji = str(i.emoji)
                    for num, emojis in enumerate(settings.Settings.floor_emojis):
                        if i.emoji in emojis:
                            floor = num

            location = settings.Settings.locations[emoji]

            floor += 1

            floor_text = '' if floor == 0 else f', floor {floor}'

            await channel.send(f'*{location.str_location()}{floor_text}*')

            new_van = await van.Van.create(self.bot, f'{self.name}: {location.str_hold()}', channel)
        else:
            channel = await self.bot.fetch_channel(settings.Settings.ch_van_holds)

            if not isinstance(channel, discord.abc.Messageable):
                return

            new_van = await van.Van.create(self.bot, self.name, channel)

        self.bot.vans.append(new_van)
        settings.Settings.save_vans(self.bot.vans)

        self.remove()

    def remove(self):
        self.bot.auto_vans.remove(self)
        settings.Settings.save_auto_vans(self.bot.auto_vans)

    def serialize(self) -> Dict:
        return {
            'name': self.name,
            'day': self.day,
            'where_time': self.where_time.isoformat() if self.where_time else None,
            'van_time': self.van_time.isoformat(),
            'channel_id': self.channel_id,
            'msg_id': self.msg_id,
        }

    @classmethod
    def deserialize(cls, bot: main.Pardina, data: Dict) -> AutoVan:
        return cls(
            bot=bot,
            name=data['name'],
            day=data['day'],
            where_time=time.fromisoformat(data['where_time']) if data['where_time'] else None,
            van_time=time.fromisoformat(data['van_time']),
            channel_id=data['channel_id'],
            msg_id=data['msg_id'],
        )