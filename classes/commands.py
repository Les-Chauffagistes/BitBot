from enum import Enum

class Command(Enum):
    
    pi_profile_edit = "</pi profile edit:1309939752388132975>"
    pi_deposit = "</pi deposit:1309939752388132975>"
    ventes_add = "</ventes add:1310291105429979217>"
    ventes_edit = "</ventes edit:1327622946251866192>"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value