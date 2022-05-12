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
    # RE amplification parameter compared to pExt when no items/goods reach the RE (>=0).
    REAmpParam = 3
    # minimum price compared to external, for which the RE can sell back to the UCs
    pRedMin = pExt/5    
    pDep = pExt/10  # deposit price per item
    g = 5  # rate of waste (item generation per day-round)
    # Inactivity penalty at the "universal days" stage (irresponsible disposal, hygiene hazard, cost of opportunity for CH, etc.)
    UDPenalty = cu(35)
    # Inactivity penalty at the "CH sell days" stage (cost of opportunity, etc.)
    CHSDPenalty = cu(15)
    OpTariff = cu(25)  # fee for operator waste handling
    # Monetary balance (in currency units) at the start of the experiment. Should suffice for the UCs buying only externally for the length of the experiment (rate of generation x p_c). Additionally, it should suffice for the maximum of either incurring the inactivity penalty or opting for the default disposal operator for all rounds and for both players.
    InitUCBalance, InitCHBalance = (g * pExt + max(UDPenalty, OpTariff)) * \
                                    num_rounds, (UDPenalty +
                                                 max(CHSDPenalty, OpTariff)) * num_rounds
    # maximum item storage capacity for UC. In this rough form not taking size or weight into account UCCmax>=g.
    UCCmax = 6
    # maximum item storage capacity for CH (2x that of UC to meet the difference in UC and CH role allocation (4:2) in the game)
    CHCmax = 2*UCCmax
    # ItemDep = {'Cutlery' : cu(3), 'Bulky' : cu(7), 'Cups' : cu(4)}  # dictionary for various recyclables (PE6) and their deposit value
    # initial price at which UC and CH are willing to sell
    pUCInit, pCHInit = cu(5), cu(5)
    # CHQc = UCCmax  # Critical quantity for CH (above which selling to an RE becomes profitable in respect to the item deposit)
    CHCostsSell = cu(2)  # accounting for selling costs
    # Critical quantity. Arbitrary but reflecting a reasonable quantity so that buying from the RE en masse becomes profitable: No of CH x constant or the CH maximum capacity
    QREcrit = CHCmax # 2 * int(CHCostsSell/pDep)
    # For linear p-Q relation: Q_max = (beta-p_min)Q_c/(beta-pExt)
    REQmax = int( (REAmpParam*pExt - pRedMin) * QREcrit/(REAmpParam*pExt - pExt) )
    pCHSellMax = CHCmax * pDep  # Upper bound for profit of CH
    pCirMin = pDep/5  # Lower bound of price at which the waste material can be reintroduced in the circular economy
    GlobalTimeout = 195  # Timeout for pages
    RecPeriod = 2  # recycling time-window for determining RE-provided survival costs


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # a field of variable length where a dictionary of the ID - item No and price are going to be stored for displaying at the results.
    ExDat = models.StringField()
    # variable to track the overall quantities sold to the RE
    TotREQuant = models.IntegerField(initial=0)  # variable for tracking the total quantities chanelled to the RE from the CHs


class Player(BasePlayer):
    role_own = models.StringField()

    # Action set: actionSUC for "UC store", actionPP for "push on platform", actionD for "Dispose through standard means" and priceUC the bidding price per item.
    # For CH: BCH "stored through purchase", RESell "quantity to be sold to RE"
    actionSUC = models.IntegerField(
        min=0, max=Constants.UCCmax, initial=0, label="How many items are you willing to store?")
    actionBCH = models.IntegerField(
        min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to buy?")
    actionRESell = models.IntegerField(
        min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to sell?")
    actionPP = models.IntegerField(
        min=0, initial=0, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=cu(
        0), initial=Constants.pUCInit, label="Name the price you are willing to sell items for.")
    priceCH = models.CurrencyField(min=Constants.pDep, max=Constants.pCHSellMax, initial=Constants.pCHInit,
                                   label="Name the price you are willing to buy items for (at least their deposit " + str(Constants.pDep) + ").")
    actionD = models.IntegerField(
        min=0, initial=0, label="How many items are you willing to dispose through standard means?")
    # a "UniversalDays" timeout signaling variable
    UDTimeOut = models.BooleanField(initial=False)
    # a "CHSellDays" timeout signaling variable
    CHSDTimeOut = models.BooleanField(initial=False)

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
            round = player.round_number
            group = player.group
            if round > 1:  # after initialization
                import statistics
                prev_groups = group.in_rounds(
                    max(1,round-Constants.RecPeriod+1), round-1)  # average of list objects
                # prev_group = group.in_round(round-1)  # reference the group in the previous round
                TotREQuant = statistics.mean([prev_group.TotREQuant for prev_group in prev_groups])  # calculating the average amount of items chanelled to the RE over the last Constants.RecPeriod rounds (builds up to that number in case the list is smaller)
                # compare what was sold overall to the RE in the last Constants.RecPeriod rounds with the critical quantity above which they can sell items at a reduced price to the UCs compared to the external survival costs.
                if TotREQuant > Constants.QREcrit:
                    if TotREQuant <= Constants.REQmax:
                        ItemPrice = (Constants.pExt-Constants.REAmpParam*Constants.pExt) / \
                                        Constants.QREcrit * TotREQuant + Constants.REAmpParam*Constants.pExt
                        # reduced survival costs supplied from the RE
                        SurvivalCosts = ItemPrice * Constants.g
                        player.participant.SurvCost = ItemPrice
                    else:
                        ItemPrice = Constants.pRedMin
                        # ItemPrice = (Constants.pExt-Constants.REAmpParam*Constants.pExt) / \
                        #                 Constants.QREcrit * Constants.REQmax + Constants.REAmpParam*Constants.pExt
                        # saturation point for price reduction as supplied from RE
                        SurvivalCosts = ItemPrice * Constants.g
                        player.participant.SurvCost = ItemPrice
                else:
                    SurvivalCosts = Constants.pExt * Constants.g  # external survival costs
                    player.participant.SurvCost = Constants.pExt
            else:
                # external survival costs for intermediate rounds
                SurvivalCosts = player.participant.SurvCost * Constants.g
                # SurvivalCosts = Constants.pExt * Constants.g
            # subtract the default survival costs from the balance
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
            LHS, RHS = actions['actionSUC'] + actions['actionPP'] + \
                actions['actionD'], Constants.g + Constants.UCCmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the items in store, pushed to platform and otherwise disposed must equal the generated waste items plus the current storage for all rounds.'
        elif player.role_own == 'CH':
            LHS = actions['actionBCH']
            # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            RHS = player.participant.capac
            if LHS > RHS:
                return 'You cannot buy more than you can store.'
            if player.participant.balance - LHS * actions['priceCH'] <= 0:
                # TODO consider debt incurrence here
                return 'You cannot afford to buy this quantity for the price you named.'

    @staticmethod
    # function for backdrop processes while waiting
    def before_next_page(player: Player, timeout_happened):
        if player.role_own == 'UC':
            # flags for keeping track of what was actually sold and bought to be displayed at the results
            player.UCOpenSupply = player.actionPP
        elif player.role_own == 'CH':
            player.CHOpenDemand = player.actionBCH

        if timeout_happened:
            player.UDTimeOut = True  # signal inactivity for templates

        import time

        # recording the players' arrival times at the wait pages
        player.wait_page_arrival = time.time()


class TransactionsWaitPage(WaitPage):
    after_all_players_arrive = 'set_transactions'


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

    @staticmethod
    # function for backdrop processes while waiting
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            if player.role_own == 'CH':
                player.CHSDTimeOut = True  # signal inactivity for templates


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_CH_earnings'


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


def set_transactions(group):
    Transactions(group, Constants)


def set_CH_earnings(group):
    PayoffsCH(group, Constants)


page_sequence = [
    UniversalDays,
    TransactionsWaitPage,
    CHSellDays,
    ResultsWaitPage,
    Results
]
