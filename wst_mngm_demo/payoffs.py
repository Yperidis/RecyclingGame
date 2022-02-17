def UCPayoffnRest(players, UC_role, CH_role, ConstantsUCCmax, ConstantsCHCmax, ConstantsClP, ConstantsOpTariff):
    wpatUC = { player : player.participant.wait_page_arrival for player in players if player.role_own == UC_role }  # dictionary of player ID-wait page arrival time
    wpatCH = { player : player.participant.wait_page_arrival for player in players if player.role_own == CH_role }
    UCWTsort, CHWTsort = sorted( zip( wpatUC.keys(), wpatUC.values()), key=lambda pair : pair[1] ), sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] )  # sort UC and CH IDs following their waiting time ascending sorting
    UCTraded, CHTraded = 0, 0  # flags to be used later on
    for UCplayer in UCWTsort:  # "first come" UC order
        # next_UCplayer = UCplayer[0].in_round(UCplayer[0].round_number + 1)
        UCplayer[0].participant.capac = ConstantsUCCmax - UCplayer[0].actionSUC  # UC recursive capacity relation
        UCplayer[0].participant.store = UCplayer[0].actionSUC  # calculate current UC storage
        for CHplayer in CHWTsort:  # "first come" CH order
            # next_CHplayer = CHplayer[0].in_round(CHplayer[0].round_number + 1)
            if UCplayer[0].priceUC <= CHplayer[0].priceCH:  # condition for the trade to take place
                if CHTraded == 0:  # the demand of the CH in question is non-zero
                    if UCplayer[0].actionPP <= CHplayer[0].actionBCH:  # check the relationship between the UC offer and the CH demand
                        if UCplayer[0].actionPP > 0:  # check whether we are talking about a non-zero PP value to signal appropriately
                            UCTraded = UCplayer[0].actionPP  # signal that the offer of the UC has been satisfied by the amount the CH is willing to store (local demand)
                        else:
                            UCTraded = 1
                        UCplayer[0].payoff = UCplayer[0].actionPP * ConstantsClP  # pay per the UC PP quantity
                        UCplayer[0].participant.balance = UCplayer[0].participant.balance + UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff = -UCplayer[0].actionPP * ConstantsClP
                        CHplayer[0].participant.balance = CHplayer[0].participant.balance + CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac = CHplayer[0].participant.capac - UCplayer[0].actionPP  # CH recursive capacity relation
                    else:  # partial fulfillment of UC offer from available demand (CH)
                        if CHplayer[0].actionBCH > 0:
                            CHTraded = CHplayer[0].actionBCH  # signal that the demand of the CH has been satisfied by the amount the UC is willing to sell (local supply)
                        else:
                            CHTraded = 1
                        UCplayer[0].payoff = CHplayer[0].actionBCH * ConstantsClP  # pay per the CH stor quantity
                        UCplayer[0].participant.balance = UCplayer[0].participant.balance + UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff = -CHplayer[0].actionBCH * ConstantsClP
                        CHplayer[0].participant.balance = CHplayer[0].participant.balance + CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac = CHplayer[0].participant.capac - CHplayer[0].actionBCH  # CH recursive capacity relation
                    CHplayer[0].participant.store = ConstantsCHCmax - CHplayer[0].participant.capac # calculate current CH storage
                    if UCTraded > 0:  # if the offer of the UC in question has been spent proceed to the next UC (case of PP=0 accounted for)
                        break
                else:  # if the CH in question has met their demand proceed to the next CH
                    CHTraded = 0  # reset the flag before proceeding to the next CH
                    continue
            else:  # no trade takes place for the given pair. Proceed to the next CH.
                continue
        if UCplayer[0].actionD > 0 or UCplayer[0].actionPP - UCTraded > 0:  # calculate the costs of a potential standard disposal by choice or by lack of satisfaction on the platform
        # if UCplayer[0].actionD > 0 or UCplayer[0].actionPP - UCplayer[0].participant.traded > 0:  # calculate the costs of a potential standard disposal by choice or by lack of satisfaction on the platform
            UCplayer[0].payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the UC payoff
        UCTraded = 0  # reset the flag before proceeding to the next UC
