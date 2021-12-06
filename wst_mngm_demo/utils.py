def creating_session(subsession):
    new_structure = [list(range(1,Constants.players_per_group+1))]  # prerequisite to set the number of players in a tabular structure for grouping purposes
    subsession.set_group_matrix(new_structure)
    players = subsession.get_players()
    subsession.group_randomly()  # for grouping players randomly in each round    

    for player in players:
        if subsession.round_number == 1 and player.role == Constants.UC_role and player.role == Constants.CH_role:
            player.participant.capac = Constants.Cmax  # this is to maintain the capacity over all rounds
            print(player.participant.capac)
        elif subsession.round_number > 1 and player.role == Constants.UC_role and player.role == Constants.CH_role:
            prev_player = player.in_round(subsession.round_number - 1)
            player.participant.capac = Constants.Cmax - prev_player.actionS  # this is to maintain the capacity over all rounds