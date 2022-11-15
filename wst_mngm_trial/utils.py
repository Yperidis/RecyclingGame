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

def SurvivalCosts(group, Constants):
    players = group.get_players()
    round = group.round_number
    for player in players:
        if player.role_own == "UC":  # UC survival costs' deductions from balance
            if round > 1:  # after initialization
                import statistics
                # average of list objects from the specified previous rounds
                prev_groups = group.in_rounds(max(1, round-Constants.RecPeriod+1), round-1)
                # calculating the average amount of items chanelled to the RE over the last Constants.RecPeriod rounds (builds up to that number in case the list is smaller)
                TotREQuant = statistics.mean([prev_group.TotREQuant for prev_group in prev_groups])
                # compare what was sold overall to the RE in the last Constants.RecPeriod rounds with the critical quantity above which they can sell items at a reduced price to the UCs compared to the external survival costs.
                if TotREQuant > Constants.QREcrit:
                    if TotREQuant <= Constants.REQmax:
                        ItemPrice = (Constants.pExt-Constants.REAmpParam*Constants.pExt) / \
                            Constants.QREcrit * TotREQuant + Constants.REAmpParam*Constants.pExt
                        # reduced survival costs supplied from the RE
                        SurvivalCosts = ItemPrice * Constants.g
                        player.participant.SurvCost = ItemPrice
                    else:
                        # saturation point for price reduction as supplied from RE
                        ItemPrice = Constants.pRedMin
                        SurvivalCosts = ItemPrice * Constants.g
                        player.participant.SurvCost = ItemPrice
                else:
                    SurvivalCosts = Constants.pExt * Constants.g  # external survival costs
                    player.participant.SurvCost = Constants.pExt
            else:
                # external survival costs for intermediate rounds
                SurvivalCosts = player.participant.SurvCost * Constants.g
            # print(SurvivalCosts)
                # SurvivalCosts = Constants.pExt * Constants.g
            # subtract the default survival costs from the balance and the round's payoff
            player.participant.balance -= SurvivalCosts
            player.payoff -= SurvivalCosts