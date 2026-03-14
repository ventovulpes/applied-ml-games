from collections import defaultdict

class Node:
    def __init__(self, state: list[list[str | None]], turn: int, depth: int, winner: str = '', minimax: int | None = None):
        self.state = state
        self.turn = turn
        self.depth = depth
        self.winner = winner
        self.minimax = minimax
    
    def __repr__(self):
        return f'{self.state[0]}\n{self.state[1]}\n{self.state[2]}\n'

class HeuristicTicTacToeTree:
    SYMBOLS = ['X', 'O']
    def __init__(self, player_perspective, n_ply):
        self.root = Node([
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ], 0, 1)
        self.player_perspective = player_perspective
        self.edges = {}
        self.nodes = {self.hash_state(self.root.state): self.root}
        self.n_ply = n_ply
        self.construct_tree()
        self.label_minimax(self.root, player_perspective)

    def get_winner(self, state) -> str | None:
        for row in state:
            symbol = row[0]
            if not symbol:
                continue
            won_by_row = True
            for n in row:
                if n != symbol:
                    won_by_row = False
                    break
            if won_by_row:
                return symbol
        for c in range(3):
            symbol = state[0][c]
            if not symbol:
                continue
            won_by_col = True
            for row in state:
                if row[c] != symbol:
                    won_by_col = False
                    break
            if won_by_col:
                return symbol
        top_left = state[0][0]
        if top_left:
            if top_left == state[1][1] and top_left == state[2][2]:
                return top_left
        top_right = state[0][2]
        if top_right:
            if top_right == state[1][1] and top_right == state[2][0]:
                return top_right
        return None
    
    def is_filled(self, state) -> bool:
        is_filled = True
        for r in state:
            for c in r:
                if not c:
                    is_filled = False
        return is_filled
    
    def copy_state(self, state: list[list[str | None]]):
        new_state = []
        for row in state:
            new_state.append(row.copy())
        return new_state
    
    def get_children(self, parent: Node) -> list[Node]:
        if parent not in self.edges.keys():
            return []
        return self.edges[parent]
    
    def hash_state(self, state: list[list[str | None]]):
        hashed = ''
        for row in state:
            for v in row:
                hashed += v if v else 'None'
        return hashed
    
    def get_move_change(self, a: list[list[str | None]], b: list[list[str | None]]) -> int:
        for r in range(len(a)):
            if a[r] is not b[r]:
                for c in range(len(a[r])):
                    if a[r][c] is not b[r][c]:
                        return 3 * r + c
        return None
    
    def count_leaf_nodes(self) -> int:
        queue = [self.root]
        visited = {self.root}
        count = 0
        while queue:
            cur = queue.pop(0)
            children = self.get_children(cur)
            if children:
                for c in children:
                    if c not in visited:
                        visited.add(c)
                        queue.append(c)
            else:
                count += 1
                print(count)
        return count
    
    def count_nodes(self):
        return len(self.nodes)

    leaf_count = 0
    def construct_tree(self):
        queue = [self.root]
        while queue:
            cur = queue.pop()
            if cur.depth - self.root.depth > self.n_ply:
                continue
            has_child = False
            for r in range(3):
                for c in range(3):
                    if not cur.state[r][c]:
                        has_child = True
                        next_state = self.copy_state(cur.state)
                        next_state[r][c] = self.SYMBOLS[cur.turn]
                        hashed_state = self.hash_state(next_state)
                        if not hashed_state in self.nodes:
                            child = Node(next_state, (cur.turn + 1) % 2, cur.depth + 1)
                            self.nodes[hashed_state] = child
                            winner = self.get_winner(child.state)
                            if not winner:
                                queue.append(child)
                            else:
                                child.winner = winner
                                self.leaf_count += 1
                        else:
                            child = self.nodes[hashed_state]

                        self.edges.setdefault(cur, []).append(child)
            if not has_child:
                self.leaf_count += 1

    def update_tree(self, state: list[list[str | None]]):
        new_root = self.nodes[self.hash_state(state)]
        new_edges = {}
        new_nodes = {}
        visited = {new_root}
        q = [new_root]
        # bfs to check if all edges should be pruned or not
        while q:
            cur = q.pop(0)
            if not cur in self.edges.keys():
                continue
            for c in self.edges[cur]:
                new_edges.setdefault(cur, []).append(c)
                new_nodes[self.hash_state(new_root.state)] = new_root
                if c not in visited:
                    visited.add(c)
                    q.append(c)
        self.edges = new_edges
        self.root = new_root
        self.nodes = new_nodes
        self.construct_tree()
        self.label_minimax(self.root, self.player_perspective)


    def label_minimax(self, cur: Node, player_perspective: int):
        children = self.get_children(cur)
        if not children:
            winner = self.get_winner(cur.state)
            if winner is None:
                if self.is_filled(cur.state):
                    # definite tie
                    cur.minimax = 0
                else:
                    cur.minimax = self.heuristic(cur)
            elif winner == self.SYMBOLS[player_perspective]:
                cur.minimax = 1
            else:
                cur.minimax = -1
            return
        if any(c.minimax is None for c in children):
            for c in children:
                if c.minimax is None:
                    self.label_minimax(c, player_perspective)
        # all children are already labeled
        if cur.turn == player_perspective:
            cur.minimax = max([c.minimax for c in children])
        else:
            cur.minimax = min([c.minimax for c in children])

    def check_for_two_in_line_with_last_empty(self, line: list[str | None]) -> int:
        # returns 1 if self has 2, -1 if opponent has 2, 0 if neither
        n_self = 0
        n_empty = 0
        for n in line:
            if n == self.SYMBOLS[self.player_perspective]:
                n_self += 1
            elif n == None:
                n_empty += 1
        if n_empty != 1:
            return 0
        if n_self == 2:
            return 1
        elif n_self == 0:
            return -1
        return 0
            
    def heuristic(self, cur: Node):
        state = cur.state
        eval = 0
        for row in state:
            eval += self.check_for_two_in_line_with_last_empty(row)
        for c in range(3):
            col = []
            for r in range(3):
                col.append(state[r][c])
            eval += self.check_for_two_in_line_with_last_empty(col)
        eval += self.check_for_two_in_line_with_last_empty([state[0][0], state[1][1], state[2][2]])
        eval += self.check_for_two_in_line_with_last_empty([state[0][2], state[1][1], state[2][0]])
        return eval / 8
            

# t = HeuristicTicTacToeTree(0, 2)
# t.update_tree(t.get_children(t.root)[0])
# print(t.heuristic(Node([
#     ['X', 'X', None],
#     ['O', None, 'O'],
#     [None, None, 'X']
# ], 0, 1)))
# # print(t.edges)