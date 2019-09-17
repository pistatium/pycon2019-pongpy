from pongpy.interfaces.team import Team
from pongpy.models.game_info import GameInfo
from pongpy.models.state import State
from pongpy.models.pos import Pos
import random

class JXTeam(Team):

    prev_ball: Pos

    @property
    def name(self) -> str:
        return 'JX Team'

    def __init__(self):
        self.prev_ball = Pos(0, 0)

    def atk_action(self, info: GameInfo, state: State) -> int:
        my_pos = state.mine_team.atk_pos
        ball_pos = state.ball_pos
        delta = 2.0

        py = self.predict_y(info, my_pos, ball_pos)

        # 内側にある時は避ける
        if (state.is_right_side and (my_pos.x < ball_pos.x)) or (not state.is_right_side and (my_pos.x > ball_pos.x)):
                py = py - info.height // 2 if py > info.height // 2 else py + info.height // 2

        return self.aim_to(my_pos, py + delta, state.enemy_team.score) * info.atk_return_limit

    def def_action(self, info: GameInfo, state: State) -> int:
        my_pos = state.mine_team.def_pos
        ball_pos = state.ball_pos

        py = self.predict_y(info, my_pos, ball_pos)
        # set pos
        self.prev_ball = ball_pos

        # ゴール内にある時は真ん中へ
        if state.is_right_side:
            if my_pos.x < ball_pos.x:
                return self.aim_to(my_pos, info.height // 2)
        else:
            if my_pos.x > ball_pos.x:
                return self.aim_to(my_pos, info.height // 2)

        return self.aim_to(my_pos, py, state.enemy_team.score) * info.def_return_limit

    def predict_y(self, info, my_pos, ball_pos) -> int:
        diff_x = abs(my_pos.x - ball_pos.x)
        vec_y = ball_pos.y - self.prev_ball.y
        total_y = + ball_pos.y + vec_y * diff_x

        if total_y % (info.height * 2) <= info.height:
            return total_y % info.height
        else:
            return info.height * 2 - total_y % (2 * info.height)

    def aim_to(self, current_pos: Pos, target_y: int, enemy_score: int = 0):
        # レベル調整
        if enemy_score <= 5:
            if random.randint(0, 6 - enemy_score) >= 2:
                return 0

        diff = target_y - current_pos.y
        if diff < -1:
            return -1
        if diff < 1:
            return 0
        return 1
