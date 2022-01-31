def UCPayoffnRest(players, UC_role, CH_role, ConstantsUCCmax, ConstantsCHCmax, ConstantsClP, ConstantsOpTariff):
    wpatUC = { player : player.participant.wait_page_arrival for player in players if player.role_own == UC_role }  # dictionary of player ID-wait page arrival time
    wpatCH = { player : player.participant.wait_page_arrival for player in players if player.role_own == CH_role }
    UCWTsort, CHWTsort = sorted( zip( wpatUC.keys(), wpatUC.values()), key=lambda pair : pair[1] ), sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] )  # sort UC and CH IDs following their waiting time ascending sorting
    for UCplayer in UCWTsort:  # "first come" UC order
        next_UCplayer = UCplayer[0].in_round(UCplayer[0].round_number + 1)
        next_UCplayer.participant.capac = ConstantsUCCmax - UCplayer[0].actionSUC  # UC recursive capacity relation
        for CHplayer in CHWTsort:  # "first come" CH order
            next_CHplayer = CHplayer[0].in_round(CHplayer[0].round_number + 1)
            next_CHplayer.participant.capac = ConstantsCHCmax - CHplayer[0].actionBCH  # CH recursive capacity relation
            if UCplayer[0].priceUC <= CHplayer[0].priceCH:  # condition for the trade to take place
                if CHplayer[0].participant.traded == 0:  # if the demand of the CH in question is non-zero
                    # PPTrade()
                    if UCplayer[0].actionPP <= CHplayer[0].actionBCH:  # check the relationship between the UC offer and the CH demand
                        UCplayer[0].participant.traded == UCplayer[0].actionPP  # signal that the offer of the UC has been satisfied by the amount the CH is willing to store (local demand)
                        UCplayer[0].payoff = UCplayer[0].actionPP * ConstantsClP  # pay per the UC PP quantity
                        CHplayer[0].payoff = -UCplayer[0].actionPP * ConstantsClP
                    else:  # partial fulfillment of UC offer from available demand (CH)
                        CHplayer[0].participant.traded == CHplayer[0].actionBCH  # signal that the offer of the CH has been satisfied by the amount the UC is willing to sell (local supply)
                        UCplayer[0].payoff = CHplayer[0].actionBCH * ConstantsClP  # pay per the CH stor quantity
                        CHplayer[0].payoff = -CHplayer[0].actionBCH * ConstantsClP
                    if UCplayer[0].participant.traded == 1:  # if the offer of the UC in question has been spent proceed to the next UC
                        break
                else:  # if the demand of the CH in question is zero proceed to the next CH
                    continue
            else:  # no trade takes place for the given pair. Proceed to the next CH.
                continue
        if UCplayer[0].actionD > 0 or UCplayer[0].actionPP - UCplayer[0].participant.traded > 0:  # calculate the costs of a potential standard disposal by choice or by lack of satisfaction on the platform
            UCplayer[0].payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the UC payoff


def PPTrade():
    pass 