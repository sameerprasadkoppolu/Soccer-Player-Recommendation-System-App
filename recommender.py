import pandas as pd
import io
import warnings
import numpy as np
from math import sqrt
import operator
from mplsoccer import Radar, FontManager, grid
import matplotlib.pyplot as plt
import streamlit as st
import requests


df = pd.read_csv("https://raw.githubusercontent.com/sameerprasadkoppolu/Soccer-Player-Recommendation-System/master/df.csv")

final_df = pd.read_csv("https://raw.githubusercontent.com/sameerprasadkoppolu/Soccer-Player-Recommendation-System/master/final_df.csv")

#distance_matrix_dict = np.load('distance_matrix_dict.npy', allow_pickle=True)
response = requests.get("https://github.com/sameerprasadkoppolu/Soccer-Player-Recommendation-System/blob/975de266647a36208a3ea541feca1b31d15c7d1e/distance_matrix_dict.npy?raw=true")
distance_matrix_dict = np.load(io.BytesIO(response.content), allow_pickle=True) 



#Function to Find Top 10 Players
def top_ten(p):

  player_index = final_df.loc[final_df['Player + Squad'] == p].index[0]
  player_pos = final_df.loc[player_index, 'Pos'].split(',')
  player_cluster = final_df.loc[player_index, 'Cluster']

  X = final_df.loc[final_df['Cluster'] == player_cluster].reset_index()
  X.drop(columns = ['index'], inplace = True)

  player_index = X.loc[X['Player + Squad'] == p].index[0]

  X1 = X.iloc[:, 6:-2]

  #distance_matrix = distance_matrix_dict[player_cluster]
  distance_matrix = distance_matrix_dict.item().get(player_cluster)

  cluster_indices = distance_matrix.shape[0]

  players_dict = {}

  for i in range(cluster_indices):
    key = X.loc[i, 'Player + Squad']
    value = distance_matrix[player_index, i]
    players_dict[key] = value


  sorted_players_dict = sorted(players_dict.items(), key=operator.itemgetter(1))

  top_ten_players = []

  for i in sorted_players_dict[1:11]:
    top_ten_players.append(i[0])


  return top_ten_players


#Function to Plot Top 10 Players
def plot_top_10(p):
  figure_list = []

  X  = df.copy()

  X['Non-PK Goals'] = X['Gls'] - X['PK']
  X['npxG+xAG'] = X['npxG_Expected'] + X['xAG_Expected']
  X['Pass Completion %'] = 100 * X['Cmp_Total'] / X['Att_Total']
  X['Blk'] = X['Sh_Blocks'] + X['Pass_Blocks']
  X.rename(columns = {'PrgC_Progression': 'PrgC', 'PrgP_Progression': 'PrgP', 'PrgR_Progression': 'PrgR', 'Tkl_Tackles':'Tkl', 'npxG_Expected':'npxG', 'xAG_Expected':'xAG', 'SCA_SCA':'SCA', 'Att_Total':'Passes Attempted'},
           inplace = True)

  params = ['Non-PK Goals', 'npxG', 'Sh_Standard', 'Ast', 'xAG', 'npxG+xAG', 'SCA', 'Passes Attempted', 'Pass Completion %', 'PrgC', 'PrgP', 'Succ_Take', 'Att Pen_Touches', 'PrgR','Int', 'Clr', 'Tkl', 'Blk', 'Won_Aerial']

  l = top_ten(p)
  low = []
  high = []

  for i in params:
    low.append(round(X[i].describe()[1], 2))
    high.append(round(X[i].describe()[-1], 2))

  lower_is_better = []

  radar = Radar(params, low, high, lower_is_better=lower_is_better, round_int=[False]*len(params), num_rings=4, ring_width=1, center_circle_radius=1)

  URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
  robotto_thin = FontManager(URL4)

  URL5 = ('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
        'RobotoSlab%5Bwght%5D.ttf')
  robotto_bold = FontManager(URL5)

  gen_plots = []

  for j in l:
    player = list(X.loc[X['Player + Squad'] == p, params].values[0])
    suggestion = list(X.loc[X['Player + Squad'] == j, params].values[0])

    fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                title_space=0, endnote_space=0, grid_key='radar', axis=False)

    radar.setup_axis(ax=axs['radar'])  # format axis as a radar
    rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#FFD700', edgecolor='#fc5f5f')
    radar_output = radar.draw_radar_compare(player, suggestion, ax=axs['radar'], kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6}, kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})

    radar_poly, radar_poly2, vertices1, vertices2 = radar_output

    range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=10, fontproperties=robotto_thin.prop)
    param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=15, fontproperties=robotto_thin.prop)

    lines = radar.spoke(ax=axs['radar'], color='#a6a4a1', linestyle='--', zorder=2)

    axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1], c='#00f2c1', edgecolors='#6d6c6d', marker='.', s=150, zorder=2)
    axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1], c='#d80499', edgecolors='#6d6c6d', marker='.', s=150, zorder=2)

    title1_text = axs['title'].text(0.01, 0.65, p, fontsize=15, color='#01c49d', fontproperties=robotto_bold.prop, ha='left', va='center')
    title3_text = axs['title'].text(0.99, 0.65, j, fontsize=15, fontproperties=robotto_bold.prop, ha='right', va='center', color='#d80499')

    #fig.show()
    #st.pyplot(fig)
    figure_list.append(fig)
  
  return figure_list


st.write("""
# Soccer Player Recommendation System

This Application Recommends the Top-10 Most Similar Players for a Given Player
""")

st.write("The Player Information and Stats are from the EPL, La Liga, Bundesliga, Ligue 1, Serie A, Eredivisie, and Liga Portugal taken at the end of the 2022-23 Season")


option = st.selectbox('Select a Player', df['Player + Squad'])

st.write('You selected:', option)

st.subheader("The Top 10 Most Similar Players are: ")

if "counter" not in st.session_state:
        st.session_state.counter = 0
st.write(st.session_state)

if option != None:
    fig_list = plot_top_10(option)

    col1, col2, col3 = st.columns([0.25, 0.659, 0.099])

    if "counter" not in st.session_state:
        st.session_state.counter = 0

    st.pyplot(fig_list[st.session_state.counter])
    title = "\t\t\tPlayer Recommendation: "+ str(st.session_state.counter+1)
    col2.subheader(title)

    if col1.button("Back"):
        st.session_state.counter -= 1
    
    if st.session_state.counter < 0:
        st.session_state.counter = len(fig_list) - 1

    if col3.button("Next"):
        st.session_state.counter += 1
    
    if st.session_state.counter >= len(fig_list):
        st.session_state.counter = 0

#Scrollable Bar for Description of Metric Names
metrics_desc = pd.DataFrame({"Name": ['Non-PK Goals', 'npxG', 'Sh_Standard', 'Ast', 'xAG', 'npxG+xAG', 'SCA', 'PrgC', 'PrgP', 'Succ_Take', 'Att Pen_Touches', 'PrgR','Int', 'Clr', 'Tkl', 'Blk', 'Won_Aerial'], 
                             "Description": ['Non-Penalty Goals', 'Non-Penalty Expected Goals', 'No. of Shots Taken (Excluding Penalty Kicks)', 'Assists', 'Expected Assisted Goals', 'Non-Penalty Expected Goals + Expected Assisted Goals',
                                            'Shot Creating Actions', 'Progressive Carries', 'Progressive Passes Completed', 'Successful Take-Ons', 'Touches in the Attacking Penalty Area',
                                            'Progressive Passes Received', 'Interceptions', 'Clearances', 'Tackles', 'Blocks', 'Number of Aerial Duels Won']})

st.write("Description of Fields in Radar Plot")

st.dataframe(metrics_desc)
