class Node:
    def __init__(self, state: list[list[str | None]], turn: int, winner: str = '', minimax: int | None = None):
        self.state = state
        self.turn = turn
        self.winner = winner
        self.minimax = minimax
    
    def __repr__(self):
        return f'{self.state[0]}\n{self.state[1]}\n{self.state[2]}\n'

class TicTacToeTree:
    SYMBOLS = ['X', 'O']
    def __init__(self, player_perspective):
        self.root = Node([
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ], 0)
        self.edges = []
        self.nodes = {self.hash_state(self.root.state): self.root}
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
    
    def copy_state(self, state: list[list[str | None]]):
        new_state = []
        for row in state:
            new_state.append(row.copy())
        return new_state
    
    def get_children(self, parent: Node) -> list[Node]:
        children = []
        for e in self.edges:
            if e[0] == parent:
                children.append(e[1])
        return children
    
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
            has_child = False
            for r in range(3):
                for c in range(3):
                    if not cur.state[r][c]:
                        has_child = True
                        next_state = self.copy_state(cur.state)
                        next_state[r][c] = self.SYMBOLS[cur.turn]
                        hashed_state = self.hash_state(next_state)
                        if not hashed_state in self.nodes:
                            child = Node(next_state, (cur.turn + 1) % 2)
                            self.nodes[hashed_state] = child
                            winner = self.get_winner(child.state)
                            if not winner:
                                queue.append(child)
                            else:
                                child.winner = winner
                                self.leaf_count += 1
                        else:
                            child = self.nodes[hashed_state]

                        self.edges.append((cur, child))
            if not has_child:
                self.leaf_count += 1

    def label_minimax(self, cur: Node, player_perspective: int):
        if cur.minimax is not None:
            return
        children = self.get_children(cur)
        if not children:
            winner = self.get_winner(cur.state)
            if winner is None:
                cur.minimax = 0
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