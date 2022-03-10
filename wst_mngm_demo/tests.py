from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    def play_round(self):
        if self.player.role_own == 'CH':
            yield Days, dict(actionBCH=5, actionRESell=0, priceCH=cu(5), actionD=0)
        if self.player.role_own == 'UC' and self.player.id_in_group == 2:
            yield Days, dict(actionUCBuyBool='Yes', actionSUC=1, actionPP=4, priceUC=5, actionD=0)
        if self.player.role_own == 'UC' and self.player.id_in_group == 4:
            yield Days, dict(actionUCBuyBool='Yes', actionSUC=2, actionPP=3, priceUC=5, actionD=0)