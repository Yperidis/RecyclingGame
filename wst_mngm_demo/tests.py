from cmath import exp
from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import json


class PlayerBot(Bot):
    def play_round(self):
        RN = self.round_number

        #### sanity checks for round 1
        # if self.player.role_own == 'RE':
        #     yield Days
        #     yield Results

        #### Four player game
        #### Trade with 1 UC selling to 1 CH and 1 UC selling to 2 CH. Both cases of UCplayer[0].UCOpenSupply <= and > CHplayer[0].CHOpenDemand take place. 
        if self.player.role_own == 'UC' and self.player.id_in_group == 2 and RN == 1:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield Days, dict(actionSUC=1, actionPP=4, priceUC=cu(4), actionD=0)
            ExDat = json.loads(self.player.group.ExDat)  # dictionary of transactions with IDs, items and prices
            IDs = list( ExDat.keys() )                        
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)
            expect(Store + self.player.actionSUC, self.player.participant.store)  # same for storage
            expect(Capac - self.player.actionSUC, self.player.participant.capac)  # same for capacity
            expect(str(4) + "_ID" in IDs, True)  # check whether the CH posting first (4) is in the transaction dictionary

        if self.player.role_own == 'CH' and self.player.id_in_group == 3 and RN == 1:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield Days, dict(actionBCH=5, actionRESell=0, priceCH=cu(5), actionD=0)
            ExDat = json.loads(self.player.group.ExDat)  # dictionary of transactions with IDs, items and prices
            IDs = list( ExDat.keys() )                        
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity
            expect(str(2) + "_ID" in IDs, True)  # check whether the UC posting first (2) is in the transaction dictionary

        if self.player.role_own == 'UC' and self.player.id_in_group == 4 and RN == 1:
            Bal = self.player.participant.balance
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield Days, dict(actionSUC=2, actionPP=3, priceUC=cu(5), actionD=0)
            ExDat = json.loads(self.player.group.ExDat)  # dictionary of transactions with IDs, items and prices
            IDs = list( ExDat.keys() )                        
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)
            expect(Store + self.player.actionSUC, self.player.participant.store)  # same for storage
            expect(Capac - self.player.actionSUC, self.player.participant.capac)  # same for capacity
            expect(str(3) + "_ID" in IDs and str(5) + "_ID" in IDs, True)  # check whether both the CHs (3 and 5) are in the transaction dictionary

        if self.player.role_own == 'CH' and self.player.id_in_group == 5 and RN == 1:
            Bal = self.player.participant.balance  # balance, storage and capacity before actions
            Store = self.player.participant.store
            Capac = self.player.participant.capac
            yield Days, dict(actionBCH=5, actionRESell=0, priceCH=cu(6), actionD=0)
            ExDat = json.loads(self.player.group.ExDat)  # dictionary of transactions with IDs, items and prices
            IDs = list( ExDat.keys() )                        
            yield Results
            expect(Bal + self.player.payoff, self.player.participant.balance)  # proper computation of the balance as per the payoff and the initial balance
            expect(Store + self.player.bought, self.player.participant.store)  # same for storage
            expect(Capac - self.player.bought, self.player.participant.capac)  # same for capacity
            expect(str(2) + "_ID" in IDs and str(4) + "_ID" in IDs, True)  # check whether both the UCs (2 and 4) are in the transaction dictionary