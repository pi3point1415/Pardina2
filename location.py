class Location:
    def __init__(self, desc : str, hold : str|None = None):
        self.desc = desc
        self.hold = hold

    def str_location(self):
        return f'The van is at {self.desc}'

    def str_hold(self):
        return f'Holds {self.hold if self.hold else f'at {self.desc}'} by default'

    def serialize(self):
        return {
            'desc': self.desc,
            'hold': self.hold,
        }

    @staticmethod
    def deserialize(d) -> Location:
        return Location(d['desc'], d['hold'])