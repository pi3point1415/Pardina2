from typing import Callable, Coroutine, Any, List, Dict
from datetime import timedelta, datetime, date

import json
import random

import discord


class Van:
    def __init__(self, name : str, channel_id : int, msg_id : int, exp : date | None = None):
        self.name = name
        self.channel_id = channel_id
        self.msg_id = msg_id
        if exp is None:
            self.exp = datetime.now().date() + timedelta(days=2)
        else:
            self.exp = exp

    def serialize(self) -> Dict:
        return {'name': self.name, 'channel_id': self.channel_id, 'msg_id': self.msg_id, 'exp': self.exp.isoformat()}

    @staticmethod
    def deserialize(d) -> Van:
        return Van(name=d['name'], channel_id=d['channel_id'], msg_id=d['msg_id'], exp=date.fromisoformat(d['exp']))

    def __str__(self):
        return f'{self.name}:\n\t{self.msg_id}\n\t{self.exp.isoformat()}'


class Pardina(discord.Client):
    def __init__(self, *args, **kwargs):
        self.database : Dict[str, str] = {
            'vans': 'vans.json',
            'alias': 'alias.json',
        }

        self.channels : Dict[int, List[str]] = {
            1265860905544192101: ['van', 'alias'],
        }

        self.commands : Dict[str, Callable[[discord.Message], Coroutine[Any, Any, None]]] = {
            'van': self.van,
            'alias': self.set_alias,
        }

        self.emoji_options : Dict[str, List[str]] = {
            'van': [
                '🚌',
                '🚐',
                '🚎',
                '🚍',
                '🦈',
                '🕴️',
                '✈️',
            ]
        }

        self.vans : List[Van] = []
        self.alias: Dict[int, str] = {}

        super().__init__(*args, **kwargs)


    async def on_ready(self):
        self.load_vans()
        self.load_alias()

        for van in self.vans:
            await self.update_van_message(van)

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return

        if message.channel.id in self.channels.keys():
            for command in self.commands:
                if message.content.lower().startswith(f'{command} '):
                    await self.commands[command](message)
                    return

    async def on_raw_reaction_add(self, reaction : discord.RawReactionActionEvent):
        await self.on_raw_reaction_change(reaction)

    async def on_raw_reaction_remove(self, reaction : discord.RawReactionActionEvent):
        await self.on_raw_reaction_change(reaction)

    async def on_raw_reaction_change(self, reaction : discord.RawReactionActionEvent):
        for van in self.vans:
            if reaction.channel_id == van.channel_id and reaction.message_id == van.msg_id:
                await self.update_van_message(van)

    async def van(self, trigger_msg : discord.Message):
        name = trigger_msg.content[4:]
        await trigger_msg.delete()

        msg = await trigger_msg.channel.send(f'Van: ')

        await msg.add_reaction(random.choice(self.emoji_options['van']))

        van = Van(name, msg.channel.id, msg.id)
        self.vans.append(van)
        self.save_vans()

        await self.update_van_message(van)

    async def set_alias(self, trigger_msg : discord.Message):
        name = trigger_msg.content[6:]
        await trigger_msg.delete()

        self.alias[trigger_msg.author.id] = name
        self.save_alias()

        for van in self.vans:
            await self.update_van_message(van)

    def save_vans(self) -> None:
        with open(self.database['vans'], 'w+') as f:
            data = [van.serialize() for van in self.vans]
            json.dump(data, f)

    def load_vans(self) -> None:
        try:
            with open(self.database['vans'], 'r') as f:
                data = json.load(f)
                for van in data:
                    self.vans.append(Van.deserialize(van))
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass

    def save_alias(self) -> None:
        with open(self.database['alias'], 'w+') as f:
            json.dump(self.alias, f)

    def load_alias(self) -> None:
        try:
            with open(self.database['alias'], 'r') as f:
                d = json.load(f)
                self.alias = {int(key): value for key, value in d.items()}
        except FileNotFoundError, json.decoder.JSONDecodeError:
            pass


    async def update_van_message(self, van: Van) -> None:
        channel = await self.fetch_channel(van.channel_id)
        # noinspection PyUnresolvedReferences
        msg = await channel.fetch_message(van.msg_id)

        names = set()

        for reaction in msg.reactions:
            if reaction.emoji in self.emoji_options['van']:
                async for user in reaction.users():
                    # noinspection PyUnresolvedReferences
                    if user.id == self.user.id:
                        continue

                    if user.id in self.alias:
                        names.add(self.alias[user.id])
                    else:
                        names.add(user.name)

        if len(names) == 0:
            await msg.edit(content=f'Van: **{van.name}**')
        else:
            await msg.edit(content=f'Van: **{van.name}** holding for **{', '.join(names)}**')


def main():
    intents = discord.Intents.default()
    # noinspection PyDunderSlots,PyUnresolvedReferences
    intents.message_content = True

    client = Pardina(intents=intents)

    with open('token', 'r') as f:
        token = f.read()
        client.run(token)


if __name__ == '__main__':
    main()