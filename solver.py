from collections import deque
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple

State = Any
Move = Any
GetMovesFn = Callable[[State], Iterable[Move]]
ApplyMoveFn = Callable[[State, Move], State]
IsGoalFn = Callable[[State], bool]
StateKeyFn = Callable[[State], Any]


def default_state_key(state: State) -> Any:
    try:
        return tuple(state)
    except TypeError:
        return repr(state)


def solve_gamestate(
    initial_state: State,
    get_moves: GetMovesFn,
    apply_move: ApplyMoveFn,
    is_goal: IsGoalFn,
    max_iterations: int = 100000,
    state_key: StateKeyFn = default_state_key,
) -> Optional[List[Move]]:
    """
    Breadth-first search solver for a generic game state.

    initial_state: current game state object
    get_moves: function(state) -> iterable of legal moves
    apply_move: function(state, move) -> next state
    is_goal: function(state) -> bool
    state_key: function(state) -> hashable representation
    """
    queue: Deque[State] = deque()
    queue.append(initial_state)

    parents: Dict[Any, Tuple[Optional[Any], Optional[Move]]] = {}
    start_key = state_key(initial_state)
    parents[start_key] = (None, None)

    visited = {start_key}
    iterations = 0

    while queue:
        if iterations >= max_iterations:
            return None
        iterations += 1

        current_state = queue.popleft()
        current_key = state_key(current_state)

        if is_goal(current_state):
            return _reconstruct_path(current_key, parents)

        for move in get_moves(current_state):
            next_state = apply_move(current_state, move)
            next_key = state_key(next_state)

            if next_key in visited:
                continue

            visited.add(next_key)
            parents[next_key] = (current_key, move)
            queue.append(next_state)

    return None


def _reconstruct_path(
    goal_key: Any,
    parents: Dict[Any, Tuple[Optional[Any], Optional[Move]]],
) -> List[Move]:
    path: List[Move] = []
    current_key = goal_key

    while True:
        parent_info = parents.get(current_key)
        if parent_info is None:
            break
        parent_key, move = parent_info
        if parent_key is None:
            break
        path.append(move)
        current_key = parent_key

    path.reverse()
    return path