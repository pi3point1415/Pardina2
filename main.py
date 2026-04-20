from typing import *

import discord

import auto_van
import van
import schedule
import settings


class Pardina(discord.Client):
    def __init__(self, *args, **kwargs):
        self.vans : List[van.Van] = []
        self.auto_vans : List[auto_van.AutoVan] = []
        self.schedule : List[schedule.Schedule] = []

        super().__init__(*args, **kwargs)


    async def on_ready(self):
        self.vans = settings.Settings.load_vans(self)
        self.auto_vans = settings.Settings.load_auto_vans(self)

        self.schedule = settings.Settings.load_schedule()

        for i in self.schedule:
            if i.is_today and not i.matches_auto_van(self.auto_vans):
                self.auto_vans.append(i.to_auto_van(self))

        # copy so that we still go through all of them if any are removed
        auto_vans = self.auto_vans[::]
        for i in auto_vans:
            await i.queue_where()

        settings.Settings.save_auto_vans(self.auto_vans)

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

    async def van_by_message(self, message : discord.Message) -> van.Van | None:
        for i in self.vans:
            if i.msg_id == message.id:
                return i
        return None

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return

        if message.content.lower().startswith('van '):
            if message.channel.id == settings.Settings.ch_van_holds:
                await self.command_van(message)
        elif message.content.lower().startswith('alias '):
            if message.channel.id in settings.Settings.alias_channels:
                await self.command_alias(message)

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


def main(client):
    with open('token', 'r') as f:
        token = f.read()
        client.run(token)


if __name__ == '__main__':
    intents = discord.Intents.default()
    # noinspection PyDunderSlots,PyUnresolvedReferences
    intents.message_content = True

    bot = Pardina(intents=intents)

    main(bot)