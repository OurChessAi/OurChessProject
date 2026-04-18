class Move:
    def __init__(self, first, final):
        #first and final are squares
        self.first = first
        self.final = final

    def __str__(self):
        s = ''
        s += f'({self.first.col}, {self.first.row})'
        s += f'({self.final.col}, {self.final.row})'
        return s

    def __eq__(self, other):
        return self.first == other.first and self.final == other.final