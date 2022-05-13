def Transactions(group, Constants):
    import json
    # from numpy import log, exp
    # alpha = log(float(Constants.pCHSellMax)/float(Constants.pDep))/(Constants.CHCmax - Constants.CHQc) # For the calculation of the CH-->RE sellings. WARNING! This coefficient should be placed iteratively in case the involved prices and quantities of CH are not equal for all CH.
    players = group.get_players()
    wpatUC = { player : player.wait_page_arrival for player in players if player.role_own == 'UC' }  # dictionary of player ID-wait page arrival time
    wpatCH = { player : player.wait_page_arrival for player in players if player.role_own == 'CH' }
    UCWTsort, CHWTsort = sorted( zip( wpatUC.keys(), wpatUC.values()), key=lambda pair : pair[1] ), sorted( zip( wpatCH.keys(), wpatCH.values()), key=lambda pair : pair[1] )  # sort UC and CH IDs following their waiting time ascending
    # UCtemp, CHtemp = {}, {}  # dictionaries-ledgers to store UC and CH transactions
    ExDat = {}

    # UCDim, CHDim = len(UCWTsort), len(CHWTsort)
    # UCCapac = np.zeros(UCDim)
    # SUC = 
    # UCStore = 
    # UCPrice = 
    # UCOpenSupply = 
    # UCPayoff = 
    # UCBalance = 

    for UCplayer in UCWTsort:  # "first come" UC order
        if UCplayer[0].UDTimeOut:  # monetary penalty for UC timeout
            UCplayer[0].payoff -= Constants.UDPenalty
            UCplayer[0].participant.balance += UCplayer[0].payoff
            continue
        UCplayer[0].participant.capac = Constants.UCCmax - UCplayer[0].actionSUC  # UC recursive capacity relation
        UCplayer[0].participant.store = UCplayer[0].actionSUC  # calculate current UC storage
        for CHplayer in CHWTsort:  # "first come" CH order
            if UCplayer[0].priceUC <= CHplayer[0].priceCH:  # condition for the trade to take place
                if CHplayer[0].CHOpenDemand > 0:  # the demand of the CH in question is non-zero
                    ClPr = (UCplayer[0].priceUC + CHplayer[0].priceCH)/2  # the clearing price (middle between stated prices)
                    if UCplayer[0].UCOpenSupply <= CHplayer[0].CHOpenDemand:  # check the relationship between the UC offer and the CH demand
                        CHplayer[0].CHOpenDemand -= UCplayer[0].UCOpenSupply  # track the remaining supply of the CH in question
                        CHplayer[0].bought += UCplayer[0].UCOpenSupply  # items bought
                        UCplayer[0].payoff += UCplayer[0].UCOpenSupply * ClPr  # pay per the UC PP quantity
                        CHplayer[0].payoff -= UCplayer[0].UCOpenSupply * ClPr
                        CHplayer[0].participant.capac -= UCplayer[0].UCOpenSupply  # CH recursive capacity relation
                        CHplayer[0].participant.store += UCplayer[0].UCOpenSupply  # CH recursive storage relation
                        if str(UCplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"].append(CHplayer[0].id_in_group)
                            ExDat[str(UCplayer[0].id_in_group) + "_items"].append(UCplayer[0].UCOpenSupply)
                            ExDat[str(UCplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"] = [CHplayer[0].id_in_group]
                            ExDat[str(UCplayer[0].id_in_group) + "_items"] = [UCplayer[0].UCOpenSupply]
                            ExDat[str(UCplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        if str(CHplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"].append(UCplayer[0].id_in_group)
                            ExDat[str(CHplayer[0].id_in_group) + "_items"].append(UCplayer[0].UCOpenSupply)
                            ExDat[str(CHplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"] = [UCplayer[0].id_in_group]
                            ExDat[str(CHplayer[0].id_in_group) + "_items"] = [UCplayer[0].UCOpenSupply]
                            ExDat[str(CHplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        UCplayer[0].UCOpenSupply = 0  # same for UC
                    else:  # partial fulfillment of UC offer from available demand (CH)
                        CHplayer[0].bought += CHplayer[0].CHOpenDemand  # items bought
                        UCplayer[0].UCOpenSupply -= CHplayer[0].CHOpenDemand  # same for the UC
                        UCplayer[0].payoff += CHplayer[0].CHOpenDemand * ClPr  # pay per the CH stored quantity
                        CHplayer[0].payoff -= CHplayer[0].CHOpenDemand * ClPr
                        CHplayer[0].participant.capac -= CHplayer[0].CHOpenDemand  # CH recursive capacity relation
                        CHplayer[0].participant.store += CHplayer[0].CHOpenDemand  # CH recursive storage relation
                        if str(UCplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"].append(CHplayer[0].id_in_group)
                            ExDat[str(UCplayer[0].id_in_group) + "_items"].append(CHplayer[0].CHOpenDemand)
                            ExDat[str(UCplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(UCplayer[0].id_in_group) + "_ID"] = [CHplayer[0].id_in_group]
                            ExDat[str(UCplayer[0].id_in_group) + "_items"] = [CHplayer[0].CHOpenDemand]
                            ExDat[str(UCplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        if str(CHplayer[0].id_in_group) + "_ID" in ExDat:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"].append(UCplayer[0].id_in_group)
                            ExDat[str(CHplayer[0].id_in_group) + "_items"].append(CHplayer[0].CHOpenDemand)
                            ExDat[str(CHplayer[0].id_in_group) + "_price"].append(float(ClPr))
                        else:
                            ExDat[str(CHplayer[0].id_in_group) + "_ID"] = [UCplayer[0].id_in_group]
                            ExDat[str(CHplayer[0].id_in_group) + "_items"] = [CHplayer[0].CHOpenDemand]
                            ExDat[str(CHplayer[0].id_in_group) + "_price"] = [float(ClPr)]
                        CHplayer[0].CHOpenDemand = 0  # track the remaining demand of the CH in question
                    CHplayer[0].participant.store = Constants.CHCmax - CHplayer[0].participant.capac  # calculate current CH storage
                    if UCplayer[0].UCOpenSupply == 0:  # if the offer of the UC in question has been spent proceed to the next UC (case of PP=0 accounted for)
                        break
                else:  # if the CH in question has met their demand proceed to the next CH
                    continue
            else:  # no trade takes place for the given pair. Proceed to the next CH.
                continue
        UCplayer[0].sold = UCplayer[0].actionPP - UCplayer[0].UCOpenSupply  # items sold
        UCplayer[0].participant.balance += UCplayer[0].payoff  # track the UC balance
        if UCplayer[0].UCOpenSupply > 0 and UCplayer[0].participant.capac > 0:  # unmathced demand channeled to storage up to saturation
            if UCplayer[0].UCOpenSupply <= UCplayer[0].participant.capac:  # unmatched demand smaller than current capacity (updates)
                UCplayer[0].participant.capac -= UCplayer[0].UCOpenSupply
                UCplayer[0].participant.store += UCplayer[0].UCOpenSupply
                UCplayer[0].UCOpenSupply = 0
            else:  # unmatched demand greater than current capacity (updates). Leads to operator cost at the next conditional.
                UCplayer[0].participant.store = Constants.UCCmax
                UCplayer[0].UCOpenSupply -= UCplayer[0].participant.capac
                UCplayer[0].participant.capac = 0
        if UCplayer[0].actionD > 0 or UCplayer[0].UCOpenSupply > 0:  # calculate the costs of a potential standard disposal by choice or by items that did not reach the bargain on the platform
            DefaultOperatorCosts(UCplayer[0], Constants.OpTariff)
    for CHplayer in CHWTsort:  # balance calculation for CH, part 1
        # RESellings(CHplayer[0], Constants, alpha, exp)  # CH payoffs from sellings to REs
        if CHplayer[0].UDTimeOut:  # monetary penalty for CH timeout on "universal days" stage (cost of opportunity and operations)
            CHplayer[0].payoff -= Constants.UDPenalty
        if CHplayer[0].CHSDTimeOut:  # monetary penalty for CH timeout on "CH sell days" stage (cost of opportunity and operations)
            CHplayer[0].payoff -= Constants.CHSDPenalty
        CHplayer[0].participant.balance += CHplayer[0].payoff  # update the CH balance
    # print(ExDat)
    group.ExDat = json.dumps(ExDat)


def PayoffsCH(group, Constants):
    players = group.get_players()
    wpatCH = {player: player.wait_page_arrival for player in players if player.role_own == 'CH'}
    CHWTsort = sorted(zip(wpatCH.keys(), wpatCH.values()), key=lambda pair: pair[1])  # sort UC and CH IDs following their waiting time ascending
    for CHplayer in CHWTsort:  # balance calculation for CH, part 2
        if CHplayer[0].actionRESell > 0:
            RESellings(CHplayer[0], Constants)  # CH payoffs from sellings to REs
            group.TotREQuant += CHplayer[0].actionRESell  # update the overall quantities being sold to the RE
        CHplayer[0].participant.balance += CHplayer[0].payoff  # update the CH balance


def DefaultOperatorCosts(player, ConstantsOpTariff):
    if player.role_own == 'UC':
        player.payoff -= ConstantsOpTariff  # subtract the standard disposal tariff from the UC payoff
        player.participant.balance -= ConstantsOpTariff  # update the UC balance


#def RESellings(CHplayer, Constants, alpha, exp):  # the timeout penalty has already been implemented in the transactions
def RESellings(CHplayer, Constants):  # the timeout penalty has already been implemented in the transactions
    # if CHplayer.actionRESell > Constants.CHQc:  # condition for sellings to be profitable for the CH
    #     CHplayer.payoff += Constants.pDep * Constants.CHQc + exp(alpha * ( CHplayer.actionRESell - Constants.CHQc ) )  # exponential profit-quantity relation for constants above the Qc for the CH
    # else:
    #     CHplayer.payoff += Constants.pDep * CHplayer.actionRESell  # otherwise sell at the market's item deposit price
    if CHplayer.actionRESell <= Constants.CHCmax/2:
        CHplayer.payoff += Constants.pDep * CHplayer.actionRESell - Constants.CHCostsSell  # simple functional form with constant costs of selling
    else:
        CHplayer.payoff += Constants.REAmpParam * Constants.pDep * CHplayer.actionRESell - Constants.CHCostsSell  # same function form with a multiplicative factor denoting an incentive for the CH to sell greater quantities
    CHplayer.sold = CHplayer.actionRESell  # total items sold to RE
    CHplayer.participant.store -= CHplayer.actionRESell  # remove the sold items from the storage...
    CHplayer.participant.capac += CHplayer.actionRESell  # and increase capacity respectively
