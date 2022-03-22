from otree.api import *
from .payoffs import *
from .utils import *


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = 'waste_management_demo'
    players_per_group = 4
    # UC_role, CH_role = 'UC', 'CH'
    num_rounds = 3
    InitUCBalance, InitCHBalance = cu(4000), cu(500)  # monetary balance (in currency units) at the start of the experiment. Should suffice for the UCs buying only externally for the length of the experiment (rate of generation x p_c), assuming they can afford it.
    g = 5  # rate of waste (item generation per day-round)
    UCCmax, CHCmax = 6, 50  # maximum item storage capacity for UC and CH. In this rough form not taking size or weight into account UCCmax>=g.
    OpTariff = cu(25)  # fee for operator waste handling
    # ItemDep = {'Cutlery' : cu(3), 'Bulky' : cu(7), 'Cups' : cu(4)}  # dictionary for various recyclables (PE6) and their deposit value
    pUCmin = cu(5) # min(ItemDep.values())  # minimum price at which UC is willing to sell
    pExt = cu(8)  # external goods' price
    CHgain = cu(2)  # static markup for the CH (commission)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    ExDat = models.StringField()  # a field of variable length where a dictionary of the ID - item No and price are going to be stored for displaying at the results.


class Player(BasePlayer):
    role_own = models.StringField()

    #### Action set: actionSUC for "UC store", actionPP for "push on platform", actionD for "Dispose through standard means" and priceUC the bidding price per item.
    #### For CH: BCH "stored through purchase"
    actionUCBuyBool = models.BooleanField(label="Would you like to buy your necessities from the platform if available?")
    actionSUC = models.IntegerField(min=0, max=Constants.UCCmax, initial=0, label="How many items are you willing to store?")
    actionBCH = models.IntegerField(min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to buy?")
    actionRESell = models.IntegerField(min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to sell?")
    actionPP = models.IntegerField(min=0, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=cu(0), initial=cu(5), label="Name the price you want to sell for.")
    priceCH = models.CurrencyField(min=cu(0), initial=cu(5), label="Name the price you are willing to buy for.")
    actionD = models.IntegerField(min=0, initial=0, label="How many items are you willing to dispose through standard means?")
    # actionFwd = models.IntegerField(min=0, max=Constants.CHCmax, label="How many items are you willing to forward to another CH?")
    actionRESell = models.IntegerField(min=0, initial=0, max=Constants.CHCmax, label="How many items are you willing to sell to an RE?")
    # WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged

    # Fields not set by participant for payoff calculation
    wait_page_arrival = models.FloatField()
    UCOpenSupply = models.IntegerField(initial=0)
    CHOpenDemand = models.IntegerField()
    sold = models.IntegerField(initial=0)
    bought = models.IntegerField(initial=0)


# PAGES
class Days(Page):
    form_model = 'player'
    # form_fields = ['actionSUC', 'actionPP', 'actionD', 'WstType']  # the action set

    @staticmethod
    def vars_for_template(player: Player):
        # if player.role_own == "RE":
        #     items_to_handle = 0
        if player.role_own == "UC":
            items_to_handle = player.participant.store + Constants.g
        else:
            items_to_handle = player.participant.store
        return dict(items_to_handle=items_to_handle)


    @staticmethod
    def get_form_fields(player):
        if player.role_own == 'UC':
            return ['actionSUC', 'actionPP', 'priceUC', 'actionD']            
        elif player.role_own == 'CH':
            return ['actionBCH', 'actionRESell', 'priceCH']


    @staticmethod
    def error_message(player, actions):
        if player.role_own == 'UC':
            amount = actions['priceUC'] + Constants.CHgain - Constants.pExt
            LHS, RHS = actions['actionSUC'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.UCCmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the items in store, pushed to platform and otherwise disposed must equal the generated waste items plus the current storage for all rounds.'
            if amount > 0:
                return "The price you are asking per item exceeds that of the item's deposit in the circular economy by " + str(amount) + ". Try a lower one."
        elif player.role_own == 'CH':
            amount = actions['priceCH'] + Constants.CHgain - Constants.pExt
            LHS1 = actions['actionBCH']
            LHS2 = actions['actionRESell']
            RHS1 = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            RHS2 = player.participant.store
            if LHS1 - LHS2 > RHS1:
                return 'You cannot buy more than you can store.'
            if RHS2 < LHS2: 
                return 'You cannot sell or dispose more than you have in store.'
            if player.participant.balance - LHS1 * actions['priceCH'] <= 0:
                return 'You cannot afford to buy this quantity.'  # TODO consider debt incurrence here
            if amount > 0:
                return "The price you are willing to pay per item exceeds that of the item's deposit in the circular economy by " + str(amount) + ". Try a lower one."


    @staticmethod
    def before_next_page(player: Player, timeout_happened):  # function for backdrop processes while waiting
        if player.role_own == 'UC':
            player.UCOpenSupply = player.actionPP  # flags for keeping track of what was actually sold and bought to be displayed at the results
        elif player.role_own == 'CH':
            player.CHOpenDemand = player.actionBCH

        import time

        player.wait_page_arrival = time.time()  # recording the players' arrival times at the wait pages


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    @staticmethod
    def js_vars(player: Player):
        import json
        ExDat = json.loads(player.group.ExDat)
        if str(player.id_in_group) + "_ID" in ExDat:
            ids = ExDat[str(player.id_in_group) + "_ID"]
            items = ExDat[str(player.id_in_group) + "_items"]
            prices = ExDat[str(player.id_in_group) + "_price"]
        else:
            ids = []
            items = []
            prices = []
        return dict(ids=ids, items_count=items, prices=prices)


def creating_session(subsession):
    Initialization(subsession, Constants)


def set_payoffs(group):
    Transactions(group, Constants)


page_sequence = [Days, ResultsWaitPage, Results]
