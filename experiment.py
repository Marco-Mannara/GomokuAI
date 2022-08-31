import os
import inspect
import sys
import itertools as it

from threading import Thread
from time import sleep
from typing import Dict
from gomoku import check_winning_condition
from match import Match
from tqdm import tqdm

from utils import no_moves_possible

class Experiment:
    def __init__(self, experiment_name : str, player_defs : Dict[str,dict], repetitions : int = 10, experiment_data_path : str = 'experiments'):
        self.player_types = self._get_player_types()

        for data in player_defs.values():
            self._check_player_id(data['class'])

        self.player_defs = player_defs
        self.repetitions = repetitions
        self.experiment_data_path = experiment_data_path
        self.experiment_name=experiment_name
        

    def run(self):
        self._create_dir()
        self._run_experiment()

    def _run_experiment(self):
        matches = list(it.product(self.player_defs, repeat=2))
        print('This experiment will simulate %d matches in total' % (self.repetitions * len(matches)))        
        for m in matches:
            black_id = m[0]
            white_id = m[1]
            black_class = self.player_defs[black_id]['class']
            black_args = self.player_defs[black_id]['args']

            white_class = self.player_defs[white_id]['class']
            white_args = self.player_defs[white_id]['args']

            p_black = self.player_types[black_class](**black_args)
            p_black.name = black_id
            p_white = self.player_types[white_class](**white_args)           
            p_white.name = white_id

            for _ in tqdm(range(self.repetitions), desc='Simulating matches - %s vs. %s' % (m[0],m[1])):
                curr_match = Match(p_black, p_white, gui_enabled=False,save_match_data=True,match_data_path=self.full_path)                                
                curr_match.tags = [black_id + '_bl', white_id + '_wh']
                while not (
                check_winning_condition(curr_match.game) or
                no_moves_possible(curr_match.game.board_state.grid)
                ):
                    sleep(1)
                    if curr_match.game.black_turn:
                        p_black.play_turn()
                    else:
                        p_white.play_turn()


    def _check_player_id(self, id):
        if id not in self.player_types:
            raise Exception('Id \'%s\' is not an existing player type.' % (id))

    def _get_player_types(self) -> dict:
        clsmembers = inspect.getmembers(sys.modules['players'], inspect.isclass)
        return {mem[0].lower().replace('player', '') : mem[1] for mem in clsmembers
        if mem[0].lower() != 'player'}

    def _create_dir(self):
        dir_name_parts = ['experiment',self.experiment_name]
        self.full_path = os.path.join(self.experiment_data_path, '-'.join(dir_name_parts))
        if not os.path.exists(self.full_path):
            try:
                os.makedirs(self.full_path)
            except OSError as e:
                pass
        else:
            pass

if __name__ == '__main__':
    test_players = {
        'ai_sd2' : {
            'class' : 'ai',
            'args' : {
                'search_depth' : 2
            }
        }
    }
    exp = Experiment('test3',test_players, repetitions=5)
    exp.run()
