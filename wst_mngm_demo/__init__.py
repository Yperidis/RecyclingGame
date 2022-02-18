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
    role_own = models.StringField()

    # Action set: actionSUC for "store", actionPP for "push on platform" and actionD for "Dispose through standard means"
    actionSUC = models.IntegerField(min=0, max=Constants.UCCmax, initial=0, label="How many items are you willing to store?")
    actionBCH = models.IntegerField(min=0, max=Constants.CHCmax, initial=0, label="How many items are you willing to buy?")
    actionPP = models.IntegerField(min=0, max=Constants.g+Constants.UCCmax, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=Constants.pUCmin, init=Constants.pUCmin, label="Name the price you want to sell for.")
    priceCH = models.CurrencyField(min=0, max=Constants.pCHmax, init=Constants.pCHmax, label="Name the price you are willing to buy for.")
    actionD = models.IntegerField(min=0, max=Constants.g+Constants.UCCmax, label="How many items are you willing to dispose through standard means?")
    actionFwd = models.IntegerField(min=0, max=Constants.CHCmax, label="How many items are you willing to forward to another CH?")
    actionRESell = models.IntegerField(min=0, max=Constants.CHCmax, label="How many iterms are you willing to sell to an RE?")
    # WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged


# PAGES
class Days(Page):
    form_model = 'player'
    # form_fields = ['actionSUC', 'actionPP', 'actionD', 'WstType']  # the action set

    @staticmethod
    def vars_for_template(player: Player):
        if player.role_own == "RE":
            return dict()
        else:
            return dict(
                items_to_handle=player.participant.store + Constants.g
            )


    @staticmethod
    def get_form_fields(player):
        if player.role_own == 'UC':
            # return ['actionSUC', 'actionPP', 'priceUC', 'actionD', 'WstType']
            return ['actionSUC', 'actionPP', 'priceUC', 'actionD']            
        elif player.role_own == 'CH':
            # return ['actionBCH', 'actionFwd', 'actionRESell', 'priceCH', 'WstType']
            return ['actionBCH', 'actionFwd', 'actionRESell', 'priceCH']


    @staticmethod
    def error_message(player, actions):
        # PlayerFormValidation(player, actions, Constants.UC_role, Constants.CH_role, Constants.CHCmax, Constants.g, Constants.UCCmax)
        if player.role_own == 'UC':
            LHS, RHS = actions['actionSUC'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.UCCmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the stored items, pushed to platform and otherwise disposed must equal the generated waste items minus the current capacity for all rounds.'
        elif player.role_own == 'CH':
            LHS1 = actions['actionBCH']
            RHS1 = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            RHS2 = actions['actionFwd']  
            RHS3 = actions['actionRESell']
            LHS2 = Constants.CHCmax - RHS1
            if LHS1 > RHS1:
                return 'You cannot buy more than you can store.'
            if RHS2 > 0 or RHS3 > 0:
                if LHS2 < RHS2 + RHS3:
                    return 'You cannot forward or sell more than you have in store.'


    @staticmethod
    def before_next_page(player: Player, timeout_happened):  # function for backdrop processes while waiting
        participant = player.participant

        if player.role_own == 'UC':
            participant.UCOpenSupply = player.actionPP  # flags for keeping track of what was actually sold and bought to be displayed at the results
        elif player.role_own == 'CH':            
            participant.CHOpenDemand = player.actionBCH

        import time

        participant.wait_page_arrival = time.time()  # recording the players' arrival times at the wait pages


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    pass


def creating_session(subsession):
    new_structure = [list(range(1,Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    subsession.set_group_matrix(new_structure)
    players = subsession.get_players()
    subsession.group_randomly(fixed_id_in_group=True)  # for grouping players randomly upon initialisation but keeping roles constant throughout the rounds    
    roles = ['UC', 'CH', 'RE']
    num_UCCH = len(roles) - 1

    for player in players:
        if player.id_in_group == 1:
            player.role_own = roles[2]
        elif player.id_in_group % num_UCCH == 1:
            player.role_own = roles[0]
        else:
            player.role_own = roles[1]
        if player.round_number == 1 and (player.role_own == 'UC' or player.role_own == 'CH'):
            if player.role_own == 'UC':
                player.participant.capac = Constants.UCCmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
            else:
                player.participant.capac = Constants.CHCmax
            # player.participant.traded = 0  # initialization for a flag on whether the PP or the SCH action has been spent during the payoff process
            player.participant.store = 0  # initialize storage as it is going to appear on Days.html before being affected (see payoffs)
            player.participant.balance = Constants.InitBalance  # initialize balance


def set_payoffs(subsession):
    players = subsession.get_players()
    UCPayoffnRest(players, 'UC', 'CH', Constants.UCCmax, Constants.CHCmax, Constants.ClP, Constants.OpTariff)


page_sequence = [Days, ResultsWaitPage, Results]
