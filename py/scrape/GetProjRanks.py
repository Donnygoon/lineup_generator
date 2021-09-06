import urllib
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
from datetime import timedelta
import urllib.request
import os

# Scaper functions to get FantasyPros.com projections and Ranks
# Need to update week number in MainGetProj each week


def GetRanks(URL, Dir, week, year, folder):
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), "html.parser")
    Pos = URL.split("/")
    Pos = Pos[-1].split(".")
    Pos = Pos[0].split("-")
    Pos = Pos[-1]
    # rankHeader = ['Rank' , 'Player Name' ,'Team' , 'Matchup' ,'Best Rank' , 'Worst Rank' , 'Avg Rank' , 'Std Dev','Status']
    rankHeader = [
        "Rank",
        "Player Name",
        "Team",
        "Matchup",
        "Best Rank",
        "Worst Rank",
        "Avg Rank",
        "Std Dev",
        "proj_pts",
    ]
    table = soup.find("tbody")

    Out = Dir + week + folder + year + "_Week_" + week + "_" + Pos + "_Rankings.csv"
    listOut = list()
    for tr in table.find_all("tr"):
        row = list()
        # Status =''
        if len(tr.find_all("td")) < 2:
            continue
        for td in tr.find_all("td"):
            # Name Logic
            if len(row) == 1:
                st = td.text

                st = st.strip()

                st = st.split()
                if not st:
                    continue
                if st[-1] == "Q":
                    # Status = st[-1]
                    # print Status
                    st = st[0 : len(st) - 1]

                ct = 0
                name = ""

                while ct < len(st) - 1:
                    if len(name) > 0:
                        name = name + " " + st[ct]
                    else:
                        name = st[ct]
                    ct = ct + 1
                if Pos == "dst":

                    name = td.text

                    name = name.strip()
                    team = name.split()
                    if len(team) == 2:
                        team = team[0][:3]
                    elif len(team) == 3:
                        team = team[1].split(")")[1]
                    elif len(team) == 4:
                        team = team[2].split(")")[1]

                    team = team.upper()

                    row.append(name)
                    row.append(team)
                    continue
                row.append(name)
                if st[-1] != "Q":

                    row.append(st[-1])
                else:

                    row.append(st[-2])

            elif len(row) == 3:
                st = td.text.split()
                # print st, row
                if len(st) == 0:
                    row.append("")
                elif st[-1] != "Q":
                    row.append(st[-1])
                else:
                    # Status = st[-1]
                    # print Status
                    row.append(st[-2])

            elif (len(row) != 1) or (Pos != "dst"):
                if td.text != u"\xa0":
                    row.append(td.text)

        # x = raw_input("check:")

        # row.append(Status)
        # print row
        listOut.append(row)
    pdOut = pd.DataFrame(listOut, columns=rankHeader)

    def name_parse(ser):
        if len(ser.split()) == 3:
            return ser.split()[0] + " " + ser.split()[-1]
        else:
            return ser.split(ser[0] + ". ")[0]

    if Pos != "dst":
        pdOut["Player Name"] = pdOut["Player Name"].apply(name_parse)
    pdOut["uncertainty"] = pd.to_numeric(pdOut["Std Dev"]) ** 2 / pd.to_numeric(
        pdOut["Best Rank"]
    )
    pdOut.to_csv(Out, index=False)


def GetProj(URL, header, Dir, week, folder):
    soup = BeautifulSoup(urllib.request.urlopen(URL).read(), "html.parser")
    Pos = URL.split("/")
    Pos = Pos[-1].split(".")
    Pos = Pos[0]
    table = soup.find("tbody")
    # print table
    Out = open(Dir + week + folder + week + Pos + ".csv", "w")
    writer = csv.writer(Out)
    writer.writerow(header)
    for tr in table.find_all("tr"):
        row = list()
        NoName = 0
        if len(tr.find_all("td")) < 2:
            continue
        for td in tr.find_all("td"):
            if len(row) == 0 or NoName == 1:
                st = td.text
                st = st.strip()
                st = st.split()
                ct = 0
                name = ""

                while ct < len(st) - 1:
                    if len(name) > 0:
                        name = name + " " + st[ct]
                    else:
                        name = st[ct]
                    ct = ct + 1
                if Pos == "dst":
                    # print td
                    name = td.text
                    name = name.strip()
                    team = name.split()
                    if len(team) == 2:
                        team = team[0][:3]
                    elif len(team) == 3:
                        if (team[0][0] + team[1][0] == "NY") or (
                            team[0][0] + team[1][0] == "LA"
                        ):
                            team = team[0][0] + team[1][0] + team[2][0]
                        else:
                            team = team[0][0] + team[1][0]
                    team = team.upper()
                    # print team
                    row.append(name)
                    row.append(team)
                    continue
                if name == "":
                    NoName = 1
                    continue
                row.append(name)
                row.append(st[-1])
            elif len(row) != 1 or Pos != "dst":
                row.append(td.text)
        if NoName == 1:
            continue
        writer.writerow(row)
    Out.close()


def MainGetProj(week, year):
    Dir = "Weeks/" + year + "_"
    currentYear = datetime.now().year - (1 if datetime.now().month < 6 else 0)

    if not os.path.exists(Dir + week + "/fanduel/Inputs"):
        os.makedirs(Dir + week + "/fanduel/Inputs")
    if int(year) < currentYear:
        print("wrong year for download")
        return "wrong year for download"
    # pd_date = pd.read_csv('Weeks/'+year+'WeekSunDates.csv',parse_dates=['Date'])
    # pd_date['Date'] = pd_date['Date'] + timedelta(hours=10)

    # ==============================================================================
    #     if (pd_date[pd_date['Week']==int(week)]['Date'][0] < datetime.now())[0]:
    #         print('Error past game time for this week.')
    #         return('Error past game time for this week.')
    # ==============================================================================

    QBRankUrl = "https://www.fantasypros.com/nfl/rankings/qb.php"
    RBRankUrl = "https://www.fantasypros.com/nfl/rankings/ppr-rb.php"
    WRRankUrl = "https://www.fantasypros.com/nfl/rankings/ppr-wr.php"
    TERankUrl = "https://www.fantasypros.com/nfl/rankings/ppr-te.php"
    DSTRankUrl = "https://www.fantasypros.com/nfl/rankings/dst.php"
    QBProjUrl = "https://www.fantasypros.com/nfl/projections/qb.php?week="+ week
    RBProjUrl = (
        "https://www.fantasypros.com/nfl/projections/rb.php?scoring=PPR&week=" + week
    )
    WRProjUrl = (
        "https://www.fantasypros.com/nfl/projections/wr.php?scoring=PPR&week=" + week
    )
    TEProjUrl = (
        "https://www.fantasypros.com/nfl/projections/te.php?scoring=PPR&week=" + week
    )
    DSTProjUrl = "https://www.fantasypros.com/nfl/projections/dst.php?week=" + week

    FDRBRankUrl = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-rb.php"
    FDWRRankUrl = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-wr.php"
    FDTERankUrl = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-te.php"

    FDRBProjUrl = (
        "https://www.fantasypros.com/nfl/projections/rb.php?scoring=HALF&week=" + week
    )
    FDWRProjUrl = (
        "https://www.fantasypros.com/nfl/projections/wr.php?scoring=HALF&week=" + week
    )
    FDTEProjUrl = (
        "https://www.fantasypros.com/nfl/projections/te.php?scoring=HALF&week=" + week
    )

    URLS = [QBRankUrl, RBRankUrl, WRRankUrl, TERankUrl, DSTRankUrl]

    # =============================================================================
    #     for url in URLS:
    #         GetRanks(url,Dir,week,year,'/Inputs/FantasyPros_')
    #
    #     for url in [QBRankUrl,FDRBRankUrl,FDWRRankUrl,FDTERankUrl,DSTRankUrl]:
    #         GetRanks(url,Dir,week,year,'/fanduel/Inputs/FPProjWeek')
    #
    # =============================================================================
    QBHeader = [
        "Player Name",
        "Team",
        "pass_att",
        "pass_cmp",
        "pass_yds",
        "pass_tds",
        "pass_ints",
        "rush_att",
        "rush_yds",
        "rush_tds",
        "fumbles",
        "fpts",
    ]
    DSTHeader = [
        "Player Name",
        "Team",
        "def_sack",
        "def_int",
        "def_fr",
        "def_ff",
        "def_td",
        "def_safety",
        "def_pa",
        "def_tyda",
        "fpts",
    ]
    RBHeader = [
        "Player Name",
        "Team",
        "rush_att",
        "rush_yds",
        "rush_tds",
        "rec_att",
        "rec_yds",
        "rec_tds",
        "fumbles",
        "fpts",
    ]
    WRHeader = [
        "Player Name",
        "Team",
        "rec_att",
        "rec_yds",
        "rec_tds",
        "rush_att",
        "rush_yds",
        "rush_tds",
        "fumbles",
        "fpts",
    ]
    TEHeader = [
        "Player Name",
        "Team",
        "rec_att",
        "rec_yds",
        "rec_tds",
        "fumbles",
        "fpts",
    ]

    GetProj(QBProjUrl, QBHeader, Dir, week, "/Inputs/FPProjWeek")
    GetProj(RBProjUrl, RBHeader, Dir, week, "/Inputs/FPProjWeek")
    GetProj(WRProjUrl, WRHeader, Dir, week, "/Inputs/FPProjWeek")
    GetProj(TEProjUrl, TEHeader, Dir, week, "/Inputs/FPProjWeek")
    GetProj(DSTProjUrl, DSTHeader, Dir, week, "/Inputs/FPProjWeek")

    # =============================================================================
    #     if not os.path.exists(Dir+week+'/fanduel/Inputs'):
    #         os.makedirs(Dir+week+'/fanduel/Inputs')
    #
    #     GetProj(QBProjUrl,QBHeader,Dir,week,'/fanduel/Inputs/FPProjWeek')
    #     GetProj(FDRBProjUrl,RBHeader,Dir,week,'/fanduel/Inputs/FPProjWeek')
    #     GetProj(FDWRProjUrl,WRHeader,Dir,week,'/fanduel/Inputs/FPProjWeek')
    #     GetProj(FDTEProjUrl,TEHeader,Dir,week,'/fanduel/Inputs/FPProjWeek')
    #     GetProj(DSTProjUrl,DSTHeader,Dir,week,'/fanduel/Inputs/FPProjWeek')
    # =============================================================================

    print("Successful Download")


if __name__ == "__main__":
    week = "6"
    year = str(datetime.now().year)
    MainGetProj(week, year)
