from otree.api import *


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
    actionS = models.IntegerField(min=0, max=Constants.g, initial=0, label="How many items do you want to store?")
    actionPP = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items do you want to push to the platform?")
    priceUC = models.CurrencyField(min=Constants.pUCmin, init=Constants.pUCmin, label="Name the price you want to sell for.")
    priceCH = models.CurrencyField(max=Constants.pCHmax, init=Constants.pCHmax, label="Name the price you are willing to buy for.")
    actionD = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items do you want to dispose through standard means?")
    actionFwd = models.IntegerField(min=0, label="How many items are you willing to forward to another CH?")
    actionRESell = models.IntegerField(min=0, label="How many iterms are you willing to sell to an RE?")
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
        # elif player.role == Constants.CH_role:
        #     if player.round_number == 1:
        #         return 'Initializing. Nothing to forward or sell yet.'
        #     else:
        #         LHS = actions['actionS'] + actions['actionFwd'] + actions['actionRESell']
        #         RHS = actions['actionPP'] + Constants.Cmax #- player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
        #         if LHS != RHS:  # what a CH forwards or sells cannot be more than what they can carry and what they already have in store
        #             return 'You cannot forward to another CH or sell to an RE more than you have.'


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
            player.participant.capac = Constants.Cmax - prev_player.actionS  # calculate capacity for next round


def Trading(players): 
    for player in players:
        next_player = player.in_round(player.round_number + 1)
        if player.role == Constants.UC_role:
            wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
            if player.participant.capac >= Constants.g:
                if player.actionD > 0:
                    player.payoff = player.actionPP * Constants.ClP - Constants.OpTariff  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
                    next_player.participant.capac = Constants.Cmax - player.actionS  # recurisve calculation for capacity
                else:
                    player.payoff = player.actionPP * Constants.ClP  # payoff formula without standard means disposal
                    next_player.participant.capac = Constants.Cmax - player.actionS
            else:
                raise ValueError('The player generates more than they can store. Fix capacity against waste generation.')  


def set_payoffs(subsession):
    players = subsession.get_players()
    # TODO Write the matching mechanism, when trading takes place and the alternatives


page_sequence = [Days, ResultsWaitPage, Results]