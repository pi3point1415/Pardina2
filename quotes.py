import csv
import settings

from random import choice
from collections import defaultdict


class QuoteLine:
    def __init__(self, quoter, quote, quotee, comments, private_comments, msg_id):
        self.quoter = quoter
        self.quote = quote
        self.quotee = quotee
        self.comments = comments
        self.private_comments = private_comments
        self.id = int(msg_id)

    def to_markdown(self):
        line1 = f'> {self.quote}'
        comments = f', {self.comments}' if len(self.comments) > 0 else ''
        padded = self.quotee + ' ' * max(0, 40 - len(self.quotee))
        line2 = f'- ||{padded}||{comments}'
        return f'{line1}\n{line2}'

class Quotes:
    def __init__(self):
        with open (settings.Settings.quotesirl_path, 'r', encoding='utf-8') as f:
            quotes = list(csv.reader(f))[1:]

            self.quotes = [QuoteLine(*quote[:6]) for quote in quotes]


        with open (settings.Settings.quotes_done_path, 'r') as f:
            self.quotes_done = [int(i.rstrip()) for i in f.readlines()]

    def group_quotes(self, filtered=True):
        if filtered:
            quotes = list(filter(lambda i: i.id not in self.quotes_done, self.quotes))
        else:
            quotes = self.quotes

        groups = defaultdict(list)

        for quote in quotes:
            groups[quote.id].append(quote)

        return list(groups.values())

    def random_quote(self, filtered=True):
        undone = self.group_quotes(filtered)
        return choice(undone)

    def random_message(self, daily=True):
        quote = self.random_quote(daily)

        text = '\n'.join([i.to_markdown() for i in quote])

        if daily:
            header = 'QOTD (guess who said it!):'
            self.quotes_done.append(quote[0].id)
            self.save_done()
        else:
            header = 'Random quote (guess who said it!):'

        return f'{header}\n{text}\nlink: ||<{settings.Settings.quotesirl_link}{quote[0].id}>||'

    def save_done(self):
        with open (settings.Settings.quotes_done_path, 'w') as f:
            f.writelines([str(i) for i in self.quotes_done])