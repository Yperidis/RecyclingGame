def Initialization(subsession, Constants):
    # new_structure = [list(range(1, Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    # subsession.set_group_matrix(new_structure)
    groups = subsession.get_groups()
    players = subsession.get_players()
    roles = ['UC', 'UC', 'CH']  # assuming two roles and six players per group, the loop below will always distribute the roles cyclically up to the number of players in the group
    num_UCCH = len(roles)

    for player in players:
        player.role_own = roles[player.id_in_group % num_UCCH]  # 4 UC and 2 CH players according to roles previously defined
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

    for group in groups:  #  allocating treatments (popup, detailed, baseline) for 3 groups
        group_rounds = group.in_rounds(1, Constants.num_rounds)
        for group_round in group_rounds:
            if group.id_in_subsession % 3 == 1 and group_round.round_number > Constants.PopUpSuppressedRoundNo:  # suppressing pop-ups on trial rounds
                group_round.treatmentPopUp = True
            elif group.id_in_subsession % 3 == 2:
                group_round.treatmentLearnMore = True


def ResetFields(group, Constants):
    players = group.get_players()
    roles = ['UC', 'UC', 'CH']  # assuming two roles and six players per group, the loop below will always distribute the roles cyclically up to the number of players in the group
    num_UCCH = len(roles)

    for player in players:
        player.role_own = roles[player.id_in_group % num_UCCH]  # 4 UC and 2 CH players according to roles previously defined
        if player.round_number == 1:# and (player.role_own == 'UC' or player.role_own == 'CH'):
            if player.role_own == 'UC':
                player.participant.capac = Constants.UCCmax  # initialise capacity as it is going to appear on Days.html before being affected (see payoffs)
                player.participant.balance = Constants.InitUCBalance  #- Constants.g * Constants.pExt # initialize balance and cost of initial waste deposit costs for survival of UC
                player.participant.SurvCost = Constants.pExt  # variable for tracking the survival costs (initialized with the default, external price)
            elif player.role_own == 'CH':
                player.participant.capac = Constants.CHCmax
                player.participant.balance = Constants.InitCHBalance  # initialize balance for CH
            player.participant.store = 0  # initialize storage as it is going to appear on Days.html before being affected (see payoffs)