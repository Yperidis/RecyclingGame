def Trading(players, CUCr, Cg, CClp, COpT, CCmax): 
    for player in players:
        next_player = player.in_round(player.round_number + 1)
        if player.role == CUCr:
            wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
            if player.participant.capac >= Cg:
                if player.actionD > 0:
                    player.payoff = player.actionPP * CClp - COpT  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
                    next_player.participant.capac = CCmax - player.actionS  # recurisve calculation for capacity
                else:
                    player.payoff = player.actionPP * CClp  # payoff formula without standard means disposal
                    next_player.participant.capac = CCmax - player.actionS
            else:
                raise ValueError('The player generates more than they can store. Fix capacity against waste generation.')  


# def set_payoffs(subsession):
#     players = subsession.get_players()

#     for player in players:
#         if player.role == Constants.UC_role:
#             UC_Payoff(subsession, player)
#         elif player.role == Constants.CH_role:
#             CH_Payoff(subsession, player)


# def UC_Payoff(subsession, player):
#     wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
#     if subsession.round_number == 1:  # first round
#         if Constants.Cmax >= Constants.g:  # check whether the capacity is greater than the waste generation 
#             if player.actionD > 0:
#                 player.payoff = player.actionPP * Constants.ItemDep[wsttype] - Constants.OpTariff  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
#                 player.participant.capac = Constants.Cmax - player.actionS  # track the capacity in case of storage action
#             else:
#                 player.payoff = player.actionPP * Constants.ItemDep[wsttype]  # payoff formula for storing and pushing to platform
#                 player.participant.capac = player.actionS  # track the capacity in case of storage action
#         else:
#             raise ValueError('The player generates more than they can handle.')  
#     else:
#         prev_player = player.in_round(subsession.round_number - 1)
#         if prev_player.participant.capac >= player.actionS:  # in case of sufficient storage
#             if player.actionD > 0:
#                 player.payoff = player.actionPP * Constants.ItemDep[wsttype] - Constants.OpTariff  # payoff formula for storing, pushing to platform and flat rate for using the stadard disposal means
#                 player.participant.capac = prev_player.participant.capac - player.actionS + player.actionPP - Constants.g + player.actionD - Constants.g  # recursive relation to track the player's item capacity
#             else:
#                 player.payoff = player.actionPP * Constants.ItemDep[wsttype]  # payoff formula for storing and pushing to platform
#                 player.participant.capac = prev_player.participant.capac - player.actionS + player.actionPP - Constants.g  # recursive relation to track the player's item capacity (no stanard disposal)

# def CH_Payoff(subsession, player):
#     if subsession.round_number == 1:  # first round
#         player.payoff = 0
#     else:
#         wsttype = player.WstType  # the specified item to be exchanged TODO: check whether it's in the constant list
#         prev_player = player.in_round(subsession.round_number - 1)
#         if prev_player.participant.capac >= player.actionS:  # in case of sufficient storage
#             if player.actionFwd > 0 or player.actionRESell > 0:
#                 player.payoff = player.actionFwd * Constants.ItemDep[wsttype] + player.actionRESell * Constants.ItemDep[wsttype]  # payoff formula for forwarding to another CH pushing
#                 player.capac = prev_player.capac - player.actionS + player.actionPP - Constants.g + player.actionD - Constants.g  # recursive relation to track the player's item capacity