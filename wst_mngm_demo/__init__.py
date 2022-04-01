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
    pExt = cu(10)  # price per item for external goods
    pDep = pExt/10  # deposit price per item
    g = 5  # rate of waste (item generation per day-round)
    Penalty = cu(35)  # Inactivity penalty (irresponsible disposal, hygiene hazard, etc.)
    InitUCBalance, InitCHBalance = (g * pExt + Penalty) * num_rounds, cu(500)  # monetary balance (in currency units) at the start of the experiment. Should suffice for the UCs buying only externally for the length of the experiment (rate of generation x p_c) and incurring the inactivity penalty.
    UCCmax = 6  # maximum item storage capacity for UC. In this rough form not taking size or weight into account UCCmax>=g.
    CHCmax = 4*UCCmax  # maximum item storage capacity for CH (4x that of UC to meet the difference in UC and CH role allocation (4:1) in the game)
    OpTariff = cu(25)  # fee for operator waste handling
    # ItemDep = {'Cutlery' : cu(3), 'Bulky' : cu(7), 'Cups' : cu(4)}  # dictionary for various recyclables (PE6) and their deposit value
    pUCInit, pCHInit = cu(5), cu(5)  # initial price at which UC and CH are willing to sell
    CHQc = UCCmax  # Critical quantity for CH (above which selling to an RE becomes profitable in respect to the item deposit)
    pCHSellMax = UCCmax * pDep  # Upper bound for profit of CH
    pCirMin = pDep/5  # Lower bound of price at which the waste material can be reintroduced in the circular economy
    GlobalTimeout = 5  # Timeout for pages


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
    actionPP = models.IntegerField(min=0, initial=0, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=cu(0), initial=Constants.pUCInit, label="Name the price you are willing to sell items for.")
    priceCH = models.CurrencyField(min=Constants.pDep, initial=Constants.pCHInit, label="Name the price you are willing to buy items for (at least their deposit " + str(Constants.pDep) + ").")
    actionD = models.IntegerField(min=0, initial=0, label="How many items are you willing to dispose through standard means?")
    TimeOut = models.BooleanField(initial=False)  # a timeout signaling variable
    # WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged

    # Fields not set by participant for payoff calculation
    wait_page_arrival = models.FloatField()
    UCOpenSupply = models.IntegerField(initial=0)
    CHOpenDemand = models.IntegerField()
    sold = models.IntegerField(initial=0)
    bought = models.IntegerField(initial=0)


# PAGES
class UniversalDays(Page):
    form_model = 'player'
    timeout_seconds = Constants.GlobalTimeout
    # form_fields = ['actionSUC', 'actionPP', 'actionD', 'WstType']  # the action set


    @staticmethod
    def vars_for_template(player: Player):
        if player.role_own == "UC": 
            items_to_handle = player.participant.store + Constants.g
            SurvivalCosts = Constants.pExt * Constants.g
            player.participant.balance -= SurvivalCosts
            return dict(items_to_handle=items_to_handle, SurvivalCosts=SurvivalCosts)


    @staticmethod
    def get_form_fields(player):
        if player.role_own == 'UC':
            return ['actionSUC', 'actionPP', 'priceUC', 'actionD']            
        elif player.role_own == 'CH':
            return ['actionBCH', 'priceCH']


    @staticmethod
    def error_message(player, actions):
        if player.role_own == 'UC':
            LHS, RHS = actions['actionSUC'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.UCCmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the items in store, pushed to platform and otherwise disposed must equal the generated waste items plus the current storage for all rounds.'
            if amount > 0:
                return "The price you are asking per item exceeds that of the item's deposit in the circular economy by " + str(amount) + ". Try a lower one."
        elif player.role_own == 'CH':
            amount = actions['priceCH'] + Constants.CHgain - Constants.pExt
            LHS = actions['actionBCH']
            RHS = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            if LHS > RHS:
                return 'You cannot buy more than you can store.'
            if player.participant.balance - LHS * actions['priceCH'] <= 0:
                return 'You cannot afford to buy this quantity.'  # TODO consider debt incurrence here


    @staticmethod
    def before_next_page(player: Player, timeout_happened):  # function for backdrop processes while waiting
        if player.role_own == 'UC':
            player.UCOpenSupply = player.actionPP  # flags for keeping track of what was actually sold and bought to be displayed at the results
        elif player.role_own == 'CH':
            player.CHOpenDemand = player.actionBCH

        if timeout_happened:
            player.TimeOut = True

        import time

        player.wait_page_arrival = time.time()  # recording the players' arrival times at the wait pages


class CHSellDays(Page):
    form_model = 'player'
    timeout_seconds = Constants.GlobalTimeout

    @staticmethod
    def is_displayed(player):
        return player.role_own == 'CH'


    @staticmethod
    def get_form_fields(player):
        if player.role_own == 'CH':
            return ['actionRESell']


    @staticmethod
    def vars_for_template(player: Player):
        if player.role_own == "CH":
            items_to_handle = player.participant.store
        return dict(items_to_handle=items_to_handle)


    @staticmethod
    def error_message(player, actions):
        if player.role_own == 'CH':
            LHS = actions['actionRESell']
            RHS = player.participant.store
            if LHS > RHS: 
                return 'You cannot sell more than you have in store.'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    timeout_seconds = Constants.GlobalTimeout


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


page_sequence = [UniversalDays, CHSellDays, ResultsWaitPage, Results]
