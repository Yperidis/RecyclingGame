def Initialization(subsession, Constants):
    # new_structure = [list(range(1, Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    # subsession.set_group_matrix(new_structure)
    groups = subsession.get_groups()
    players = subsession.get_players()
    # subsession.group_randomly(fixed_id_in_group=True)  # for grouping players randomly upon initialisation but keeping roles constant throughout the rounds    
    roles = ['UC', 'UC', 'CH']  # assuming two roles, the loop below will always distribute the roles cyclically up to the number of players in the group
    num_UCCH = len(roles)

    for player in players:
        # if player.id_in_group == 1:
        #     player.role_own = roles[2]  # RE assignment
        # if player.id_in_group % num_UCCH == 0:
        #     player.role_own = roles[0]  # UC assignment
        # else:
        #     player.role_own = roles[1]  # CH assignment
        player.role_own = roles[player.id_in_group % num_UCCH]
        if player.round_number == 1:# and (player.role_own == 'UC' or player.role_own == 'CH'):
            if player.role_own == 'UC':
                player.participant.capac = Constants.UCCmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
                player.participant.balance = Constants.InitUCBalance  #- Constants.g * Constants.pExt # initialize balance and cost of initial waste deposit costs for survival of UC
                player.participant.SurvCost = Constants.pExt  # variable for tracking the survival costs (initialized with the default, external price)
            elif player.role_own == 'CH':
                player.participant.capac = Constants.CHCmax
                player.participant.balance = Constants.InitCHBalance  # initialize balance for CH
            player.participant.store = 0  # initialize storage as it is going to appear on Days.html before being affected (see payoffs)

    for group in groups:
        group_rounds = group.in_rounds(1, Constants.num_rounds)
        for group_round in group_rounds:
            if group.id_in_subsession % 3 == 1:
                group_round.treatmentPopUp = True
            elif group.id_in_subsession % 3 == 2:
                group_round.treatmentLearnMore = True


def ResetFields(group, Constants):
    players = group.get_players()
    roles = ['UC', 'CH']  # assuming two roles, the loop below will always distribute the roles cyclically up to the number of players in the group
    num_UCCH = len(roles)    
    for player in players:
        # if player.id_in_group == 1:
        #     player.role_own = roles[2]  # RE assignment
        if player.id_in_group % num_UCCH == 0:
            player.role_own = roles[0]  # UC assignment
        else:
            player.role_own = roles[1]  # CH assignment
        if player.round_number == 1:# and (player.role_own == 'UC' or player.role_own == 'CH'):
            if player.role_own == 'UC':
                player.participant.capac = Constants.UCCmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
                player.participant.balance = Constants.InitUCBalance  #- Constants.g * Constants.pExt # initialize balance and cost of initial waste deposit costs for survival of UC
                player.participant.SurvCost = Constants.pExt  # variable for tracking the survival costs (initialized with the default, external price)
            elif player.role_own == 'CH':
                player.participant.capac = Constants.CHCmax
                player.participant.balance = Constants.InitCHBalance  # initialize balance for CH
            player.participant.store = 0  # initialize storage as it is going to appear on Days.html before being affected (see payoffs)
            player.participant.DropoutCounter = 0  # initializing the drop-out counter for each player