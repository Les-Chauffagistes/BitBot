from enum import Enum

from commands import pi_profile

class Command(Enum):
    
    pi_profile_edit = "</pi profile edit:1309939752388132975>"
    pi_deposit = "</pi deposit:1309939752388132975>"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value