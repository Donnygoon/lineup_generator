# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 08:50:20 2018

@author: Don
"""
from itertools import combinations
import time
import pandas as pd


def OwnDST(player):
    if player["OwnPer"] > 0.1:
        return pd.Series({"DSTRB": 0, "DSTWR": 0, "DSTTE": 0, "DSTQB": 0})
    norm_own = 1 - (player["OwnPer"] / 0.1) ** 3

    return pd.Series(
        {"DSTRB": norm_own, "DSTWR": norm_own, "DSTTE": norm_own, "DSTQB": norm_own}
    )


def Gen_Comb(Flex, num):
    combos = pd.DataFrame(
        list(combinations(Flex, num)),
        columns=["Flex" + str(y) for y in range(1, num + 1)],
    )
    combos = combos[
        (combos["Flex1"] != combos["Flex2"])
        & (combos["Flex1"] != combos["Flex3"])
        & (combos["Flex2"] != combos["Flex3"])
    ]
    # for x in combos: print x
    return combos


def GenDST4(Dir, year, week, Mult=1.0):
    RB_DST = 0.07
    Opp_WR = 0.00
    Opp_RB = 0.00

    # Speed constraint recommended 100 for live lineups
    # dst_Per = [2000,80,15,3]
    dst_Per = [1000, 50, 10, 2]
    # Speed constraint recommend 4.0
    min_Points = 7.0

    RRPC = 2.0

    FullDST = pd.DataFrame()

    Flex4Fill = pd.read_csv(Dir + week + "/MidSteps/PredictFlex.csv")
    QBs = pd.read_csv(Dir + week + "/MidSteps/OwnUpQB.csv")
    DSTs = pd.read_csv(Dir + week + "/MidSteps/PredictDST.csv")

    DSTs[["DSTRB", "DSTWR", "DSTTE", "DSTQB"]] = DSTs.apply(OwnDST, axis=1)

    categorical = ["Gametime", "Team", "Opp_Team", "Pos"]

    for cat in categorical:
        DSTs[cat] = DSTs[cat].astype("category")
        QBs[cat] = QBs[cat].astype("category")
        Flex4Fill[cat] = Flex4Fill[cat].astype("category")

    QBOwn = QBs[["Team", "OwnPer"]].groupby("Team").head(1).reset_index(drop=True)
    Flex4Fill = Flex4Fill.merge(
        QBOwn, left_on="Team", right_on="Team", how="left", suffixes=("", "_QB")
    )
    # Flex4Fill['OwnPenalty'] = Flex4Fill.apply(OwnExpectedValue,axis=1)
    # Flex4Fill['CheapSalBonus'] = Flex4Fill.apply(SalBonus,axis=1)
    # Flex4Fill['Expected_Points'] = Flex4Fill['Expected_Points']*Flex4Fill['OwnPenalty']*Flex4Fill['CheapSalBonus']
    Flex4Fill = Flex4Fill[
        (Flex4Fill["Expected_Points"] > min_Points) & (Flex4Fill["PointPerCost"] > 2)
    ]
    Flex4Fill["Expected_Points"] = Flex4Fill["Predicted_Points"]

    # Potential Fill Mults
    try:
        FillMult = pd.read_csv(Dir + week + "/ManInputs/FillMults.csv")
        Flex4Fill = Flex4Fill.merge(
            FillMult, left_on="Name_ID", right_on="Name_ID", how="left"
        )
        Flex4Fill.fillna(1.0, inplace=True)
        Flex4Fill["Expected_Points"] = (
            Flex4Fill["Expected_Points"] * Flex4Fill["Fill_Mult"]
        )
        # print Flex4Fill
    except:
        print("No Fill Mults")

    Flex4Fill.to_csv(Dir + week + "/MidSteps/FlexPen.csv")
    # sys.exit()

    # DSTs['Expected_Points']= DSTs.apply(OwnPenDST,axis=1)
    DSTs["Expected_Points"] = DSTs["Predicted_Points"]
    # DSTs.to_csv(Dir+week+'/MidSteps/DSTPen.csv')
    # sys.exit()
    # DSTs.to_csv(Dir+week+'/MidSteps/DSTPen.csv')

    DstCombos = Gen_Comb(Flex4Fill["ID"].values, 4)
    Flex4Fill = Flex4Fill.set_index("ID", drop=True)
    DstCombos = DstCombos.merge(
        Flex4Fill[
            [
                "Name_ID",
                "Pos",
                "Cost",
                "Rec_Tds",
                "Rec_Yds",
                "Rush_Tds",
                "Rush_Yds",
                "Team",
                "Opp_Team",
                "Predicted_Points",
                "RecRatio",
                "RB_Percent_Rush",
                "OwnPer",
            ]
        ],
        left_on="Flex1",
        right_index=True,
        how="left",
    )
    DstCombos = DstCombos.merge(
        Flex4Fill[
            [
                "Name_ID",
                "Pos",
                "Cost",
                "Rec_Tds",
                "Rec_Yds",
                "Rush_Tds",
                "Rush_Yds",
                "Team",
                "Opp_Team",
                "Predicted_Points",
                "RecRatio",
                "RB_Percent_Rush",
                "OwnPer",
            ]
        ],
        left_on="Flex2",
        right_index=True,
        how="left",
    )
    DstCombos = DstCombos.merge(
        Flex4Fill[
            [
                "Name_ID",
                "Pos",
                "Cost",
                "Rec_Tds",
                "Rec_Yds",
                "Rush_Tds",
                "Rush_Yds",
                "Team",
                "Opp_Team",
                "Predicted_Points",
                "RecRatio",
                "RB_Percent_Rush",
                "OwnPer",
            ]
        ],
        left_on="Flex3",
        right_index=True,
        how="left",
    )
    DstCombos = DstCombos.merge(
        Flex4Fill[
            [
                "Name_ID",
                "Pos",
                "Cost",
                "Rec_Tds",
                "Rec_Yds",
                "Rush_Tds",
                "Rush_Yds",
                "Team",
                "Opp_Team",
                "Predicted_Points",
                "RecRatio",
                "RB_Percent_Rush",
                "OwnPer",
            ]
        ],
        left_on="Flex4",
        right_index=True,
        how="left",
    )
    DstCombos.columns = [
        "ID1",
        "ID2",
        "ID3",
        "ID4",
        "Flex1",
        "Pos1",
        "Cost1",
        "Rec_Tds1",
        "Rec_Yds1",
        "Rush_Tds1",
        "Rush_Yds1",
        "Team1",
        "Opp1",
        "EV1",
        "RR1",
        "RPR1",
        "own1",
        "Flex2",
        "Pos2",
        "Cost2",
        "Rec_Tds2",
        "Rec_Yds2",
        "Rush_Tds2",
        "Rush_Yds2",
        "Team2",
        "Opp2",
        "EV2",
        "RR2",
        "RPR2",
        "own2",
        "Flex3",
        "Pos3",
        "Cost3",
        "Rec_Tds3",
        "Rec_Yds3",
        "Rush_Tds3",
        "Rush_Yds3",
        "Team3",
        "Opp3",
        "EV3",
        "RR3",
        "RPR3",
        "own3",
        "Flex4",
        "Pos4",
        "Cost4",
        "Rec_Tds4",
        "Rec_Yds4",
        "Rush_Tds4",
        "Rush_Yds4",
        "Team4",
        "Opp4",
        "EV4",
        "RR4",
        "RPR4",
        "own4",
    ]

    DstCombos = DstCombos.query(
        "(Team1 != Team2) & (Team1 != Team3) & (Team2 != Team3)&"
        "(Team1 != Team4) & (Team4 != Team3) & (Team2 != Team4)",
        engine="python",
    )
    DstCombos = DstCombos.query(
        "((Team1 != Opp2)|((RR1<@RRPC)&(RR2<@RRPC))) & ((Team1 != Opp3)|((RR1<@RRPC)&(RR3<@RRPC))) & ((Team2 != Opp3)|((RR2<@RRPC)&(RR3<@RRPC)))&"
        "((Team1 != Opp4)|((RR1<@RRPC)&(RR4<@RRPC))) & ((Team4 != Opp3)|((RR4<@RRPC)&(RR3<@RRPC))) & ((Team2 != Opp4)|((RR2<@RRPC)&(RR4<@RRPC)))",
        engine="python",
    )

    DstCombos["count_RB_DST"] = (
        (DstCombos["Pos1"] == "RB").astype(int)
        + (DstCombos["Pos2"] == "RB").astype(int)
        + (DstCombos["Pos3"] == "RB").astype(int)
        + (DstCombos["Pos4"] == "RB").astype(int)
    )
    DstCombos["count_TE_DST"] = (
        (DstCombos["Pos1"] == "TE").astype(int)
        + (DstCombos["Pos2"] == "TE").astype(int)
        + (DstCombos["Pos3"] == "TE").astype(int)
        + (DstCombos["Pos4"] == "TE").astype(int)
    )
    DstCombos["count_WR_DST"] = (
        (DstCombos["Pos1"] == "WR").astype(int)
        + (DstCombos["Pos2"] == "WR").astype(int)
        + (DstCombos["Pos3"] == "WR").astype(int)
        + (DstCombos["Pos4"] == "WR").astype(int)
    )

    DstCombos = DstCombos[
        (DstCombos["count_TE_DST"] <= 2)
        & (DstCombos["count_WR_DST"] <= 4)
        & (DstCombos["count_RB_DST"] <= 3)
        & (DstCombos["count_RB_DST"] > 0)
    ]

    DstCombos["RBOwn"] = (
        (DstCombos["Pos1"] == "RB").astype(int) * DstCombos["own1"]
        + (DstCombos["Pos2"] == "RB").astype(int) * DstCombos["own2"]
        + (DstCombos["Pos3"] == "RB").astype(int) * DstCombos["own3"]
        + (DstCombos["Pos4"] == "RB").astype(int) * DstCombos["own4"]
    )

    DstCombos["TEOwn"] = (
        (DstCombos["Pos1"] == "TE").astype(int) * DstCombos["own1"]
        + (DstCombos["Pos2"] == "TE").astype(int) * DstCombos["own2"]
        + (DstCombos["Pos3"] == "TE").astype(int) * DstCombos["own3"]
        + (DstCombos["Pos4"] == "TE").astype(int) * DstCombos["own4"]
    )

    DstCombos["WROwn"] = (
        (DstCombos["Pos1"] == "WR").astype(int) * DstCombos["own1"]
        + (DstCombos["Pos2"] == "WR").astype(int) * DstCombos["own2"]
        + (DstCombos["Pos3"] == "WR").astype(int) * DstCombos["own3"]
        + (DstCombos["Pos4"] == "WR").astype(int) * DstCombos["own4"]
    )

    DstCombos["QBRB"] = (
        (DstCombos["count_RB_DST"] == 2).astype(int)
        * ((1 - (DstCombos["RBOwn"] / 0.15) ** 3).clip(lower=0.0))
        + (DstCombos["count_RB_DST"] == 1).astype(int)
        * (1 - (DstCombos["RBOwn"] / 0.1) ** 3).clip(lower=0.0)
        + (DstCombos["count_RB_DST"] == 0).astype(int)
    )

    DstCombos["QBWR"] = (
        (DstCombos["count_WR_DST"] == 2).astype(int)
        * (1 - (DstCombos["WROwn"] / 0.15) ** 3).clip(lower=0.0)
        + (DstCombos["count_WR_DST"] == 1).astype(int)
        * (1 - (DstCombos["WROwn"] / 0.1) ** 3).clip(lower=0.0)
        + (DstCombos["count_WR_DST"] == 0).astype(int)
    )

    DstCombos["QBTE"] = (DstCombos["count_TE_DST"] == 1).astype(int) * (
        1 - (DstCombos["TEOwn"] / 0.1) ** 3
    ).clip(lower=0.0) + (DstCombos["count_TE_DST"] == 0).astype(int)

    DstCombos["WRTE"] = DstCombos["QBWR"] * DstCombos["QBTE"]

    DstCombos["Total_Cost"] = DstCombos.eval("Cost4 + Cost1 + Cost2 + Cost3")
    DstCombos["Total_EV"] = (
        DstCombos["EV4"] + DstCombos["EV1"] + DstCombos["EV2"] + DstCombos["EV3"]
    )
    print(len(DstCombos))
    DstCombos = DstCombos.sort_values("Total_EV", ascending=False)
    DstCombos = (
        DstCombos.groupby(["Total_Cost", "Flex1", "Flex2", "Flex3"])
        .head(dst_Per[3])
        .reset_index(drop=True)
    )
    print(len(DstCombos))
    DstCombos = (
        DstCombos.groupby(["Total_Cost", "Flex1", "Flex2"])
        .head(dst_Per[2])
        .reset_index(drop=True)
    )
    print(len(DstCombos))
    DstCombos = (
        DstCombos.groupby(["Total_Cost", "Flex1"])
        .head(dst_Per[1])
        .reset_index(drop=True)
    )
    print(len(DstCombos))
    DstCombos = (
        DstCombos.groupby(["Total_Cost"]).head(dst_Per[0]).reset_index(drop=True)
    )
    print(len(DstCombos))

    print(DSTs.columns)
    DSTs = DSTs[["Name_ID", "Cost", "Expected_Points", "Team", "Opp_Team", "OwnPer"]]

    DSTs.columns = ["DST", "Cost_DST", "EV_DST", "Team_DST", "DST_Opp", "Own_DST"]

    DSTs["Year"] = int(year)
    DstCombos["Year"] = int(year)
    FullDST = DstCombos.merge(DSTs, left_on="Year", right_on="Year")
    # print(FullDST.info())
    FullDST = FullDST.query(
        "(DST_Opp != Team1) &"
        "(DST_Opp != Team2) &"
        "(DST_Opp != Team3) &"
        "(DST_Opp != Team4) &"
        "((Team_DST != Team1) | (RR1 > (2.6 - RPR1))) &"
        "((Team_DST != Team4) | (RR1 > (2.6 - RPR4))) &"
        "((Team_DST != Team2) | (RR2 > (2.6 - RPR2))) &"
        "((Team_DST != Team3) | (RR3 > (2.6 - RPR3)))",
        engine="python",
    )

    FullDST["Total_Cost"] = FullDST.eval("Cost_DST + Total_Cost")

    FullDST["DST_4_own"] = (
        FullDST["Own_DST"]
        + FullDST["own1"]
        + FullDST["own2"]
        + FullDST["own3"]
        + FullDST["own4"]
    )

    cols = [
        "Flex1",
        "Flex2",
        "Flex3",
        "Flex4",
        "Team_DST",
        "Pos1",
        "Team1",
        "EV1",
        "Pos2",
        "Team2",
        "EV2",
        "Pos3",
        "Team3",
        "EV3",
        "Pos4",
        "Team4",
        "EV4",
        "Total_EV",
        "DST",
        "EV_DST",
        "DST_Opp",
        "Total_Cost",
        "count_RB_DST",
        "count_TE_DST",
        "count_WR_DST",
        "DST_4_own",
    ]

    FullDST = FullDST[cols]
    FullDST["Total_EV"] = FullDST["EV_DST"] + FullDST["Total_EV"]  # *0.8

    # =============================================================================
    #     for index, DST in DSTs.iterrows():
    #         print(index)
    #         if FullDST.empty:
    #             FullDST = Gen_DST(DstCombos,DST,RB_DST,Opp_WR,Opp_RB,dst_Per,Mult)
    #         else:
    #             FullDST = FullDST.append(Gen_DST(DstCombos,DST,RB_DST,Opp_WR,Opp_RB,dst_Per,Mult))
    # =============================================================================
    print("Length = ", len(FullDST))

    stacks = pd.read_csv(Dir + week + "/MidSteps/stack3.csv", index_col=0)
    dst_min = 50000 - stacks.Total_Salary.max() - 500
    dst_max = 50000 - stacks.Total_Salary.min()

    FullDST = FullDST[
        (FullDST["Total_Cost"] <= dst_max) & (FullDST["Total_Cost"] >= dst_min)
    ]
    print("Length = ", len(FullDST))
    cols = [
        "Flex1",
        "Flex2",
        "Flex3",
        "Flex4",
        "Team_DST",
        "Pos1",
        "Team1",
        "Pos2",
        "Team2",
        "Pos3",
        "Team3",
        "Pos4",
        "Team4",
        "DST",
        "EV_DST",
        "DST_Opp",
        "Total_Cost",
        "Total_EV",
        "count_RB_DST",
        "count_TE_DST",
        "count_WR_DST",
        "DST_4_own",
    ]
    FullDST = FullDST[cols]

    FullDST.sort_values("Total_EV", ascending=False, inplace=True)
    FullDST = FullDST.reset_index(drop=True)
    FullDST.to_pickle(Dir + week + "/MidSteps/DST4Flex.pkl")

    return FullDST


if __name__ == "__main__":
    start_time = time.time()
    DSTMult = 0.9
    year = "2017"
    for year in ["2017"]:
        dir_str = "Weeks/" + year + "_"
        for x in [str(y) for y in range(2, 3)]:
            GenDST4(dir_str, year, x, DSTMult)
    # GenDST4(dir_str, '1')
    print("--- %s Minutes ---" % ((time.time() - start_time) / 60.0))