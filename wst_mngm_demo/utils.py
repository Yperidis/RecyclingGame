def PlayerFormValidation(player, actions, CUC, CCH, CCHCmax, Cg, CUCCmax):
    if player.role == CUC:
        LHS, RHS = actions['actionSUC'] + actions['actionPP'] + actions['actionD'], Cg + CUCCmax - player.participant.capac
        if LHS != RHS:
            return 'The sum of the stored items, pushed to platform and otherwise disposed must equal the generated waste items minus the current capacity for all rounds.'
    elif player.role == CCH:
        LHS1 = actions['actionSCH']
        RHS1 = player.participant.capac  # TODO pick a UC and include what they pushed in the round at hand (the criteria for the picked one are: 1. that the CH maximizes their profit, 2. that the CH is closest to the UC and 3. that the UC is willing to pair)
        RHS2 = actions['actionFwd']  
        RHS3 = actions['actionRESell']
        LHS2 = CCHCmax - RHS1
        if LHS1 > RHS1:
            return 'You cannot store more than you can carry.'
        if RHS2 > 0 or RHS3 > 0:
            if LHS2 < RHS2 + RHS3:
                return 'You cannot forward or sell more than you have in store.'
