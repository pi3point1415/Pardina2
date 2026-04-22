from random import randint, choice
from typing import *
import asyncio
import os

import discord

from datetime import datetime, timedelta

import auto_van
import van
import schedule
import settings
import quotes

import re


class Pardina(discord.Client):
    def __init__(self, *args, **kwargs):
        self.vans : List[van.Van] = []
        self.auto_vans : List[auto_van.AutoVan] = []
        self.schedule : List[schedule.Schedule] = []

        self.quotes : quotes.Quotes = quotes.Quotes()

        super().__init__(*args, **kwargs)


    async def on_ready(self):
        self.vans = settings.Settings.load_vans(self)

        self.auto_vans = settings.Settings.load_auto_vans(self)
        self.load_schedule()

        asyncio.create_task(self.quotes_loop())
        asyncio.create_task(self.daily_loop())

    @property
    async def ch_van_holds(self) -> discord.abc.Messageable | None:
        try:
            channel = await self.fetch_channel(settings.Settings.ch_van_holds)
        except discord.NotFound, discord.errors.HTTPException:
            return None
        if not isinstance(channel, discord.abc.Messageable):
            return None
        else:
            return channel

    @property
    async def ch_chat_games(self) -> discord.abc.Messageable | None:
        try:
            channel = await self.fetch_channel(settings.Settings.ch_chat_games)
        except discord.NotFound, discord.errors.HTTPException:
            return None
        if not isinstance(channel, discord.abc.Messageable):
            return None
        else:
            return channel

    async def van_by_message(self, message : discord.Message) -> van.Van | None:
        for i in self.vans:
            if i.msg_id == message.id:
                return i
        return None

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return

        if message.content.lower().startswith('van '):
            if message.channel.id == settings.Settings.ch_van_holds or message.channel.id == settings.Settings.ch_botspam:
                await self.command_van(message)
        elif message.content.lower().startswith('alias '):
            if message.channel.id in settings.Settings.ch_van_holds or message.channel.id == settings.Settings.ch_botspam:
                await self.command_alias(message)
        elif message.content.lower() == 'quote':
            if message.channel.id == settings.Settings.ch_chat_games or message.channel.id == settings.Settings.ch_botspam:
                await self.command_quote(message)

        if re.search('(?i)sha+rk', message.content):
            await message.channel.send(f'sh{'a' * randint(5, 15)}rk')

        if re.search('(?i)buf+alo', message.content):
            path = choice(os.listdir(settings.Settings.buffalo_path))
            text = path[3:-4].replace('_', ' ')
            file = discord.File(os.path.join(settings.Settings.buffalo_path, path))
            await message.channel.send(text, file=file)

    async def command_van(self, trigger_msg : discord.Message):
        channel = trigger_msg.channel
        if channel is not None:
            name = trigger_msg.content[4:]
            self.vans.append(await van.Van.create(self, name, channel))
            await trigger_msg.delete()

        settings.Settings.save_vans(self.vans)

    async def command_alias(self, trigger_msg : discord.Message):
        name = trigger_msg.content[6:]
        settings.Settings.add_alias(trigger_msg.author.id, name)

        for i in self.vans:
            await i.update()

        await trigger_msg.delete()

    async def command_quote(self, message : discord.Message | None = None):
        if message is None:
            channel = await self.ch_chat_games
        else:
            channel = message.channel
        if channel is not None:
            msg = self.quotes.random_message(message is None)
            await channel.send(msg)

    async def on_raw_reaction_add(self, reaction : discord.RawReactionActionEvent):
        await self.on_raw_reaction_change(reaction)

    async def on_raw_reaction_remove(self, reaction : discord.RawReactionActionEvent):
        await self.on_raw_reaction_change(reaction)

    async def on_raw_reaction_change(self, reaction : discord.RawReactionActionEvent):
        channel = await self.fetch_channel(reaction.channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            return
        message = await channel.fetch_message(reaction.message_id)

        v = await self.van_by_message(message)
        if v is not None:
            await v.update()

    def load_schedule(self):
        self.schedule = settings.Settings.load_schedule()

        for i in self.schedule:
            if i.is_today and not i.matches_auto_van(self.auto_vans):
                self.auto_vans.append(i.to_auto_van(self))

        # copy so that we still go through all of them if any are removed
        auto_vans = self.auto_vans[::]
        for i in auto_vans:
            asyncio.create_task(i.queue_where())

        settings.Settings.save_auto_vans(self.auto_vans)

    async def quotes_loop(self):
        while True:
            quote_time = settings.Settings.quotes_time

            now = datetime.now()
            target = now.replace(hour=quote_time.hour, minute=quote_time.minute, second=quote_time.second, microsecond=0)

            while target < now:
                target = target + timedelta(days=1)

            delay = (target - now).total_seconds()

            await asyncio.sleep(delay)

            await self.command_quote()

    async def daily_loop(self):
        while True:
            now = datetime.now()
            target = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            delay = (target - now).total_seconds()

            await asyncio.sleep(delay)

            self.auto_vans = settings.Settings.load_auto_vans(self)
            self.load_schedule()

            # copy so that we still go through all of them if any are removed
            vans = self.vans[::]

            for i in vans:
                if datetime.now().date() >= i.exp:
                    self.vans.remove(i)


def main():
    intents = discord.Intents.default()
    # noinspection PyDunderSlots,PyUnresolvedReferences
    intents.message_content = True

    bot = Pardina(intents=intents)

    bot.run(settings.Settings.token)


if __name__ == '__main__':
    main()