"""
@file: create_cutechess_plots
Created on 28.09.2023
@project: CrazyAra
@author: HelpstoneX

creates plots based on the results of different cutechess match configurations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def compare_approaches():
    use960 = False
    prefix_960 = "960_" if use960 else ""
    all_match_info_df = pd.read_csv("all_matches_outcomes_new.csv", index_col=0)
    batch_size = 64
    metric = "nodes"
    matchups = [(f"{prefix_960}correct_phases", f"{prefix_960}no_phases"),
                (f"{prefix_960}movecount2", f"{prefix_960}no_phases"),
                (f"{prefix_960}movecount3", f"{prefix_960}no_phases"),
                (f"{prefix_960}movecount4", f"{prefix_960}no_phases"),
                (f"{prefix_960}movecount5", f"{prefix_960}no_phases")]
                #("specific_endgame", "no_phases")]

    translation_dict = {f"{prefix_960}correct_phases": "Lichess",
                        f"{prefix_960}movecount2": "Move Count 2",
                        f"{prefix_960}movecount3": "Move Count 3",
                        f"{prefix_960}movecount4": "Move Count 4",
                        f"{prefix_960}movecount5": "Move Count 5",
                        f"{prefix_960}correct_opening": "Opening Expert",
                        f"{prefix_960}correct_midgame": "Middlegame Expert",
                        f"{prefix_960}correct_endgame": "Endgame Expert"}
    y_lim = (-430, 165)
    all_match_info_df = all_match_info_df.sort_values(by=["playerA", "bsize", "nodes", "movetime"])

    sns_color_cmap = sns.color_palette("colorblind", as_cmap=True)
    #plt.set_cmap(sns_color_cmap)

    plt.rc('axes', titlesize=15)  # fontsize of the axes title
    plt.rc('axes', labelsize=15)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=12)  # fontsize of the tick labels
    plt.rc('legend', fontsize=12)  # legend fontsize
    plt.rc('figure', titlesize=40)  # fontsize of the figure title
    #N_colors = 7
    #plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.hot(np.linspace(0, 1, N_colors)))

    fig, ax = plt.subplots()
    idx = 0

    for playerA, playerB in matchups:
        # batch sizes by nodes
        matchup_df = all_match_info_df[(all_match_info_df["playerA"] == f"{prefix_960}ClassicAra_{playerA}") &
                                       (all_match_info_df["playerB"] == f"{prefix_960}ClassicAra_{playerB}")]
        nodes_experiments_df = matchup_df[matchup_df[metric] != 0]

        curr_bs_df = nodes_experiments_df[nodes_experiments_df["bsize"] == batch_size]
        plt.plot(curr_bs_df[metric], curr_bs_df["A_elo_diff"], label=translation_dict.get(playerA, playerA),
                 marker=".", color=sns_color_cmap[idx])
        plt.fill_between(x=curr_bs_df[metric], y1=curr_bs_df["A_elo_diff"] + curr_bs_df["A_elo_err"],
                         y2=curr_bs_df["A_elo_diff"] - curr_bs_df["A_elo_err"], alpha=0.2,
                         color=sns_color_cmap[idx])

        idx += 1

    plt.axhline(y=0, color="black", linestyle="-")
    if metric == "nodes":
        plt.xlabel("Number of Nodes")
    elif metric == "movetime":
        plt.xlabel("Movetime [ms]")
    plt.ylabel("Relative Elo")
    plt.ylim(*y_lim)
    #ax.set_xticks(curr_bs_df["nodes"])
    plt.legend(loc="right")
    ax.grid(axis='y')
    #plt.title(f"{playerA} vs {playerB}")

    if metric == "nodes":
        plt.savefig(f'plots/{prefix_960}phase_definition_comparison.pdf', bbox_inches='tight')
    elif metric == "movetime":
        plt.savefig(f'plots/{prefix_960}phase_definition_comparison_movetime.pdf', bbox_inches='tight')

    plt.show()


def visualize_approach_performance():
    all_match_info_df = pd.read_csv("all_matches_outcomes_new.csv", index_col=0)
    batch_sizes = [1, 8, 16, 32, 64]
    use960 = False
    prefix_960 = "960_" if use960 else ""
    matchups = [("correct_phases", "no_phases"),]
                #("specific_opening", "no_phases"),
                #("no_phases", "specific_endgame"),]
                #("specific_endgame", "no_phases")]
    y_lim = (-10, 175)

    all_match_info_df = all_match_info_df.sort_values(by=["playerA", "bsize", "nodes", "movetime"])

    plt.rc('axes', titlesize=15)  # fontsize of the axes title
    plt.rc('axes', labelsize=15)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=12)  # fontsize of the tick labels
    plt.rc('legend', fontsize=12)  # legend fontsize
    plt.rc('figure', titlesize=40)  # fontsize of the figure title
    N_colors = len(batch_sizes) + 1
    plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.hot(np.linspace(0, 1, N_colors)))

    for playerA, playerB in matchups:
        # batch sizes by nodes
        matchup_df = all_match_info_df[(all_match_info_df["playerA"] == f"{prefix_960}ClassicAra_{playerA}") &
                                       (all_match_info_df["playerB"] == f"{prefix_960}ClassicAra_{playerB}")]
        nodes_experiments_df = matchup_df[matchup_df["nodes"] != 0]
        fig, ax = plt.subplots()

        for batch_size in batch_sizes:
            curr_bs_df = nodes_experiments_df[nodes_experiments_df["bsize"] == batch_size]
            plt.plot(curr_bs_df["nodes"], curr_bs_df["A_elo_diff"], label=f"Batch Size: {batch_size}", marker=".")
            plt.fill_between(x=curr_bs_df["nodes"], y1=curr_bs_df["A_elo_diff"] + curr_bs_df["A_elo_err"],
                             y2=curr_bs_df["A_elo_diff"] - curr_bs_df["A_elo_err"], alpha=0.2)
            #curr_bs_df = curr_bs_df[curr_bs_df["stockfish_nodes"] == curr_bs_df["nodes"]]
            #plt.plot(curr_bs_df["nodes"], curr_bs_df["B_elo_diff"], label=f"stockfish with equal nodes", marker=".")
            #plt.fill_between(x=curr_bs_df["nodes"], y1=curr_bs_df["B_elo_diff"] + curr_bs_df["B_elo_err"],
            #                 y2=curr_bs_df["B_elo_diff"] - curr_bs_df["B_elo_err"], alpha=0.2)

        plt.axhline(y=0, color="black", linestyle="-")
        plt.xlabel("Number of Nodes")
        plt.ylabel("Relative Elo")
        plt.ylim(*y_lim)
        #ax.set_xticks(curr_bs_df["nodes"])
        plt.legend(loc="lower right")
        ax.grid(axis='y')
        #plt.title(f"{playerA} vs {playerB}")
        plt.axhline(y=76.24, color="black", linestyle="--")
        plt.savefig(f'plots/{prefix_960}{playerA}_vs_{playerB}.pdf', bbox_inches='tight')
        plt.show()

        # batch sizes by movetime
        movetime_experiments_df = matchup_df[matchup_df["movetime"] != 0]
        fig2, ax2 = plt.subplots()

        for batch_size in batch_sizes:
            curr_movetime_df = movetime_experiments_df[movetime_experiments_df["bsize"] == batch_size]
            plt.plot(curr_movetime_df["movetime"], curr_movetime_df["A_elo_diff"], label=f"Batch Size: {batch_size}", marker=".")
            plt.fill_between(x=curr_movetime_df["movetime"], y1=curr_movetime_df["A_elo_diff"] + curr_movetime_df["A_elo_err"],
                             y2=curr_movetime_df["A_elo_diff"] - curr_movetime_df["A_elo_err"], alpha=0.2)
        plt.axhline(y=0, color="black", linestyle="-")
        plt.xlabel("Movetime [ms]")
        plt.ylabel("Relative Elo")
        plt.ylim(*y_lim)
        plt.legend(loc="lower right")
        ax2.grid(axis='y')
        #plt.title(f"{playerA} vs {playerB}")
        plt.savefig(f'plots/{prefix_960}{playerA}_vs_{playerB}_movetime.pdf', bbox_inches='tight')
        plt.show()

    print(all_match_info_df.head(5))


if __name__ == "__main__":
    #compare_approaches()
    visualize_approach_performance()
