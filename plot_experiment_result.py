from shutil import move
import matplotlib.pyplot as plt
import json
import numpy as np
from ast import literal_eval
import os
from os.path import join

def create_experiment_imgs(experiment_path, experiment_name):
    newPath = join('images', experiment_name)

    if not os.path.exists(newPath):
            os.makedirs(newPath+'/PlayImg')
            os.makedirs(newPath+'/TimeImg')

    full_experiment_path = join(experiment_path,experiment_name)
    for matchn in os.listdir(full_experiment_path):
        name = join(full_experiment_path,matchn)

        file_json = open(name)
        data = json.load(file_json)

        vec_x = np.array([])
        vec_y = np.array([])
        vec_color = np.array([])

        winner = data["winner"]

        moves = ()
        number_moves=0
        for move in data["moves"]:
            moves = moves +(move,)
            number_moves = number_moves+1

        for k in range(number_moves):
            x = moves[k][0]
            vec_x = np.append(vec_x, x)
            y = moves[k][1]
            vec_y = np.append(vec_y, y)
            color = moves[k][2]
            vec_color= np.append(vec_color, color)

        annotations =np.arange(1,np.size(vec_x)+1)
        sizes = np.random.uniform(400, 400)
        color = np.array([])
        color_text = np.array([])

        plt.rcParams['axes.facecolor'] = '#EEDFCC'
        fig, ax = plt.subplots(1, figsize=(6, 5))
        for i in vec_color:
            if i== 1.0:
                color = np.append(color, "black")
            if i== 0.0:
                color = np.append(color, "white")

        ax.scatter(vec_x, vec_y, s=sizes, c=color, vmin=0, vmax=100)
        ax.set(xlim=(-1, 15), xticks=np.arange(0, 15),
            ylim=(15,-1), yticks=np.arange(0, 15))
        ax.grid(b=True, which='major', color="white", linestyle='-', alpha=0.4)

        for i, label in enumerate(annotations):
            if color[i] == 'black':
                color_text = np.append(color_text, "white")
            else:
                color_text = np.append(color_text, "black")

            ax.annotate(label,
                                xy=(vec_x[i], vec_y[i]),
                                xytext=(vec_x[i]-0.25, vec_y[i]+0.2),
                                color= color_text[i],
                                size = 11
                                )

        plt.suptitle("Gomoku Play Example", fontsize = 12)
        plt.title("Winner: "+winner +" player", fontsize=10)
        plt.xlabel("row")
        plt.ylabel("column")

        play_img = matchn+'_PlayImg.png'
        fig.savefig(join(newPath, 'PlayImg', play_img))

        #Time Graph
        time_bl = np.array([])
        time_wh = np.array([])
        tup = ()
        count=0
        for move in data["move_data"]:
            temp = tuple(literal_eval(move))
            tup = tup +(temp,)
            count = count+1

        fig = plt.figure(figsize=(6, 5))
        for i in range(count):
            if tup[i][2] == True:
                time_black = data["move_data"][str(tup[i])]["time"]
                time_bl = np.append(time_bl, time_black)
            else:
                time_white = data["move_data"][str(tup[i])]["time"]
                time_wh = np.append(time_wh, time_white)

        stop = np.size(time_wh)
        time_wh =time_wh[1:stop]
        ax_x_bl = np.arange(1, np.size(time_bl)+1)
        ax_x_wh = np.arange(1, np.size(time_wh)+1)

        plt.plot(ax_x_bl,time_bl, color='black', marker='o', linestyle='dashed',
            linewidth=2, markersize=8)


        plt.plot(ax_x_wh,time_wh, color='white', marker='o', linestyle='dashed',
            linewidth=2, markersize=8)

        plt.grid()
        plt.suptitle("Time taken by the player to place a stone", fontsize=12)
        plt.title("Winner: "+winner +" player", fontsize=10)
        plt.ylabel("Time")
        plt.xlabel("#move")


        img = matchn+'_TimeImg.png'
        fig.savefig(join(newPath,'TimeImg',img))
        plt.close('all')

def create_winner_graph(experiment_path, experiment_name):
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    newPath = join('images', experiment_name)

    if not os.path.exists(newPath):
            os.makedirs(newPath+'/PlayImg')
            os.makedirs(newPath+'/TimeImg')

    full_experiment_path = join(experiment_path,experiment_name)

    experiment_data = {}
    match_list = os.listdir(full_experiment_path)
    match_types_set = set([' '.join(mname.split('_')[1:5]) for mname in match_list])

    for match_type in match_types_set:
        match_names = [mname for mname in match_list if ' '.join(mname.split('_')[1:5]).lower() == match_type.lower()]
        bwins = 0
        wwins = 0
        draws = 0

        moves_stats = {
            'black' : [],
            'white' : []
        }
        for mname in match_names:
            with open(os.path.join(full_experiment_path,mname),'r') as mjson:
                mdata = json.load(mjson)
                experiment_data[mname] = mdata
                win = mdata['winner'].lower()
                nmoves = len(mdata['moves'])
                if win == 'black':
                    moves_stats['black'].append(nmoves)
                    bwins += 1
                elif win == 'white':
                    moves_stats['white'].append(nmoves)
                    wwins += 1
                elif win == 'draw':
                    draws += 1

        #WIN COUNTS
        fig, ax = plt.subplots()

        bar_labels = ('Black', 'White', 'Draw')
        y_pos = np.arange(len(bar_labels))

        win_data = [bwins,wwins,draws]
        bars = ax.barh(y_pos, win_data, align='center',color = [(0.9,0.5,0.1),(0.1,0.1,0.9),(0.5,0,0.5)])
        ax.set_yticks(y_pos, labels=bar_labels)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Wins')
        ax.set_title(f"{' '.join(experiment_name.split('-')).upper()} Win Statistics")

        ax.bar_label(bars,win_data)

        fig.savefig(os.path.join(newPath,f"{experiment_name}_{match_type.replace(' ', '')}_WinStats.png"))

        #NUMBER OF MOVES TO WIN
        fig, ax = plt.subplots(figsize=(6, 6), sharey=True)
        move_data = [moves_stats['black'],moves_stats['white']]
        bp = ax.boxplot(move_data, labels=['Black','White'], showfliers=False, patch_artist=True)    

        #Purple and Blue
        colors = [(176 / 255, 51 / 255, 170 / 255, 1),(44 / 255, 72 / 255, 184 / 255, 1)]
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        plt.setp(bp['medians'], color='Cyan')
        ax.set_title(f"{' '.join(experiment_name.split('-')).upper()} Number of Moves to Win")

        fig.subplots_adjust(hspace=0.4)
        fig.savefig(os.path.join(newPath,f"{experiment_name}_{match_type.replace(' ', '')}_NMoves.png"))


    player_types = [mtype.split(' ')[0] for mtype in match_types_set]
    player_types.extend([mtype.split(' ')[2] for mtype in match_types_set])
    player_types = list(set(player_types))
    player_types.sort()
    black_wins = {ptype : 0 for ptype in player_types}
    white_wins = {ptype : 0 for ptype in player_types}        

    for mdata in experiment_data.values():
        winner_color = mdata['winner']
        player_colors = mdata['swap2_data']['select_color']
        ptype = player_colors[winner_color].split('_')[0]
        if winner_color == 'black':
            black_wins[ptype] += 1
        elif winner_color == 'white':
            white_wins[ptype] += 1


    x = np.arange(len(player_types))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, [black_wins[ptype] for ptype in player_types], width, label='Black Wins')
    rects2 = ax.bar(x + width/2, [white_wins[ptype] for ptype in player_types], width, label='White Wins')

    # Add some text for labels, title and custom x-axis tick labels, etc.        
    ax.set_title(f"{' '.join(experiment_name.split('-')).upper()} Player Wins")
    ax.set_xticks(x, player_types)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    fig.savefig(os.path.join(newPath,f"{experiment_name}_PWins.png"))

    plt.close('all')      


def create_search_data_graph(experiment_path, experiment_name):
    newPath = join('images', experiment_name)
    full_experiment_path = join(experiment_path,experiment_name)

    match_list = os.listdir(full_experiment_path)
    match_types_set = set([' '.join(mname.split('_')[1:5]) for mname in match_list])
    search_data = {
        'branching' : [],
        'visited' : []
    }
    for match_type in match_types_set:
        match_names = [mname for mname in match_list if ' '.join(mname.split('_')[1:5]).lower() == match_type.lower()]
        for mname in match_names:
            with open(os.path.join(full_experiment_path,mname),'r') as mjson:
                match_data = json.load(mjson)
            search_data['branching'].extend([mdata['search_data']['branching']
            for mdata in match_data['move_data'].values()
            if 'search_data' in mdata
            ])
            search_data['visited'].extend([mdata['search_data']['visited']
            for mdata in match_data['move_data'].values()
            if 'search_data' in mdata
            ])

        #NUMBER OF MOVES TO WIN
        fig, ax = plt.subplots(figsize=(6, 6), sharey=True)
        sdata = [search_data['branching'],search_data['visited']]
        bp = ax.boxplot(sdata, labels=['Branching Factor','Visited Nodes'], showfliers=False, patch_artist=True)

        #Red and Green
        colors = [(235 / 255, 64 / 255, 52 / 255,1.0),(93 / 255, 199 / 255, 58 / 255, 1.0)]
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        plt.setp(bp['medians'], color='black')

        ax.set_title(f"{experiment_name.replace('-',' ').upper()} Minimax Search Data")

        fig.subplots_adjust(hspace=0.4)
        fig.savefig(os.path.join(newPath,f"{experiment_name}_{match_type.replace(' ', '')}_SearchData.png"))
        plt.close('all')

if __name__ == '__main__':
    experiment_path = 'experiments'
    experiment_name = 'experiment-v1-vs-v2'
    SMALL_SIZE = 10
    MEDIUM_SIZE = 14

    plt.rc('axes', labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=MEDIUM_SIZE)
    plt.rc('ytick', labelsize=MEDIUM_SIZE)

    create_experiment_imgs(experiment_path,experiment_name)
    create_winner_graph(experiment_path,experiment_name)
    create_search_data_graph(experiment_path,experiment_name)
