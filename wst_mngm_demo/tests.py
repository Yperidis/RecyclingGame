from cmath import exp
from otree.api import Currency as c, currency_range, expect, Bot
from . import *
# import json


class PlayerBot(Bot):
    def play_round(self):
        RN = self.round_number

        #### Four player game (2 UCs and 2 CHs)
        #### Round 1. Trade with 1 UC selling to 1 CH and 1 UC selling to 2 CH. Both cases of UCplayer[0].UCOpenSupply <= and > CHplayer[0].CHOpenDemand take place. 
        if self.player.role_own == 'CH' and self.player.id_in_group == 1 and RN == 1:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionBCH=5, priceCH=cu(5))
            yield CHSellDays, dict(actionRESell=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'UC' and self.player.id_in_group == 2 and RN == 1:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionSUC=2, actionPP=3, priceUC=cu(5), actionD=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)
            expect(self.player.actionSUC, self.player.participant.store)  # same for storage
            expect(Capac - self.player.actionSUC, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'CH' and self.player.id_in_group == 3 and RN == 1:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionBCH=5, priceCH=cu(6))
            yield CHSellDays, dict(actionRESell=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'UC' and self.player.id_in_group == 4 and RN == 1:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionSUC=1, actionPP=4, priceUC=cu(4), actionD=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(self.player.actionSUC, self.player.participant.store)  # same for storage
            expect(Capac - self.player.actionSUC, self.player.participant.capac)  # same for capacity

        #### Round 2. Trade with 1 UC partially selling to 1 CH, partially storing and partially disposing. The other UC partially trades to the other CH but because of insufficient demand stores the rest and due to lack of capacity disposes as well.
        if self.player.role_own == 'CH' and self.player.id_in_group == 1 and RN == 2:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionBCH=0, priceCH=cu(5))
            yield CHSellDays, dict(actionRESell=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'UC' and self.player.id_in_group == 2 and RN == 2:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionSUC=2, actionPP=0, priceUC=cu(5), actionD=5)                       
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)
            expect(self.player.actionSUC, self.player.participant.store)  # same for storage
            expect(Constants.UCCmax - self.player.actionSUC, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'CH' and self.player.id_in_group == 3 and RN == 2:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionBCH=0, priceCH=cu(6))
            yield CHSellDays, dict(actionRESell=0)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity

        if self.player.role_own == 'UC' and self.player.id_in_group == 4 and RN == 2:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield UniversalDays, dict(actionSUC=1, actionPP=5, priceUC=cu(4), actionD=0)  # 6 items to handle (1 in storage + g)
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(self.player.actionSUC + self.player.actionPP, self.player.participant.store)  # 
            expect(Constants.UCCmax - self.player.participant.store, self.player.participant.capac)  # same for capacity