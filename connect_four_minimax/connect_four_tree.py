class Node:
    def __init__(self, state: list[list[str | None]], turn: int, depth: int, winner: str | None = None, minimax: int | None = None):
        self.state = state
        self.turn = turn
        self.depth = depth
        self.winner = winner
        self.minimax = minimax

    def __repr__(self):
        string = ''
        for row in self.state:
            string += str(row) + '\n'
        return string

SYMBOLS = ['X', 'O']

class ConnectFourTree:
    def __init__(self, perspective: int, n_ply: int):
        self.perspective = perspective
        self.n_ply = n_ply
        empty_grid = []
        for i in range(6):
            empty_grid.append([])
            for _ in range(7):
                empty_grid[i].append(None)
        self.root = Node(empty_grid, 0, 1)
        self.edges = {self.root : []}
        self.nodes = {self.stringify_state(self.root.state) : self.root}

        self.construct_tree()
        self.label_minimax(self.root)

    def stringify_state(self, state: list[list[str | None]]) -> str:
        string = ''
        for row in state:
            for n in row:
                string += n if n is not None else 'N'
            string += ' '
        return string
    
    def copy_state(self, state: list[list[str | None]]) -> list[list[str | None]]:
        copy = []
        for row in state:
            copy.append([])
            for n in row:
                copy[-1].append(n)
        return copy
    
    def construct_tree(self):
        # construct tree using bfs
        q = [self.root]

        while q:
            cur_node = q.pop()
            if (cur_node.depth - self.root.depth + 1 >= self.n_ply or cur_node in self.nodes.items()):
                continue
            cur_state = cur_node.state
            for c in range(7):
                if cur_state[0][c] is not None:
                    continue
                for r in range(5, -1, -1):
                    if cur_state[r][c] is not None:
                        continue
                    new_state = self.copy_state(cur_state)
                    new_state[r][c] = SYMBOLS[cur_node.turn]
                    if self.stringify_state(new_state) not in self.nodes:
                        child = Node(new_state, (cur_node.turn + 1) % 2, cur_node.depth + 1)
                        self.nodes[self.stringify_state(child.state)] = child
                    else:
                        # if state already exists, use that node and attach it to the current node as a child
                        child = self.nodes[self.stringify_state(new_state)]
                        child.depth = cur_node.depth + 1
                            
                    q.append(child)
                    self.edges.setdefault(cur_node, []).append(child)
                    break

    def get_children(self, node: Node) -> list[Node]:
        if node not in self.edges.keys():
            return []
        return self.edges[node]
    
    def get_lines(self, state: list[list[str | None]]):
        lines = []
        for row in state:
            lines.append(row)
        for c in range(7):
            col = []
            for r in range(6):
                col.append(state[r][c])
            lines.append(col)
        # diagonals starting from top
        for c in range(4):
            diag = []
            i = 0
            while i < 6 and i + c < 7:
                diag.append(state[i][c + i])
                i += 1
            lines.append(diag)
        for c in range(3, 7):
            diag = []
            i = 0
            while 5 - i >= 0 and c - i >= 0:
                diag.append(state[i][c - i])
                i += 1
            lines.append(diag)
        # remaining diagonals starting from sides
        for i in range(1, 3):
            diag_left = []
            diag_right = []
            j = i
            while j <= 5:
                diag_left.append(state[j][(j - i)])
                diag_right.append(state[j][6 - (j - i)])
                j += 1
            lines.append(diag_left)
            lines.append(diag_right)
        return lines
    
    def get_winner(self, state):
        lines = self.get_lines(state)
        for line in lines:
            last_symbol = None
            run = 0
            for n in line:
                if n is None:
                    last_symbol = None
                    run = 0
                elif n == last_symbol:
                    run += 1
                else:
                    last_symbol = n
                    run = 1

                if run >= 4:
                    return last_symbol
        return None
    
    def board_is_filled(self, state):
        for row in state:
            for n in row:
                if n is None:
                    return False
        return True

    def label_minimax(self, node: Node):
        # recursively label minimax
        winner = self.get_winner(node.state)
        if winner == SYMBOLS[self.perspective]:
            node.minimax = 1
            return
        elif winner is not None:
            node.minimax = -1
            return
        if self.board_is_filled(node.state):
            node.minimax = 0
            return
        if node.depth - self.root.depth + 1 >= self.n_ply:
            node.minimax = self.heuristic(node.state)
            return
        # label children first, then self
        children = self.get_children(node)
        for c in children:
            if c.minimax is None:
                self.label_minimax(c)
        if node.turn == self.perspective:
            node.minimax = max([c.minimax for c in children])
        else:
            node.minimax = min([c.minimax for c in children])

    def heuristic(self, state: list[list[str | None]]) -> float:
        player_score = 0
        opponent_score = 0
        lines = self.get_lines(state)
        total_possibilities = 0
        opponent_symbol = SYMBOLS[(self.perspective + 1) % 2]
        for i in range(len(lines)):
            line = lines[i]
            for s in range(len(line) - 3):
                total_possibilities += 1
                player_count = line[s : s+4].count(SYMBOLS[self.perspective])
                opponent_count = line[s : s+4].count(opponent_symbol)
                if opponent_count == 0:
                    if player_count == 3:
                        player_score += 0.75
                        # extra weight for rows closer to the bottom and columns
                        if 2 < i <= 12:
                            player_score += 0.25
                    if player_count == 2:
                        player_score += 0.5
                if player_count == 0:
                    if opponent_count == 3:
                        opponent_score += 0.75
                        if 2 < i <= 12:
                            opponent_score += 0.25
                    if opponent_count == 2:
                        opponent_score += 0.5
        return (player_score - opponent_score) / total_possibilities
    
    def update_tree(self, state: list[list[str | None]]):
        # first prune trees
        new_root = self.nodes[self.stringify_state(state)]
        new_edges = {}
        new_nodes = {}
        q = [new_root]
        visited = {new_root}
        while q:
            cur_node = q.pop()
            new_nodes[self.stringify_state(cur_node.state)] = cur_node
            if cur_node not in self.edges:
                continue
            # travel to all edges after new root (thereby discarding all previous unnecessary nodes)
            for child in self.edges[cur_node]:
                new_edges.setdefault(cur_node, []).append(child)
                if child not in visited:
                    visited.add(child)
                    q.append(child)
        self.root = new_root
        self.edges = new_edges
        self.nodes = new_nodes
        # then add new nodes
        self.construct_tree()
        self.label_minimax(self.root)

    def get_move_change(self, state_a: list[list[str | None]], state_b: list[list[str | None]]):
        for c in range(7):
            for r in range(5, -1, -1):
                if state_a[r][c] != state_b[r][c]:
                    return c
        return None