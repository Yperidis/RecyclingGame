from otree.api import *
from .payoffs import *


doc = """
Your app description
"""

class Constants(BaseConstants):
    name_in_url = 'waste_management_demo'
    players_per_group = 3
    UC_role, CH_role, RE_role = 'UC', 'CH', 'RE'
    num_rounds = 3
    InitBalance = cu(1000)  # monetary balance (in currency units) at the start of the experiment for UCs
    g = 5  # rate of waste (item generation per day-round)
    Cmax = 10  # maximum item storage capacity. In this rough form not taking size or weight into account Cmax>=g.
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
    # Action set: actionS for "store", actionPP for "push on platform" and actionD for "Dispose through standard means"
    actionS = models.IntegerField(min=0, max=Constants.Cmax, initial=0, label="How many items are you willing to store?")
    actionPP = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items are you willing to push to the platform?")
    priceUC = models.CurrencyField(min=0, init=Constants.pUCmin, label="Name the price you want to sell for.")
    priceCH = models.CurrencyField(init=Constants.pCHmax, label="Name the price you are willing to buy for.")
    actionD = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items are you willing to dispose through standard means?")
    actionFwd = models.IntegerField(min=0, max=Constants.Cmax, label="How many items are you willing to forward to another CH?")
    actionRESell = models.IntegerField(min=0, max=Constants.Cmax, label="How many iterms are you willing to sell to an RE?")
    WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged
    

# PAGES
class Days(Page):
    form_model = 'player'
    # form_fields = ['actionS', 'actionPP', 'actionD', 'WstType']  # the action set

    @staticmethod
    def get_form_fields(player):
        if player.role == Constants.UC_role:
            return ['actionS', 'actionPP', 'priceUC', 'actionD', 'WstType']
        elif player.role == Constants.CH_role:
            return ['actionS', 'actionFwd', 'actionRESell', 'priceCH', 'WstType']

    @staticmethod
    def error_message(player, actions):
        if player.role == Constants.UC_role:
            LHS, RHS = actions['actionS'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.Cmax - player.participant.capac
            if LHS != RHS:
                return 'The sum of the stored items, pushed to platform and otherwise disposed must equal the generated waste items minus the current capacity for all rounds.'
        elif player.role == Constants.CH_role:
            LHS = actions['actionS']
            RHS = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
            if LHS > RHS:  # what a CH forwards or sells cannot be more than what they can carry and what they already have in store
                return 'You cannot store more than you can carry.'


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
        if player.round_number == 1 and (player.role == Constants.UC_role or player.role == Constants.CH_role):
            player.participant.capac = Constants.Cmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
        elif player.round_number > 1 and (player.role == Constants.UC_role or player.role == Constants.CH_role):
            prev_player = player.in_round(player.round_number - 1)
            player.participant.capac = Constants.Cmax - prev_player.actionS  # initialise capacity for next round


def NoTrading():
    pass

def set_payoffs(subsession):
    players = subsession.get_players()
    UCplayers = [ player.role for player in players if player.role == Constants.UC_role ]
    CHplayers = [ player.role for player in players if player.role == Constants.CH_role ]
    # Done = True
    # while Done:
    #     for UC in UCplayers:
    #         for CH in CHplayers:
    #             if UC.priceUC <= CH.priceCH:
    #                 Q = min(UC.actionPP, CH.actionS+CH.actionFwd+CH.actionRESell)
    #                 TradingUC(UC), TradingCH(CH)  # the trade and goods exchange for the pair UC-CH
    #                 CHplayers.remove(CH)  # CH is no more available to pair with a UC
    #                 break
    #             else:
    #                 NoTradingUC(UC)
    #     for CH in CHplayers:
    #         NoTradingCH(CH)
    # TODO Write the matching mechanism, when trading takes place and the alternatives
    Trading(players, Constants.UC_role, Constants.g, Constants.ClP, Constants.OpTariff, Constants.Cmax)


page_sequence = [Days, ResultsWaitPage, Results]