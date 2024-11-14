from enum import Enum

class Emoji(Enum):


    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value