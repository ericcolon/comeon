"""
Created on Wed Nov  1 14:27:52 2017

ToDo:
    Finish it for Version 0.0.5

@author: haenec
"""


import pandas as pd
from comeon_common import connect
from comeon_common import startBetLogging
from comeon_common import placeBet


# load data from the configuration
import yaml
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

stakes = 2
stakes_fix = 5
stakes_value_challenger = 10
stakes_value_wta = 5
stakes_value_atp = 10
stakes_value_gs = 10

margin = 5 #prcent better bet 
margin_btc = 7

proba_fix = 70

bet_on_value = 1.2


con, meta = connect()  


def place_ta_bet(row) :
    l_log = startBetLogging("common")
    if row['winner'] == 'home' :
        winner_name = row['home_player_name']
        winner_odds_id = row['home_odds_id']
        winner_odds = row['home_odds']
        winner_proba = row['home_player_proba']
    else :
        winner_name = row['away_player_name']
        winner_odds_id = row['away_odds_id']        
        winner_odds = row['away_odds']
        winner_proba = row['away_player_proba']

    
    calc_stakes = round(stakes / (winner_odds - 1),1)
    #calc_stakes =  stakes
    
    status = placeBet(winner_odds_id, winner_odds, calc_stakes, product_id=5)
    #status = False
    
    if status :
        l_log.warn("place bet on event '" + str(row['home_player_name']) + " vs " + str(row['away_player_name']) + \
                 "' winner " + str(winner_name) + \
                 " stakes : " + str(calc_stakes) + \
                 " odds : " + str(winner_odds) + \
                 " proba : " + str(winner_proba))
        
    return True


def place_ta_bet_fix(row) :
    l_log = startBetLogging("common")
    if row['winner'] == 'home' :
        winner_name = row['home_player_name']
        winner_odds_id = row['home_odds_id']
        winner_odds = row['home_odds']
        winner_proba = row['home_player_proba']
    else :
        winner_name = row['away_player_name']
        winner_odds_id = row['away_odds_id']        
        winner_odds = row['away_odds']
        winner_proba = row['away_player_proba']

    
    #calc_stakes = round(stakes / (winner_odds - 1),1)
    calc_stakes =  stakes_fix
    
    status = placeBet(winner_odds_id, winner_odds, calc_stakes, product_id=8)
    #status = False
    
    if status :
        l_log.warn("place bet on event '" + str(row['home_player_name']) + " vs " + str(row['away_player_name']) + \
                 "' winner " + str(winner_name) + \
                 " stakes : " + str(calc_stakes) + \
                 " odds : " + str(winner_odds) + \
                 " proba : " + str(winner_proba))
        
    return True


def place_ta_bet_value(row) :
    l_log = startBetLogging("common")
    if row['winner'] == 'home' :
        winner_name = row['home_player_name']
        winner_odds_id = row['home_odds_id']
        winner_odds = row['home_odds']
        winner_proba = row['home_player_proba']
        winner_value = row['home_value']
    else :
        winner_name = row['away_player_name']
        winner_odds_id = row['away_odds_id']        
        winner_odds = row['away_odds']
        winner_proba = row['away_player_proba']
        winner_value = row['away_value']


    
        
    #calc_stakes = round(stakes / (winner_odds - 1),1)
    if 'Challenger' in row['ta_tournament'] :
        calc_stakes =  stakes_value_challenger
        product = 9
    elif 'ATP' in row['ta_tournament'] :
        calc_stakes =  stakes_value_atp
        product = 10     
    elif 'WTA' in row['ta_tournament'] :
        calc_stakes =  stakes_value_wta
        product = 11
    else :
        calc_stakes = stakes_value_gs
        product = 12
        
    
    if product != 11 :
        status = placeBet(winner_odds_id, winner_odds, calc_stakes, product_id=product)
    else :
        status = False
    
    
    if status :
        l_log.warn("place bet on event '" + str(row['home_player_name']) + " vs " + str(row['away_player_name']) + \
                 "' winner " + str(winner_name) + \
                 " stakes : " + str(calc_stakes) + \
                 " odds : " + str(winner_odds) + \
                 " value : " + str(round(winner_value, 2)) + \
                 " proba : " + str(winner_proba))
        
    return True

def place_ta_bet_betbtc(row) :
    l_log = startBetLogging("common")

    if row['winner'] == 'home' :
        winner_name = row['home_player_name']
        winner_odds_id = row['home_odds_id']
        winner_odds = row['home_odds']
        winner_proba = row['home_player_proba']
    else :
        winner_name = row['away_player_name']
        winner_odds_id = row['away_odds_id']        
        winner_odds = row['away_odds']
        winner_proba = row['away_player_proba']

    
    calc_stakes = round(stakes / (winner_odds - 1),1)
    
    status = placeBet(winner_odds_id, winner_odds, calc_stakes, product_id=6)
    #status = False
    
    if status :
        l_log.warn("place bet on event '" + str(row['home_player_name']) + " vs " + str(row['away_player_name']) + \
                 "' winner " + str(winner_name) + \
                 " stakes : " + str(calc_stakes) + \
                 " odds : " + str(winner_odds) + \
                 " proba : " + str(winner_proba))
        
    return True


def ta_proba() :

    sql = """
    SELECT * from v_ta_next_events;
    """

    df_ta_bet_events = pd.read_sql(sql, con)
    
    if df_ta_bet_events.empty :
        return False
    
    df_ta_bet_events['home_odds_proba'] = (1 / df_ta_bet_events['home_odds']) * 100
    df_ta_bet_events['away_odds_proba'] = (1 / df_ta_bet_events['away_odds']) * 100
    
    
    home_winner = df_ta_bet_events[df_ta_bet_events['home_player_proba'] > 50]
    away_winner = df_ta_bet_events[df_ta_bet_events['away_player_proba'] > 50]
       
    good_home_winner = home_winner[home_winner['home_player_proba'] >= (home_winner['home_odds_proba'] + margin) ]
    if not good_home_winner.empty :
        good_home_winner['winner'] = 'home'
    
    good_away_winner = away_winner[away_winner['away_player_proba'] >= (away_winner['away_odds_proba'] + margin) ]
    if not good_away_winner.empty :    
        good_away_winner['winner'] = 'away'
    
    if not (good_home_winner.empty or good_away_winner.empty) :  
        good_winners = pd.concat([good_home_winner, good_away_winner])
    elif not good_home_winner.empty :
        good_winners = good_home_winner
    elif not good_away_winner.empty :
        good_winners = good_away_winner
    else :
        return False
    
    if not good_winners.empty :
       # good_winners.apply(place_ta_bet, axis=1)
        good_winners.apply(place_ta_bet, axis=1)        
        #place_ta_bet_fix
        #good_away_winner.apply(place_ta_bet, axis=1)
        
    return True

def ta_proba_fix() :

    sql = """
    SELECT * from v_ta_next_events_fix;
    """

    df_ta_bet_events = pd.read_sql(sql, con)
    
    if df_ta_bet_events.empty :
        return False
    
    df_ta_bet_events['home_odds_proba'] = (1 / df_ta_bet_events['home_odds']) * 100
    df_ta_bet_events['away_odds_proba'] = (1 / df_ta_bet_events['away_odds']) * 100
    
    
    home_winner = df_ta_bet_events[df_ta_bet_events['home_player_proba'] > proba_fix]
    away_winner = df_ta_bet_events[df_ta_bet_events['away_player_proba'] > proba_fix]
       
    good_home_winner = home_winner[home_winner['home_player_proba'] >= (home_winner['home_odds_proba'] + margin) ]
    if not good_home_winner.empty :
        good_home_winner['winner'] = 'home'
    
    good_away_winner = away_winner[away_winner['away_player_proba'] >= (away_winner['away_odds_proba'] + margin) ]
    if not good_away_winner.empty :    
        good_away_winner['winner'] = 'away'
    
    if not (good_home_winner.empty or good_away_winner.empty) :  
        good_winners = pd.concat([good_home_winner, good_away_winner])
    elif not good_home_winner.empty :
        good_winners = good_home_winner
    elif not good_away_winner.empty :
        good_winners = good_away_winner
    else :
        return False
    
    if not good_winners.empty :
       # good_winners.apply(place_ta_bet, axis=1)
        good_winners.apply(place_ta_bet_fix, axis=1)        
        #place_ta_bet_fix
        #good_away_winner.apply(place_ta_bet, axis=1)
        
    return True


def ta_proba_value() :

    sql = """
    SELECT * from v_ta_next_events_value;
    """

    df_ta_bet_events = pd.read_sql(sql, con)
    
    if df_ta_bet_events.empty :
        return False
    
    df_ta_bet_events['home_value'] = df_ta_bet_events['home_player_proba'] / 100 *  df_ta_bet_events['home_odds']
    df_ta_bet_events['away_value'] = df_ta_bet_events['away_player_proba'] / 100 *  df_ta_bet_events['away_odds']
    
    
    home_winner = df_ta_bet_events[df_ta_bet_events['home_value'] > bet_on_value]
    away_winner = df_ta_bet_events[df_ta_bet_events['away_value'] > bet_on_value]
       
    good_home_winner = home_winner
    if not good_home_winner.empty :
        good_home_winner['winner'] = 'home'
    
    good_away_winner = away_winner
    if not good_away_winner.empty :    
        good_away_winner['winner'] = 'away'
    
    if not (good_home_winner.empty or good_away_winner.empty) :  
        good_winners = pd.concat([good_home_winner, good_away_winner])
    elif not good_home_winner.empty :
        good_winners = good_home_winner
    elif not good_away_winner.empty :
        good_winners = good_away_winner
    else :
        return False
    
    if not good_winners.empty :
        good_winners.apply(place_ta_bet_value, axis=1)
       # good_winners.apply(place_ta_bet_fix, axis=1)        
        #place_ta_bet_fix
        #good_away_winner.apply(place_ta_bet, axis=1)
        
    return True


def ta_proba_btc() :

    sql = """
    SELECT * from v_ta_betbtc_next_events;
    """

    df_ta_bet_events = pd.read_sql(sql, con)
    
    if df_ta_bet_events.empty :
        return False
    
    df_ta_bet_events['home_odds_proba'] = (1 / df_ta_bet_events['home_odds']) * 100
    df_ta_bet_events['away_odds_proba'] = (1 / df_ta_bet_events['away_odds']) * 100
    
    
    home_winner = df_ta_bet_events[df_ta_bet_events['home_player_proba'] > 50]
    away_winner = df_ta_bet_events[df_ta_bet_events['away_player_proba'] > 50]
       
    good_home_winner = home_winner[home_winner['home_player_proba'] >= (home_winner['home_odds_proba'] + margin_btc) ]
    if not good_home_winner.empty :
        good_home_winner['winner'] = 'home'
    
    good_away_winner = away_winner[away_winner['away_player_proba'] >= (away_winner['away_odds_proba'] + margin_btc) ]
    if not good_away_winner.empty :    
        good_away_winner['winner'] = 'away'
    
    if not (good_home_winner.empty or good_away_winner.empty) :  
        good_winners = pd.concat([good_home_winner, good_away_winner])
    elif not good_home_winner.empty :
        good_winners = good_home_winner
    elif not good_away_winner.empty :
        good_winners = good_away_winner
    else :
        return False
    
    if not good_winners.empty :
        good_winners.apply(place_ta_bet_betbtc, axis=1)
        #good_away_winner.apply(place_ta_bet, axis=1)
        
    return True