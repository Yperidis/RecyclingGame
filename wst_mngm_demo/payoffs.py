def UCPayoffnRest(subsession, Constants):
# def UCPayoffnRest(subsession, ConstantsUCCmax, ConstantsCHCmax, ConstantsOpTariff):
    import json
    players = subsession.get_players()
    wpatUC = { player : player.wait_page_arrival for player in players if player.role_own == 'UC' }  # dictionary of player ID-wait page arrival time
    wpatCH = { player : player.wait_page_arrival for player in players if player.role_own == 'CH' }
    UCWTsort, CHWTsort = sorted( zip( wpatUC.keys(), wpatUC.values()), key=lambda pair : pair[1] ), sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] )  # sort UC and CH IDs following their waiting time ascending
    for UCplayer in UCWTsort:  # "first come" UC order
        UCplayer[0].participant.capac = Constants.UCCmax - UCplayer[0].actionSUC  # UC recursive capacity relation
        UCplayer[0].participant.store = UCplayer[0].actionSUC  # calculate current UC storage
        for CHplayer in CHWTsort:  # "first come" CH order
            if CHplayer[0].actionD > 0:  # calculate the costs of a potential standard disposal by choice for the CH
                DefaultOperatorCosts(CHplayer[0], Constants.OpTariff)
            if UCplayer[0].priceUC <= CHplayer[0].priceCH:  # condition for the trade to take place
                if CHplayer[0].CHOpenDemand > 0:  # the demand of the CH in question is non-zero
                    UCplayer[0].ClPr = min(UCplayer[0].priceUC, CHplayer[0].priceCH)  # the clearing price
                    CHplayer[0].ClPr = UCplayer[0].ClPr
                    if UCplayer[0].actionPP <= CHplayer[0].actionBCH:  # check the relationship between the UC offer and the CH demand
                        UCplayer[0].UCOpenSupply -= UCplayer[0].actionPP  # track the remaining supply of the UC in question
                        CHplayer[0].CHOpenDemand -= UCplayer[0].actionPP  # same for CH
                        CHplayer[0].bought = CHplayer[0].actionBCH - CHplayer[0].CHOpenDemand  # items bought
                        UCplayer[0].payoff = UCplayer[0].actionPP * UCplayer[0].ClPr # ConstantsClP  # pay per the UC PP quantity
                        UCplayer[0].participant.balance = UCplayer[0].participant.balance + UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff -= UCplayer[0].actionPP * UCplayer[0].ClPr # ConstantsClP
                        CHplayer[0].participant.balance += CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac -= UCplayer[0].actionPP  # CH recursive capacity relation
                        CHplayer[0].ExDat += json.dumps( { CHplayer[0].id_in_group : (CHplayer[0].bought, float( CHplayer[0].payoff) ) } )
                    else:  # partial fulfillment of UC offer from available demand (CH)
                        CHplayer[0].CHOpenDemand -= CHplayer[0].actionBCH  # track the remaining demand of the CH in question
                        CHplayer[0].bought = CHplayer[0].actionBCH  # items bought
                        UCplayer[0].UCOpenSupply -= CHplayer[0].actionBCH  # same for the UC
                        UCplayer[0].payoff = CHplayer[0].actionBCH * UCplayer[0].ClPr #ConstantsClP  # pay per the CH stor quantity
                        UCplayer[0].participant.balance += UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff -= CHplayer[0].actionBCH * UCplayer[0].ClPr #ConstantsClP
                        CHplayer[0].participant.balance += CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac -= CHplayer[0].actionBCH  # CH recursive capacity relation
                        CHplayer[0].ExDat += json.dumps( { CHplayer[0].id_in_group : [ CHplayer[0].bought, float( CHplayer[0].payoff) ] } )
                    CHplayer[0].participant.store = Constants.CHCmax - CHplayer[0].participant.capac # calculate current CH storage
                    if UCplayer[0].UCOpenSupply == 0:  # if the offer of the UC in question has been spent proceed to the next UC (case of PP=0 accounted for)
                        break
                else:  # if the CH in question has met their demand proceed to the next CH
                    continue
            else:  # no trade takes place for the given pair. Proceed to the next CH.
                continue
        UCplayer[0].sold = UCplayer[0].actionPP - UCplayer[0].UCOpenSupply  # items sold
        if UCplayer[0].actionD > 0 or UCplayer[0].UCOpenSupply > 0:  # calculate the costs of a potential standard disposal by choice or by items that did not reach the bargain on the platform
            DefaultOperatorCosts(UCplayer[0], Constants.OpTariff)


def CHPayoffnRest():
    wpatCH = { player : player.wait_page_arrival for player in players if player.role_own == 'CH' }  # dictionary of player ID-wait page arrival time
    wpatRE = { player : player.wait_page_arrival for player in players if player.role_own == 'RE' }
    CHWTsort, REWTsort = sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] ), sorted( zip( wpatRE.keys(), wpatRE.values()), key=lambda pair : pair[1] )  # sort CH and RE IDs following their waiting time ascending



def DefaultOperatorCosts(player, ConstantsOpTariff):
    if player.role_own == 'CH':
        player.payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the CH payoff
        player.participant.balance -= ConstantsOpTariff  # update the CH balance
        player.participant.capac += player.actionD  # update the CH capacity and storage
        player.participant.store -= player.actionD

    if player.role_own == 'UC':
        player.payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the UC payoff
        player.participant.balance -= ConstantsOpTariff  # update the UC balance