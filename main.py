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

import logging
from logging.handlers import RotatingFileHandler

class Pardina(discord.Client):
    def __init__(self, logger, *args, **kwargs):
        self.vans : List[van.Van] = []
        self.auto_vans : List[auto_van.AutoVan] = []
        self.schedule : List[schedule.Schedule] = []

        self.quotes : quotes.Quotes = quotes.Quotes()

        self.logger : logging.Logger = logger

        super().__init__(*args, **kwargs)


    async def on_ready(self):
        self.vans = settings.Settings.load_vans(self)

        self.auto_vans = settings.Settings.load_auto_vans(self)
        self.load_schedule()

        asyncio.create_task(self.quotes_loop())
        asyncio.create_task(self.daily_loop())

        self.logger.log(logging.INFO, "Pardina ready")

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

    @property
    async def ch_people_visiting(self) -> discord.abc.Messageable | None:
        try:
            channel = await self.fetch_channel(settings.Settings.ch_people_visiting)
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
            self.logger.log(logging.INFO, f'Shark message sent in channel {message.channel.id}')

        if re.search('(?i)buf+alo', message.content):
            path = choice(os.listdir(settings.Settings.buffalo_path))
            text = path[3:-4].replace('_', ' ')
            file = discord.File(os.path.join(settings.Settings.buffalo_path, path))
            await message.channel.send(text, file=file)
            self.logger.log(logging.INFO, f'Buffalo message sent in channel {message.channel.id}')

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
        self.logger.log(logging.INFO, f'Alias of user {trigger_msg.author.id} changed to {name}')

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
            self.logger.log(logging.INFO, f'{'Random' if message is None else 'Daily'} quote created in channel {channel.id}')


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
                v = i.to_auto_van(self)
                self.auto_vans.append(v)

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

            self.logger.log(logging.INFO, f'Quotes loop started for target time {target.strftime('%Y-%m-%d %H:%M:%S')}')

            await asyncio.sleep(delay)

            await self.command_quote()

    async def daily_loop(self):
        while True:
            now = datetime.now()
            target = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            delay = (target - now).total_seconds()

            self.logger.log(logging.INFO, f'Daily loop started for target time {target.strftime('%Y-%m-%d %H:%M:%S')}')

            await asyncio.sleep(delay)

            self.auto_vans = settings.Settings.load_auto_vans(self)
            self.load_schedule()

            # copy so that we still go through all of them if any are removed
            vans = self.vans[::]

            for i in vans:
                if datetime.now().date() >= i.exp:
                    self.vans.remove(i)
                    self.logger.log(logging.INFO, f'Removing expired van {i.name}')

            channel = await self.ch_people_visiting

            if channel is not None:
                async for msg in channel.history(limit=None):
                    now = datetime.now()
                    msg_time = msg.created_at
                    diff = msg_time - now
                    if diff.days >= 17 and msg.id != 892970388693336095:
                        await msg.delete()
                        self.logger.log(logging.INFO,
                                        f'Deleted message [time: {msg.created_at}, author: {msg.author.id}, content: {msg.content}]')


def main():
    intents = discord.Intents.default()
    # noinspection PyDunderSlots,PyUnresolvedReferences
    intents.message_content = True

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    fh = RotatingFileHandler(
        settings.Settings.log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
        mode='a+'
    )
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    bot = Pardina(intents=intents, logger=logger)

    bot.run(settings.Settings.token)


if __name__ == '__main__':
    main()