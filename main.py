from typing import *
from datetime import timedelta, datetime, date, time
import json
import random
import asyncio

import discord

from van import Van
from settings import Settings


# class Location:
#     def __init__(self, desc : str, hold : str|None = None):
#         self.desc = desc
#         self.hold = hold
#
#     def str_location(self):
#         return f'*The van is at {self.desc}*'
#
#     def str_hold(self):
#         return f'Holds {self.hold if self.hold else f'at {self.desc}'} by default'
#
#     def serialize(self):
#         return {
#             'desc': self.desc,
#             'hold': self.hold,
#         }
#
#     @staticmethod
#     def deserialize(d) -> Location:
#         return Location(d['desc'], d['hold'])
#
#
# class Where:
#     def __init__(self, channel_id : int, msg_id : int, exp : date | None = None):
#         self.channel_id = channel_id
#         self.msg_id = msg_id
#         self.exp = exp
#         if exp is None:
#             self.exp = datetime.now().date() + timedelta(days=2)
#         else:
#             self.exp = exp
#
#     def serialize(self) -> Dict:
#         return {
#             'channel_id': self.channel_id,
#             'msg_id': self.msg_id,
#             'exp': self.exp.isoformat()
#         }
#
#     @staticmethod
#     def deserialize(d) -> Where:
#         return Where(
#             channel_id=d['channel_id'],
#             msg_id=d['msg_id'],
#             exp=date.fromisoformat(d['exp'])
#         )
#
#
# class Van:
#     def __init__(self, name : str, channel_id : int, msg_id : int, exp : date | None = None):
#         self.name = name
#         self.channel_id = channel_id
#         self.msg_id = msg_id
#         if exp is None:
#             self.exp = datetime.now().date() + timedelta(days=2)
#         else:
#             self.exp = exp
#
#     def serialize(self) -> Dict:
#         return {
#             'name': self.name,
#             'channel_id': self.channel_id,
#             'msg_id': self.msg_id,
#             'exp': self.exp.isoformat()
#         }
#
#     @staticmethod
#     def deserialize(d) -> Van:
#         return Van(
#             name=d['name'],
#             channel_id=d['channel_id'],
#             msg_id=d['msg_id'],
#             exp=date.fromisoformat(d['exp'])
#         )
#
#     def __str__(self):
#         return f'{self.name}:\n\t{self.msg_id}\n\t{self.exp.isoformat()}'
#
#
# class AutoVan:
#     def __init__(self, name : str, day: int, van_time : time, where_time : time | None = None):
#         self.name = name
#         self.day = day
#         self.van_time = van_time
#         self.where_time = where_time
#
#     def serialize(self) -> Dict:
#         return {
#             'name': self.name,
#             'day': self.day,
#             'where_time': self.where_time.isoformat() if self.where_time else None,
#             'van_time': self.van_time.isoformat(),
#         }
#
#     @staticmethod
#     def deserialize(d) -> AutoVan:
#         return AutoVan(
#             name=d['name'],
#             day=d['day'],
#             van_time=time.fromisoformat(d['van_time']),
#             where_time=time.fromisoformat(d['where_time']) if d['where_time'] else None,
#         )
#
#     def __str__(self):
#         return f'{self.name}:\n\t{self.day}\n\t{self.van_time.isoformat()}'


class Pardina(discord.Client):
    def __init__(self, *args, **kwargs):
        self.json_indent = 4

        self.vans : List[Van] = []

        # self.database : Dict[str, str] = {
        #     'wheres': 'data/wheres.json',
        #     'vans': 'data/vans.json',
        #     'alias': 'data/alias.json',
        #     'schedule': 'data/schedule.json',
        # }
        #
        # self.channels : Dict[int, List[str]] = {
        #     1265860905544192101: ['van', 'alias'],
        # }
        #
        # self.commands : Dict[str, Callable[[discord.Message], Coroutine[Any, Any, None]]] = {
            # 'van': self.create_van,
            # 'alias': self.set_alias,
        # }
        #
        # self.emoji_options : Dict[str, List[str]] = {
        #     'van': [
        #         '🚌',
        #         '🚐',
        #         '🚎',
        #         '🚍',
        #         '🦈',
        #         '🕴️',
        #         '✈️',
        #     ]
        # }
        #
        # self.locations : Dict[str, Location] = {
        #     '🧑‍✈️': Location('the lot at 158 Mass Ave'),
        #     '🇦🇱': Location('Albany Street Garage', 'holds between buildings 39 and 24'),
        #     '🗽': Location('beneath Stata'),
        #     '❓': Location('a mystery location'),
        # }
        #
        # self.wheres : List[Where] = []
        # self.vans : List[Van] = []
        # self.alias : Dict[int, str] = {}
        # self.schedule : List[AutoVan] = []
        #
        # self.van_tasks : List[asyncio.Task] = []

        super().__init__(*args, **kwargs)


    async def on_ready(self):
        pass
        # self.load_wheres()
        # self.load_vans()
        # self.load_alias()
        # self.load_schedule()

        # for van in self.vans:
        #     await self.update_van_message(van)

    @property
    async def ch_van_holds(self) -> discord.abc.Messageable | None:
        try:
            channel = await self.fetch_channel(Settings.ch_van_holds)
        except discord.NotFound, discord.errors.HTTPException:
            return None
        if not isinstance(channel, discord.abc.Messageable):
            return None
        else:
            return channel

    async def van_by_message(self, message : discord.Message) -> Van | None:
        for i in self.vans:
            if i.msg_id == message.id:
                return i
        return None

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return

        if message.content.lower().startswith('van '):
            if message.channel.id == Settings.ch_van_holds:
                await self.command_van(message)

    async def command_van(self, trigger_msg : discord.Message):
        channel = trigger_msg.channel
        if channel is not None:
            name = trigger_msg.content[4:]
            self.vans.append(await Van.create(self, name, channel))
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

        van = await self.van_by_message(message)
        if van is not None:
            await van.update()
    #
    # async def create_where(self, channel, exp = None):
    #     print(f'[Vans]: Creating "Where is the van?" message in channel {channel}')
    #
    #     msg = await channel.send(f'Where is the van?')
    #
    #     for loc in self.locations.keys():
    #         await msg.add_reaction(loc)
    #
    #     where = Where(channel.id, msg.id, exp)
    #     self.wheres.append(where)
    #     self.save_wheres()
    #
    #     return where
    #
    # async def create_van(self, name, channel):
    #     print(f'[Vans]: Creating van {name} in channel {channel}')
    #
    #     msg = await channel.send(f'[Van]')
    #
    #     await msg.add_reaction(random.choice(self.emoji_options['van']))
    #
    #     van = Van(name, msg.channel.id, msg.id)
    #     self.vans.append(van)
    #     self.save_vans()
    #
    #     await self.update_van_message(van)
    #
    # async def van(self, trigger_msg : discord.Message):
    #     name = trigger_msg.content[4:]
    #     channel = trigger_msg.channel
    #     await trigger_msg.delete()
    #
    #     await self.create_van(name, channel)
    #
    # async def where_van(self, van : AutoVan):
    #     where : Where | None = None
    #
    #     if van.where_time is not None:
    #         now = datetime.now()
    #         where_time = van.where_time
    #         target = now.replace(
    #             hour=where_time.hour,
    #             minute=where_time.minute,
    #             second=where_time.second,
    #             microsecond=0,
    #         )
    #
    #         if target >= now:
    #             delay = (target - now).total_seconds()
    #
    #             print(f'[Vans]: Where is the van message scheduled for "{van.name}" at {where_time.isoformat()}')
    #
    #             await asyncio.sleep(delay)
    #
    #             for channel_id in self.channels:
    #                 if 'van' in self.channels[channel_id]:
    #                     channel = await self.fetch_channel(channel_id)
    #
    #                     # noinspection PyTypeChecker
    #                     where = await self.create_where(channel)
    #                     break
    #
    #     now = datetime.now()
    #     van_time = van.van_time
    #     target = now.replace(
    #         hour=van_time.hour,
    #         minute=van_time.minute,
    #         second=van_time.second,
    #         microsecond=0,
    #     )
    #
    #     if target <= now:
    #         return
    #
    #     delay = (target - now).total_seconds()
    #
    #     print(f'[Vans]: Van {van.name} message scheduled for {van_time.isoformat()}')
    #
    #     await asyncio.sleep(delay)
    #
    #     location : Location | None = None
    #
    #     if where is not None:
    #         channel = await self.fetch_channel(where.channel_id)
    #         # noinspection PyUnresolvedReferences
    #         msg = await channel.fetch_message(where.msg_id)
    #         reactions = msg.reactions
    #
    #         for i in reactions:
    #             if i.count >= 2 and i.emoji in self.locations:
    #                 # noinspection PyTypeChecker
    #                 location = self.locations[i.emoji]
    #
    #     for channel_id in self.channels:
    #         if 'van' in self.channels[channel_id]:
    #             channel = await self.fetch_channel(channel_id)
    #             if location is not None:
    #                 # noinspection PyUnresolvedReferences
    #                 await channel.send(location.str_location())
    #                 loc_string = f'. {location.str_hold()}'
    #             else:
    #                 # noinspection PyUnresolvedReferences
    #                 await channel.send('The van is at a mystery location')
    #                 loc_string = ''
    #
    #             # noinspection PyTypeChecker
    #             await self.create_van(f'{van.name}{loc_string}', channel)
    #             break
    #
    # async def set_alias(self, trigger_msg : discord.Message):
    #     name = trigger_msg.content[6:]
    #     await trigger_msg.delete()
    #
    #     self.alias[trigger_msg.author.id] = name
    #     self.save_alias()
    #
    #     for van in self.vans:
    #         await self.update_van_message(van)
    #
    # def save_wheres(self) -> None:
    #     with open(self.database['wheres'], 'w+') as f:
    #         data = [where.serialize() for where in self.wheres]
    #         json.dump(data, f, indent=self.json_indent)
    #
    # def load_wheres(self) -> None:
    #     try:
    #         with open(self.database['wheres'], 'r') as f:
    #             data = json.load(f)
    #             for where in data:
    #                 self.wheres.append(Where.deserialize(where))
    #     except FileNotFoundError, json.decoder.JSONDecodeError:
    #         pass
    #
    #
    # def save_vans(self) -> None:
    #     with open(self.database['vans'], 'w+') as f:
    #         data = [van.serialize() for van in self.vans]
    #         json.dump(data, f, indent=self.json_indent)
    #
    # def load_vans(self) -> None:
    #     try:
    #         with open(self.database['vans'], 'r') as f:
    #             data = json.load(f)
    #             for van in data:
    #                 self.vans.append(Van.deserialize(van))
    #     except FileNotFoundError, json.decoder.JSONDecodeError:
    #         pass
    #
    # def save_alias(self) -> None:
    #     with open(self.database['alias'], 'w+') as f:
    #         json.dump(self.alias, f, indent=self.json_indent)
    #
    # def load_alias(self) -> None:
    #     try:
    #         with open(self.database['alias'], 'r') as f:
    #             d = json.load(f)
    #             self.alias = {int(key): value for key, value in d.items()}
    #     except FileNotFoundError, json.decoder.JSONDecodeError:
    #         pass
    #
    # def save_schedule(self) -> None:
    #     with open(self.database['schedule'], 'w+') as f:
    #         data = [van.serialize() for van in self.schedule]
    #         json.dump(data, f, indent=self.json_indent)
    #
    # def load_schedule(self) -> None:
    #     try:
    #         with open(self.database['schedule'], 'r') as f:
    #             data = json.load(f)
    #             for van in data:
    #                 self.schedule.append(AutoVan.deserialize(van))
    #     except FileNotFoundError, json.decoder.JSONDecodeError:
    #         pass
    #
    #     for van in self.schedule:
    #         task = asyncio.create_task(self.where_van(van))
    #         self.van_tasks.append(task)
    #
    #
    # async def update_van_message(self, van: Van) -> None:
    #     channel = await self.fetch_channel(van.channel_id)
    #     # noinspection PyUnresolvedReferences
    #     msg = await channel.fetch_message(van.msg_id)
    #
    #     names = set()
    #
    #     for reaction in msg.reactions:
    #         if reaction.emoji in self.emoji_options['van']:
    #             async for user in reaction.users():
    #                 # noinspection PyUnresolvedReferences
    #                 if user.id == self.user.id:
    #                     continue
    #
    #                 if user.id in self.alias:
    #                     names.add(self.alias[user.id])
    #                 else:
    #                     names.add(user.name)
    #
    #     if len(names) == 0:
    #         await msg.edit(content=f'[Van] **{van.name}**')
    #     else:
    #         await msg.edit(content=f'[Van] **{van.name}**, holding for **{', '.join(names)}**')


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