#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 21:49:30 2020

@author: dongoonetilleke
"""
import pandas as pd

pd.set_option("display.max_columns", 500)


def mil_time(x):
    time_str = x.game_time
    min_day = 0
    if "PM" in time_str:
        min_day += 12 * 60

    hours_mins = time_str.replace("PM", "").replace("AM", "").split(":")

    return min_day + int(hours_mins[0]) * 60 + int(hours_mins[1])


def game_sch(week, year):

    players = "Weeks/{}_{}/ManInputs/DKEntriesSun{}.csv".format(year, week, week)

    info_df = pd.read_csv(
        players,
        skiprows=7,
        header=0,
        usecols=["Name + ID", "Name", "ID", "Salary", "Game Info", "TeamAbbrev"],
        index_col=False,
        engine="python",
    )
    info_df.columns = ["Name_ID", "Name", "ID", "Salary", "Game_Info", "Team"]
    info_df = info_df[info_df["Game_Info"] != "Postponed"]
    info_df["game_time"] = info_df["Game_Info"].str.split().str[-2]
    info_df = info_df.dropna()
    info_df["mil_minutes"] = info_df.apply(mil_time, axis=1)

    first_game = info_df["mil_minutes"].min()

    info_df["time_since_start"] = info_df["mil_minutes"] - first_game

    game_sch = info_df[["Team", "time_since_start"]].groupby("Team").max()
    game_sch = (
        game_sch.assign(rank=lambda df: df.rank(method="dense").astype("int"))
        .reset_index()
        .assign(day="Sun")
        .assign(mult=1)
    )
    game_sch = game_sch.assign(Team=lambda x: x["Team"].str.replace("JAX", "JAC"))
    sch = game_sch[["Team", "rank", "day", "mult"]]
    sch.columns = ["team", "rank", "day", "mult"]
    sch.to_csv("Weeks/{}_{}/sch.csv".format(year, week), index=False)
    return game_sch


if __name__ == "__main__":

    week = "1"
    year = "2020"
    sch = game_sch(week, year)
    print(sch)
