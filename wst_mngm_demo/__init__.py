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
    InitItems = 0  # item load upon start
    g = 5  # rate of waste (item generation per day-round)
    Cmax = 10  # maximum item storage capacity. In this rough form not taking size or weight into account Cmax>=g.
    OpTariff = cu(20)  # fee for operator waste handling
    ItemDep = {'Cutlery' : cu(3), 'Bulky' : cu(7), 'Cups' : cu(4)}  # dictionary for various recyclables (PE6) and their deposit value


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):  
    # Action set: actionS for "store", actionPP for "push on platform" and actionD for "Dispose through standard means"
    actionS = models.IntegerField(min=0, max=Constants.g, initial=0, label="How many items do you want to store?")
    actionPP = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items do you want to push to the platform?")
    actionD = models.IntegerField(min=0, max=Constants.g+Constants.Cmax, label="How many items do you want to dispose through standard means?")
    actionFwd = models.IntegerField(min=0, label="How many items do you want to forward to another CH?")
    actionRESell = models.IntegerField(min=0, label="How many iterms do you want to sell to an RE?")
    WstType = models.StringField(choices=[['Cutlery', 'Cutlery'], ['Bulky', 'Bulky'], ['Cups', 'Cups']], label="Describe your item from the available types and upload a photo (latter N/A yet).")  # description of item to be exchanged
    

# PAGES
class Days(Page):
    form_model = 'player'
    # form_fields = ['actionS', 'actionPP', 'actionD', 'WstType']  # the action set

    @staticmethod
    def get_form_fields(player):
        if player.role == Constants.UC_role:
            return ['actionS', 'actionPP', 'actionD', 'WstType']
        elif player.role == Constants.CH_role and player.round_number > 1:
            return ['actionS', 'actionFwd', 'actionRESell', 'WstType']

    @staticmethod
    def error_message(player, actions):
        if player.role == Constants.UC_role:
            LHS, RHS = actions['actionS'] + actions['actionPP'] + actions['actionD'], Constants.g + Constants.Cmax - player.capac
            if LHS != RHS:
                return 'The sum of the stored items, pushed to platform and otherwise disposed must equal the generated waste items for all rounds.'
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
            player.capac = Constants.Cmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
        elif player.round_number > 1 and (player.role == Constants.UC_role or player.role == Constants.CH_role):
            prev_player = player.in_round(player.round_number - 1)
            # print(prev_player.round_number, prev_player.role, prev_player.participant.capac, player.participant.capac, player.role)
            player.capac = Constants.Cmax - prev_player.actionS  # calculate capacity for next round
            print(prev_player.round_number, prev_player.role, prev_player.capac, player.capac, player.role)


def set_payoffs(subsession):
    players = subsession.get_players()
    for player in players:
        if player.role == Constants.UC_role:
            wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
            if subsession.round_number == 1:  # first round
                if Constants.Cmax >= Constants.g:  # check whether the capacity is greater than the waste generation 
                    if player.actionD > 0:
                        player.payoff = player.actionPP * Constants.ItemDep[wsttype] - Constants.OpTariff  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
                        player.capac = Constants.Cmax - player.actionS  # this is what we see at the end of round 1, i.e. the status quo for round 2 (C2 in the recursive formula)
                    else:
                        player.payoff = player.actionPP * Constants.ItemDep[wsttype]  # payoff formula without standard means disposal
                        player.capac = Constants.Cmax - player.actionS
                else:
                    raise ValueError('The player generates more than they can store.')  
            else:
                prev_player = player.in_round(player.round_number - 1)
                if prev_player.capac >= player.actionS:  # in case of sufficient storage
                    if player.actionD > 0:
                        player.payoff = player.actionPP * Constants.ItemDep[wsttype] - Constants.OpTariff  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
                        player.capac = Constants.Cmax - prev_player.capac  # this is what we see at the end of round n, i.e. the status quo for round n+1 (C(n+1) in the recursive formula)
                    else:
                        player.payoff = player.actionPP * Constants.ItemDep[wsttype]  # payoff formula for storing and pushing to platform
                        player.capac = Constants.Cmax - prev_player.capac  # no stanard disposal


page_sequence = [Days, ResultsWaitPage, Results]