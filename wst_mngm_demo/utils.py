def Initialization(subsession, Constants):
    new_structure = [list(range(1, Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    subsession.set_group_matrix(new_structure)
    players = subsession.get_players()
    subsession.group_randomly(fixed_id_in_group=True)  # for grouping players randomly upon initialisation but keeping roles constant throughout the rounds    
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
            elif player.role_own == 'CH':
                player.participant.capac = Constants.CHCmax
                player.participant.balance = Constants.InitCHBalance  # initialize balance for CH
            player.participant.store = 0  # initialize storage as it is going to appear on Days.html before being affected (see payoffs)
            
