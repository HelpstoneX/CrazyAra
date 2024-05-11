"""
@file: analyse_game_phase_definition
Created on 15.12.2023
@project: CrazyAra
@author: HelpstoneX

Use game_phase_detector, analyse the resulting game phase samples and create plots showing phase distributions,
sample counts, jumps to previous phases and more.
"""

import chess
import chess.pgn
import numpy as np
import matplotlib.pyplot as plt
import io
from DeepCrazyhouse.configs.main_config import main_config
import os
from DeepCrazyhouse.src.preprocessing.game_phase_detector import get_game_phase
import math
import seaborn as sns

if __name__ == "__main__":
    print(get_game_phase(chess.Board()))

    #pgn = open("download_pgns/lichess_db_standard_rated_2013-01.pgn", encoding="utf-8-sig")

    use960 = False
    dataset = "test"
    save_figs = True
    prefix = "plots/960_" if use960 else "plots/"

    import_dir = f"C:/workspace/Python/CrazyAra/data/chess960_pgns/pgn/{dataset}/" if use960 else f"C:/workspace/Python/CrazyAra/data/kingbase2019_lite_pgn_months/pgn/{dataset}/"
    pgn_filenames = os.listdir(import_dir)

    pgn = open(import_dir + pgn_filenames[0], "r")
    #pgn = io.StringIO("1. e4 Nc6 2. Nf3 e5 3. Bb5 a6 4. Ba4 b5 { C70 Ruy Lopez: Morphy Defense, Caro Variation } 5. Bb3 d6 6. O-O Nh6 7. d4 g6 8. d5 Nb4 9. a3 Nxc2 10. Qxc2 Ng4 11. h3 Nf6 12. Nc3 h5 13. Bg5 Bh6 14. Bxh6 Rxh6 15. Qd2 c5 16. Qxh6 c4 17. Bc2 Ke7 18. b3 cxb3 19. Bxb3 Rb8 20. Qg5 b4 21. Ne2 a5 22. Ba4 Ba6 23. Rfe1 Rc8 24. Bc6 Bd3 25. axb4 Bxe4 26. bxa5 Bd3 27. Ned4 Rxc6 28. dxc6 Kf8 29. Qh6+ Kg8 30. a6 exd4 31. Nxd4 Ne4 32. a7 Qa8 33. c7 Nxf2 34. Kxf2 f5 35. Qxg6+ Kh8 36. c8=Q+ Qxc8 37. a8=Q Qxa8 38. Rxa8# { White wins. } 1-0")

    stats_by_move_idx = dict()
    games_parsed = 0
    moves_parsed = 0
    midgame_start_moves = list()
    endgame_start_moves = list()
    midgame_start_moves_games = list()
    endgame_start_moves_games = list()

    phase_to_phase_id = {"opening": 0, "midgame": 1, "endgame": 2}
    mid_to_open_per_game = list()
    end_to_mid_per_game = list()
    end_to_open_per_game = list()
    all_prev_switch_per_game = list()
    game_movecounts = list()

    while True:
        curr_game = chess.pgn.read_game(pgn)
        if curr_game is None or games_parsed > 1000:
            break
        if curr_game.__str__().find(f"5. ") != -1:  # if game is at least 5 moves long
            games_parsed += 1
            if games_parsed % 100 == 0:
                print(games_parsed)

            if curr_game.headers.get("FEN", "?") == "?":  # to fix lichess using "?" as FEN for the default position
                curr_game.headers["FEN"] = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

            curr_board = curr_game.board()
            midgame_started = False
            endgame_started = False

            curr_phase = "opening"
            mid_to_open_counter = 0
            end_to_mid_counter = 0
            end_to_open_counter = 0
            all_prev_switch_counter = 0
            curr_game_moves = 0

            for idx, move in enumerate(curr_game.main_line()):
                assert math.floor(0.5*curr_game_moves) == (curr_board.fullmove_number - 1)
                phase, num_maj_and_min, backrank_sparse, mix_score, _ = get_game_phase(curr_board, phase_definition="lichess")
                #print(get_game_phase(curr_board), move)

                if curr_phase == "midgame" and phase == "opening":
                    mid_to_open_counter += 1
                    all_prev_switch_counter += 1

                if curr_phase == "endgame" and phase == "midgame":
                    end_to_mid_counter += 1
                    all_prev_switch_counter += 1

                if curr_phase == "endgame" and phase == "opening":
                    end_to_open_counter += 1
                    all_prev_switch_counter += 1

                if not midgame_started and phase == "midgame":
                    midgame_started = True
                    midgame_start_moves.append(idx)
                    midgame_start_moves_games.append(curr_game.__str__())

                if not endgame_started and phase == "endgame":
                    endgame_started = True
                    endgame_start_moves.append(idx)
                    endgame_start_moves_games.append(curr_game.__str__())

                if idx not in stats_by_move_idx:
                    stats_by_move_idx[idx] = [[phase_to_phase_id[phase], num_maj_and_min, int(backrank_sparse),
                                               mix_score, int(num_maj_and_min <= 10), int(mix_score > 150)]]
                else:
                    stats_by_move_idx[idx].append([phase_to_phase_id[phase], num_maj_and_min, int(backrank_sparse),
                                                   mix_score, int(num_maj_and_min <= 10), int(mix_score > 150)])
                curr_board.push(move)
                moves_parsed += 1
                curr_phase = phase
                curr_game_moves += 1

            mid_to_open_per_game.append((mid_to_open_counter, curr_game.__str__()))
            end_to_mid_per_game.append((end_to_mid_counter, curr_game.__str__()))
            end_to_open_per_game.append((end_to_open_counter, curr_game.__str__()))
            all_prev_switch_per_game.append((all_prev_switch_counter, curr_game.__str__()))
            game_movecounts.append(curr_game_moves)
        else:
            print(curr_game.__str__())

    plt.rc('axes', titlesize=15)  # fontsize of the axes title
    plt.rc('axes', labelsize=15)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=12)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=12)  # fontsize of the tick labels
    plt.rc('legend', fontsize=12)  # legend fontsize
    plt.rc('figure', titlesize=40)  # fontsize of the figure title

    all_trans_list = [x for x, _ in all_prev_switch_per_game]
    print("average count any jump", np.mean(all_trans_list))
    print("max of any jump", max(all_trans_list))
    print(all_prev_switch_per_game[np.argmax(all_trans_list)][1])

    labels, counts = np.unique(all_trans_list, return_counts=True)
    percentages = [round(count*100/sum(counts), 2) for count in counts]
    graph = plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    plt.xlabel("Jumps to previous phase")
    plt.ylabel("Games")

    i = 0
    for p in graph:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        plt.text(x + width / 2,
                 y + height * 1.01,
                 str(percentages[i]) + '%',
                 ha='center',
                 weight='bold')
        i += 1

    if save_figs:
        plt.savefig(f'{prefix}prev_phase_jumps.pdf', bbox_inches='tight')
    plt.show()

    mid_trans_list = [x for x, _ in mid_to_open_per_game]
    print("average count of mid to open", np.mean(mid_trans_list))
    print("max of mid to open", max(mid_trans_list))
    print(mid_to_open_per_game[np.argmax(mid_trans_list)][1])

    end_mid_trans_list = [x for x, _ in end_to_mid_per_game]
    print("average count of end to mid", np.mean(end_mid_trans_list))
    print("max of end to mid", max(end_mid_trans_list))
    print(end_to_mid_per_game[np.argmax(end_mid_trans_list)][1])

    all_trans_list_bool = [1 if x > 0 else 0 for x, _ in all_prev_switch_per_game]
    print("chance of any jump", np.mean(all_trans_list_bool))

    mid_trans_list_bool = [1 if x > 0 else 0 for x, _ in mid_to_open_per_game]
    print("chance of mid to open", np.mean(mid_trans_list_bool))

    end_trans_list_bool = [1 if x > 0 else 0 for x, _ in end_to_mid_per_game]
    print("chance of end to mid", np.mean(end_trans_list_bool))

    num_maj_and_min_data = list()
    mix_score_data = list()
    backrank_sparses_data = list()  #  list of mean backrank sparseness for each move
    num_samples_data = list()
    opening_moves = list() # move indices of opening moves
    midgame_moves = list()
    endgame_moves = list()

    num_opening_moves = 0
    num_midgame_moves = 0
    num_endgame_moves = 0

    positions_by_movecount = list()

    for move_idx, stats in stats_by_move_idx.items():
        stats_array = np.array(stats)
        game_phases = list(stats_array[:, 0])
        backrank_sparses = stats_array[:, 2]

        num_opening_moves += game_phases.count(0)
        num_midgame_moves += game_phases.count(1)
        num_endgame_moves += game_phases.count(2)

        if 0 < move_idx < 100:
            opening_moves += game_phases.count(0)*[move_idx/2]
            midgame_moves += game_phases.count(1)*[move_idx/2]
            endgame_moves += game_phases.count(2)*[move_idx/2]
            backrank_sparses_data.append(np.mean(backrank_sparses))
            positions_by_movecount += len(game_phases)*[move_idx/2]

        if 0 < move_idx < 120 and move_idx % 10 == 0:

            num_maj_and_mins = stats_array[:, 1]
            mix_scores = stats_array[:, 3]
            middle_piece_conds = stats_array[:, 4]
            mix_conds = stats_array[:, 5]
            samples = len(num_maj_and_mins)

            num_maj_and_min_data.append(num_maj_and_mins)
            mix_score_data.append(mix_scores)
            num_samples_data.append(samples)

    bins = np.linspace(0, 50, 100)
    plt.hist(positions_by_movecount, bins)
    plt.ylabel("Positions")
    plt.xlabel("Move")
    #plt.title("game phase distribution")
    if save_figs:
        plt.savefig(f'{prefix}positions_by_move_ungrouped.pdf', bbox_inches='tight')
    plt.show()

    plt.boxplot(num_maj_and_min_data)
    plt.xticks(list(range(1, len(num_maj_and_min_data)+1)), [5*x for x in range(1, len(num_maj_and_min_data)+1)])
    #plt.title("Major and minor pieces left")
    plt.ylabel("Major and minor pieces left")
    plt.xlabel("Move")
    if save_figs:
        plt.savefig(f'{prefix}maj_min_pieces.pdf', bbox_inches='tight')
    plt.show()

    plt.plot(np.array(list(range(len(backrank_sparses_data))))/2, backrank_sparses_data)
    #plt.title()
    plt.ylabel("Chance of backrank sparseness")
    plt.xlabel("Move")
    if save_figs:
        plt.savefig(f'{prefix}backrank.pdf', bbox_inches='tight')
    plt.show()

    plt.boxplot(mix_score_data)
    plt.xticks(list(range(1, len(mix_score_data)+1)), [5*x for x in range(1, len(mix_score_data)+1)])
    #plt.title("Board mixedness")
    plt.ylabel("Mixedness")
    plt.xlabel("Move")
    if save_figs:
        plt.savefig(f'{prefix}mixedness.pdf', bbox_inches='tight')
    plt.show()

    graph = plt.bar(list(range(len(num_samples_data))), np.array(num_samples_data))
    percentages = [round(count*100/sum(np.array(num_samples_data)), 2) for count in np.array(num_samples_data)]
    i = 0
    for p in graph:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        plt.text(x + width / 2,
                 y + height * 1.01,
                 str(percentages[i]) + '%',
                 ha='center',
                 weight='bold',
                 fontsize=7)
        i += 1

    plt.xticks(list(range(len(num_samples_data))), [5*x for x in range(len(num_samples_data))])
    #plt.title("num_samples")
    plt.ylabel("Positions")
    plt.xlabel("Move")
    if save_figs:
        plt.savefig(f'{prefix}positions_by_movecount.pdf', bbox_inches='tight')
    plt.show()

    bins = np.linspace(0, 50, 100)
    sns_color_cmap = sns.color_palette("colorblind", as_cmap=True)
    plt.hist(opening_moves, bins, alpha=0.5, label="Opening", color=sns_color_cmap[0])
    plt.hist(midgame_moves, bins, alpha=0.5, label="Middlegame", color=sns_color_cmap[1])
    plt.hist(endgame_moves, bins, alpha=0.5, label="Endgame", color=sns_color_cmap[2])
    plt.ylabel("Positions")
    plt.xlabel("Move")
    #plt.title("game phase distribution")
    plt.legend()
    plt.axvline(np.mean(midgame_start_moves)/2, 0, 1, color="black")
    plt.axvline(np.mean(endgame_start_moves)/2, 0, 1, color="black")
    if save_figs:
        plt.savefig(f'{prefix}game_phase_distribution.pdf', bbox_inches='tight')
    plt.show()

    plt.hist([opening_moves, midgame_moves, endgame_moves], bins, stacked=True, density=False, alpha=0.5, label=['opening', 'midgame', 'endgame'])
    plt.ylabel("Positions")
    plt.xlabel("Move")
    plt.legend()
    plt.axvline(np.mean(midgame_start_moves)/2, 0, 1, color="black")
    plt.axvline(np.mean(endgame_start_moves)/2, 0, 1, color="black")
    if save_figs:
        plt.savefig(f'{prefix}positions_stacked.pdf', bbox_inches='tight')
    plt.show()

    bins = np.linspace(0, 50, 50)
    plt.hist(np.array(midgame_start_moves)/2, bins, alpha=0.5, label="midgame start")
    plt.hist(np.array(endgame_start_moves)/2, bins, alpha=0.5, label="endgame start")
    plt.xlabel("Move")
    plt.ylabel("Games")
    #plt.title("game phase start distribution")
    plt.legend()
    plt.axvline(np.mean(midgame_start_moves)/2, 0, 1, color="black")
    plt.axvline(np.mean(endgame_start_moves)/2, 0, 1, color="black")
    if save_figs:
        plt.savefig(f'{prefix}phase_start_distribution.pdf', bbox_inches='tight')
    plt.show()

    print("mean midgame start:", np.mean(np.array(midgame_start_moves)) / 2)
    print("std midgame start:", np.std(np.array(midgame_start_moves)/2))
    print("min midgame start", min(midgame_start_moves)/2)
    print("max midgames start", max(midgame_start_moves) / 2)
    print("mean endgame start:", np.mean(np.array(endgame_start_moves)) / 2)
    print("std endgame start:", np.std(np.array(endgame_start_moves)/2))
    print("min endgame start", min(endgame_start_moves)/2)
    print("max endgame start", max(endgame_start_moves) / 2)

    print("earliest midgame start game", midgame_start_moves_games[np.argmin(midgame_start_moves)])
    print("latest midgame start game", midgame_start_moves_games[np.argmax(midgame_start_moves)])

    print("earliest endgame start game", endgame_start_moves_games[np.argmin(endgame_start_moves)])
    print("latest endgame start game", endgame_start_moves_games[np.argmax(endgame_start_moves)])

    labels = ["opening_positions", "midgame_positions", "endgame_positions"]
    counts = [num_opening_moves, num_midgame_moves, num_endgame_moves]
    percentages = [round(count*100/sum(counts), 2) for count in counts]
    graph = plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    plt.title("game phase position counts")
    plt.ylabel("Positions")

    i = 0
    for p in graph:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        plt.text(x + width / 2,
                 y + height * 1.01,
                 str(percentages[i]) + '%',
                 ha='center',
                 weight='bold')
        i += 1
    if save_figs:
        plt.savefig(f'{prefix}game_phase_position_counts.pdf', bbox_inches='tight')
    plt.show()

    print("end")
