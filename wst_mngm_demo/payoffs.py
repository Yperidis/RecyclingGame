def Trading(players, CUCr, Cg, CClp, COpT, UCCmax): 
    for player in players:
        next_player = player.in_round(player.round_number + 1)
        if player.role == CUCr:
            wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
            if player.participant.capac >= Cg:
                if player.actionD > 0:
                    player.payoff = player.actionPP * CClp - COpT  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
                    next_player.participant.capac = UCCmax - player.actionSUC  # recurisve calculation for capacity
                else:
                    player.payoff = player.actionPP * CClp  # payoff formula without standard means disposal
                    next_player.participant.capac = UCCmax - player.actionSUC
            else:
                raise ValueError('The player generates more than they can store. Fix capacity against waste generation.')