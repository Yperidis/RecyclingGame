from otree.api import *
from .payoffs import *
# from .utils import *


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = 'waste_management_demo'
    players_per_group = 3
    # UC_role, CH_role, RE_role = 'UC', 'CH', 'RE'
    num_rounds = 3
    InitBalance = cu(1000)  # monetary balance (in currency units) at the start of the experiment for UCs
    g = 5  # rate of waste (item generation per day-round)
    UCCmax = 6  # maximum item storage capacity for UC. In this rough form not taking size or weight into account UCCmax>=g.
    CHCmax = 50  # maximum item storage capacity for CH. In this rough form not taking size or weight into account UCCmax>=g.    
    OpTariff = cu(20)  # fee for operator waste handling
    ItemDep = {'Cutlery' : cu(3), 'Bulky' : cu(7), 'Cups' : cu(4)}  # dictionary for various recyclables (PE6) and their deposit value
    pUCmin = min(ItemDep.values())  # minimum price at which UC is willing to sell
    pCHmax = max(ItemDep.values())  # maximum price at which CH is willing to buy
    ClP = (pUCmin + pCHmax)/2  # a tentative clearing price    


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def role(self):  # modify depending on the desired distribution of UCs and CHs
        roles = ['UC', 'CH', 'RE']
        num_UCCH = len(roles)-1
        if self.id_in_group == 1:
            return roles[2]
        if self.id_in_group % num_UCCH == 1:
            return roles[0]
        if self.id_in_group % num_UCCH == 0:
            return roles[1]


    # Action set: actionSUC for "store", actionPP for "push on platform" and actionD for "Dispose through standard means"
    actionSUC = models.IntegerField(min=0, max=Constants.UCCmax, initial=0, label="How many items are you willing to store?")
    actionBCH = models.IntegerField(min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to buy?")
    actionPP = models.IntegerField(min=0, max=Constants.g+Constants.UCCmax, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=Constants.pUCmin, init=Constants.pUCmin, label="Name the price you want to sell for.")
    priceCH = models.CurrencyField(min=0, max=Constants.pCHmax, init=Constants.pCHmax, label="Name the price you are willing to buy for.")
    actionD = models.IntegerField(min=0, max=Constants.g+Constants.UCCmax, label="How many items are you willing to dispose through standard means?")
    actionFwd = models.IntegerField(min=0, max=Constants.CHCmax, label="How many items are you willing to forward to another CH?")
    actionRESell = models.IntegerField(min=0, max=Constants.CHCmax, label="How many iterms are you willing to sell to an RE?")
    WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged


# PAGES
class Days(Page):
    form_model = 'player'
    # form_fields = ['actionSUC', 'actionPP', 'actionD', 'WstType']  # the action set


    @staticmethod
    def get_form_fields(player):
        if player.role == 'UC':
            return ['actionSUC', 'actionPP', 'priceUC', 'actionD', 'WstType']
        elif player.role == 'CH':
            return ['actionBCH', 'actionFwd', 'actionRESell', 'priceCH', 'WstType']


    @staticmethod
    def error_message(player, actions):
        # PlayerFormValidation(player, actions, Constants.UC_role, Constants.CH_role, Constants.CHCmax, Constants.g, Constants.UCCmax)
        if player.role == 'UC':
            LHS, RHS = actions['actionSUC'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.UCCmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the stored items, pushed to platform and otherwise disposed must equal the generated waste items minus the current capacity for all rounds.'
        elif player.role == 'CH':
            LHS1 = actions['actionBCH']
            RHS1 = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            RHS2 = actions['actionFwd']  
            RHS3 = actions['actionRESell']
            LHS2 = Constants.CHCmax - RHS1
            if LHS1 > RHS1:
                return 'You cannot store more than you can carry.'
            if RHS2 > 0 or RHS3 > 0:
                if LHS2 < RHS2 + RHS3:
                    return 'You cannot forward or sell more than you have in store.'


    @staticmethod
    def before_next_page(player: Player, timeout_happened):  # function for recording the players' arrival times at the wait pages
        participant = player.participant

        import time

        participant.wait_page_arrival = time.time()


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    pass


def creating_session(subsession):
    new_structure = [list(range(1,Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    subsession.set_group_matrix(new_structure)
    players = subsession.get_players()
    subsession.group_randomly(fixed_id_in_group=True)  # for grouping players randomly upon initialisation but keeping roles constant throughout the rounds    

    for player in players:
        if player.role == 'UC' or player.role == 'CH':
            if player.role == 'UC':
                player.participant.capac = Constants.UCCmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
            else:
                player.participant.capac = Constants.CHCmax
            player.participant.traded = 0  # initialization for a flag on whether the PP or the SCH action has been spent during the payoff process
            print(player.participant.capac)


def set_payoffs(subsession):
    players = subsession.get_players()
    UCPayoffnRest(players, 'UC', 'CH', Constants.UCCmax, Constants.CHCmax, Constants.ClP, Constants.OpTariff)


page_sequence = [Days, ResultsWaitPage, Results]