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
    delete = "<:delete:1310513587588169748>"
    share = "<:share:1310514510397968414>"
    world = "<:world:1310632749245399181>"
    lock = "<:lock:1310632703330091098>"
    back = "<:back:1310238973565735042>"
    shop_bag = "<:shop_bag:1310906629243539487>"
    send = "<:send:1317112698563072020>"
    pause = "<:pause:1324690746183254077>"
    play = "<:play:1324691102091186187>"
    done = "<:done:1324792101300600832>"
    report = "<:report:1326478828914086001>"
    add = "<:add:1337810147656863806>"
    code = "<:passcode:1338478704749314121>"
    message = "<:message:1338514047514972201>"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value