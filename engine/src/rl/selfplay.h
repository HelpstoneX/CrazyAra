/*
  CrazyAra, a deep learning chess variant engine
  Copyright (C) 2018  Johannes Czech, Moritz Willig, Alena Beyer
  Copyright (C) 2019  Johannes Czech

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

/*
 * @file: selfplay.h
 * Created on 16.09.2019
 * @author: queensgambit
 *
 * Functionality for running CrazyAra in self play mode
 */

#ifndef SELFPLAY_H
#define SELFPLAY_H

#include "../agents/mctsagent.h"
#include "../agents/rawnetagent.h"
#include "gamepgn.h"
#include "../manager/statesmanager.h"
#include "tournamentresult.h"


#ifdef USE_RL
class SelfPlay
{
private:
    RawNetAgent* rawAgent;
    MCTSAgent* mctsAgent;
    PlaySettings* playSettings;
    GamePGN gamePGN;
    TrainDataExporter* exporter;
    string filenamePGNSelfplay;
    string filenamePGNArena;
    string fileNameGameIdx;
    size_t gameIdx;
    float gamesPerMin;
    float samplesPerMin;

    /**
     * @brief generate_game Generates a new game in self play mode
     * @param variant Current chess variant
     * @param searchLimits Search limits struct
     * @param states States manager for maintaining the states objects. Used for 3-fold repetition check.
     * @param policySharpening Threshold which is applied after move selection before exporting the policy to undo dirichlet noise
     */
    void generate_game(Variant variant, SearchLimits& searchLimits, StatesManager* states, float policySharpening, bool verbose);

    /**
     * @brief generate_arena_game Generates a game of the current NN weights vs the new acquired weights
     * @param whitePlayer MCTSAgent which will play with the white pieces
     * @param blackPlayer MCTSAgent which will play with the black pieces
     * @param variant Current chess variant
     * @param searchLimits Search limits struct
     */
    Result generate_arena_game(MCTSAgent *whitePlayer, MCTSAgent *blackPlayer, Variant variant, SearchLimits& searchLimits, StatesManager* states);

    /**
     * @brief write_game_to_pgn Writes the game log to a pgn file
     * @param pngFileName Filename to export
     * @param verbose If true, game will also be printed to stdout
     */
    void write_game_to_pgn(const std::string& pngFileName, bool verbose);

    /**
     * @brief set_game_result Sets the game result to the gamePGN object
     * @param terminalNode Terminal node of the game
     */
    void set_game_result_to_pgn(const Node* terminalNode);

    /**
     * @brief reset_speed_statistics Resets the interal measurements for gameIdx, gamesPerMin and samplesPerMin
     */
    void reset_speed_statistics();

    /**
     * @brief speed_statistic_report Updates the speed statistics and prints a summary to std-out
     */
    void speed_statistic_report(float elapsedTimeMin, int generatedSamples);

    /**
     * @brief export_number_generated_games Creates a file which describes how many games have been generated in the newly created .zip-file
     */
    void export_number_generated_games() const;

public:
    /**
     * @brief SelfPlay
     * @param rawAgent Raw network agent which uses the raw network policy for e.g. game initiliation
     * @param mctsAgent MCTSAgent which is used during selfplay for game generation
     * @param playSettings Playing setting configuration struct
     * @param numberChunks Number of chunks for for one file in the exported data set
     * @param chunkSize Size of a single chunk. The product of numberChunks and chunkSize is the number of samples in an export file.
     */
    SelfPlay(RawNetAgent* rawAgent, MCTSAgent* mctsAgent, PlaySettings* playSettings, size_t numberChunks, size_t chunkSize);
    ~SelfPlay();

    /**
     * @brief go Starts the self play game generation for a given number of games
     * @param numberOfGames Number of games to generate
     * @param searchLimits Search limit struct
     * @param policySharpening Threshold which is applied after move selection before exporting the policy to undo dirichlet noise
     */
    void go(size_t numberOfGames, SearchLimits& searchLimits, StatesManager* states, float policySharpening);

    /**
     * @brief go_arena Starts comparision matches between the original mctsAgent with the old NN weights and
     * the mctsContender which uses the new updated wieghts
     * @param mctsContender MCTSAgent using different NN weights
     * @param numberOfGames Number of games to compare
     * @param searchLimits Search limit struct
     * @return Score in respect to the contender, as floating point number.
     *  Wins give 1.0 points, 0.5 for draw, 0.0 for loss.
     */
    TournamentResult go_arena(MCTSAgent *mctsContender, size_t numberOfGames, SearchLimits& searchLimits, StatesManager* states);
};
#endif

/**
 * @brief clean_up Applies a clean-up operation after a generated game.
 * Deletes the position, clears the current active states of the StatesManager, clears the game history of the MCTSAgent,
 * calls new_game() for the gamePGN struct
 * @param gamePGN gamePGN struct
 * @param mctsAgent mctsAgent object
 * @param states StatesManager
 * @param position Board position which will be deleted
 */
void clean_up(GamePGN& gamePGN, MCTSAgent* mctsAgent, StatesManager* states, Board* position);

/**
 * @brief init_board Initialies a new board with the starting position of the variant
 * @param variant Variant to be played
 * @param states State manager which takes over the newly created state object
 * @return New board object
 */
Board* init_board(Variant variant, StatesManager* states);

/**
 * @brief init_games_from_raw_policy Inits a new starting position by sampling from the raw policy with temperature 1.
 * The iteration stops either when the number of plys is reached or when the next move would lead to a terminal state.
 * @param rawAgent Handle to the raw agent
 * @param plys Number of plys to generate
 * @param gamePGN Game pgn struct where the moves will be stored
 */
Board* init_starting_pos_from_raw_policy(RawNetAgent& rawAgent, size_t plys, GamePGN& gamePGN, Variant variant, StatesManager* states);

/**
 * @brief clip_ply Clips a given ply touse maxPly as the maximum value. In case of an entry greater than max it is uniformly sampled from
 * [0, maxPly] instead.
 * @param ply Given ply which might be greater than maxPly
 * @param maxPly Maximum ply value
 * @return
 */
size_t clip_ply(size_t ply, size_t maxPly);

#endif // SELFPLAY_H
