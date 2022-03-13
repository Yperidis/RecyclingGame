def Transactions(group, Constants):
    import json
    players = group.get_players()
    wpatUC = { player : player.wait_page_arrival for player in players if player.role_own == 'UC' }  # dictionary of player ID-wait page arrival time
    wpatCH = { player : player.wait_page_arrival for player in players if player.role_own == 'CH' }
    UCWTsort, CHWTsort = sorted( zip( wpatUC.keys(), wpatUC.values()), key=lambda pair : pair[1] ), sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] )  # sort UC and CH IDs following their waiting time ascending
    # UCtemp, CHtemp = {}, {}  # dictionaries-ledgers to store UC and CH transactions
    ExDat = {}
    for UCplayer in UCWTsort:  # "first come" UC order
        UCplayer[0].participant.capac = Constants.UCCmax - UCplayer[0].actionSUC  # UC recursive capacity relation
        UCplayer[0].participant.store = UCplayer[0].actionSUC  # calculate current UC storage
        for CHplayer in CHWTsort:  # "first come" CH order
            if UCplayer[0].priceUC <= CHplayer[0].priceCH:  # condition for the trade to take place
                if CHplayer[0].CHOpenDemand > 0:  # the demand of the CH in question is non-zero
                    ClPr = (UCplayer[0].priceUC + CHplayer[0].priceCH)/2  # the clearing price (middle between stated prices)
                    if UCplayer[0].UCOpenSupply <= CHplayer[0].CHOpenDemand:  # check the relationship between the UC offer and the CH demand
                        CHplayer[0].CHOpenDemand -= UCplayer[0].UCOpenSupply  # track the remaining supply of the CH in question
                        CHplayer[0].bought += UCplayer[0].UCOpenSupply  # items bought
                        UCplayer[0].payoff = UCplayer[0].UCOpenSupply * ClPr  # pay per the UC PP quantity
                        UCplayer[0].participant.balance += UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff -= UCplayer[0].UCOpenSupply * ClPr
                        CHplayer[0].participant.balance += CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac -= UCplayer[0].UCOpenSupply  # CH recursive capacity relation
                        CHplayer[0].participant.store += UCplayer[0].UCOpenSupply  # CH recursive storage relation
                        UCplayer[0].UCOpenSupply = 0  # same for UC
                        if str(UCplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"].append(CHplayer[0].id_in_group)
                            ExDat[str(UCplayer[0].id_in_group) + "_items"].append(UCplayer[0].actionPP)
                            ExDat[str(UCplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"] = [CHplayer[0].id_in_group]
                            ExDat[str(UCplayer[0].id_in_group) + "_items"] = [UCplayer[0].actionPP]
                            ExDat[str(UCplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        if str(CHplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"].append(UCplayer[0].id_in_group)
                            ExDat[str(CHplayer[0].id_in_group) + "_items"].append(UCplayer[0].actionPP)
                            ExDat[str(CHplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"] = [UCplayer[0].id_in_group]
                            ExDat[str(CHplayer[0].id_in_group) + "_items"] = [UCplayer[0].actionPP]
                            ExDat[str(CHplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        # UCtemp.update( { UCplayer[0].id_in_group : (UCplayer[0].actionPP, str( UCplayer[0].payoff) ) } )
                        # CHtemp.update( { CHplayer[0].id_in_group : (UCplayer[0].actionPP, str( UCplayer[0].payoff) ) } )
                    else:  # partial fulfillment of UC offer from available demand (CH)
                        CHplayer[0].bought += CHplayer[0].CHOpenDemand  # items bought
                        UCplayer[0].UCOpenSupply -= CHplayer[0].CHOpenDemand  # same for the UC
                        UCplayer[0].payoff += CHplayer[0].CHOpenDemand * ClPr  # pay per the CH stor quantity
                        UCplayer[0].participant.balance += UCplayer[0].payoff  # track the UC balance
                        CHplayer[0].payoff = -CHplayer[0].CHOpenDemand * ClPr
                        CHplayer[0].participant.balance += CHplayer[0].payoff  # track the CH balance
                        CHplayer[0].participant.capac -= CHplayer[0].CHOpenDemand  # CH recursive capacity relation
                        CHplayer[0].participant.store += CHplayer[0].CHOpenDemand  # CH recursive storage relation
                        CHplayer[0].CHOpenDemand = 0  # track the remaining demand of the CH in question
                        if str(UCplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"].append(CHplayer[0].id_in_group)
                            ExDat[str(UCplayer[0].id_in_group) + "_items"].append(CHplayer[0].bought)
                            ExDat[str(UCplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"] = [CHplayer[0].id_in_group]
                            ExDat[str(UCplayer[0].id_in_group) + "_items"] = [CHplayer[0].bought]
                            ExDat[str(UCplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        if str(CHplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"].append(UCplayer[0].id_in_group)
                            ExDat[str(CHplayer[0].id_in_group) + "_items"].append(CHplayer[0].bought)
                            ExDat[str(CHplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"] = [UCplayer[0].id_in_group]
                            ExDat[str(CHplayer[0].id_in_group) + "_items"] = [CHplayer[0].bought]
                            ExDat[str(CHplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        # UCtemp.update( { UCplayer[0].id_in_group : (CHplayer[0].bought, str( UCplayer[0].payoff) ) } )
                        # CHtemp.update( { CHplayer[0].id_in_group : (CHplayer[0].bought, str( UCplayer[0].payoff) ) } )
                    # CHplayer[0].UCExDat = json.dumps( UCtemp )  # parse for passing UC exchanges to the template
                    # UCplayer[0].CHExDat = json.dumps( CHtemp )  # parse for passing CH exchanges to the template
                    CHplayer[0].participant.store = Constants.CHCmax - CHplayer[0].participant.capac # calculate current CH storage
                    if UCplayer[0].UCOpenSupply == 0:  # if the offer of the UC in question has been spent proceed to the next UC (case of PP=0 accounted for)
                        # CHtemp = {}
                        break
                else:  # if the CH in question has met their demand proceed to the next CH
                    # UCtemp = {}  # reset ledger for UC transactions
                    continue
            else:  # no trade takes place for the given pair. Proceed to the next CH.
                continue
            # if CHplayer[0].CHOpenDemand == 0:
            #     UCtemp = {}  # in case that the open demand of the CH in question has been met the next CH tracks the next UCs and therefore we reset the ledger for UC transactions
        UCplayer[0].sold = UCplayer[0].actionPP - UCplayer[0].UCOpenSupply  # items sold
        # CHtemp = {}
        if UCplayer[0].actionD > 0 or UCplayer[0].UCOpenSupply > 0:  # calculate the costs of a potential standard disposal by choice or by items that did not reach the bargain on the platform
            DefaultOperatorCosts(UCplayer[0], Constants.OpTariff)
    for CHplayer in CHWTsort:
        if CHplayer[0].actionD > 0:  # calculate the costs of a potential standard disposal by choice for the CH
            DefaultOperatorCosts(CHplayer[0], Constants.OpTariff)
    print(ExDat)
    group.ExDat = json.dumps(ExDat)


# def CHPayoffnRest():
#     wpatCH = { player : player.wait_page_arrival for player in players if player.role_own == 'CH' }  # dictionary of player ID-wait page arrival time
#     wpatRE = { player : player.wait_page_arrival for player in players if player.role_own == 'RE' }
#     CHWTsort, REWTsort = sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] ), sorted( zip( wpatRE.keys(), wpatRE.values()), key=lambda pair : pair[1] )  # sort CH and RE IDs following their waiting time ascending


def DefaultOperatorCosts(player, ConstantsOpTariff):
    if player.role_own == 'CH':
        player.payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the CH payoff
        player.participant.balance -= ConstantsOpTariff  # update the CH balance
        player.participant.capac += player.actionD  # update the CH capacity and storage
        player.participant.store -= player.actionD

    if player.role_own == 'UC':
        player.payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the UC payoff
        player.participant.balance -= ConstantsOpTariff  # update the UC balance
