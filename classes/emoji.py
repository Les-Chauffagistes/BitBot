from enum import Enum

class Emoji(Enum):

    wallet = "<:wallet:1309943715137196075>"
    verified_user = "<:verified_user:1310218769682927667>"
    cart = "<:cart:1310231858998415441>"
    store = "<:store:1310231869681565696>"
    next = "<:next:1310238998907846696>"
    profile = "<:profile:1310262757530144892>"
    pay = "<:pay:1310270876704571464>"
    edit = "<:edit:1287775378944954408>"
    image = "<:image:1310288606023127082>"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value