from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:  # sanity checks for round 1
            if self.player.role_own == 'RE':
                yield Days
                yield Results
            if self.player.role_own == 'CH':
                yield Days, dict(actionBCH=5, actionRESell=0, priceCH=cu(5), actionD=0)
                yield Results
                expect(Constants.InitCHBalance + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            if self.player.role_own == 'UC' and self.player.id_in_group == 2:
                yield Days, dict(actionSUC=1, actionPP=4, priceUC=cu(5), actionD=0)
                yield Results
                expect(Constants.InitUCBalance + self.player.payoff, self.player.participant.balance)
            if self.player.role_own == 'UC' and self.player.id_in_group == 4:
                yield Days, dict(actionSUC=2, actionPP=3, priceUC=cu(5), actionD=0)
                yield Results
                expect(Constants.InitUCBalance + self.player.payoff, self.player.participant.balance)