class ChineseCheckers:
    def __init__(self, player_count=2):
        self.player_count = player_count
        self.board = {}
        self.init_board()

    def init_board(self):
        self.board = {}

        # Cube directions (pointy top hex)
        cube_dirs = [
            (1, -1, 0),
            (1, 0, -1),
            (0, 1, -1),
            (-1, 1, 0),
            (-1, 0, 1),
            (0, -1, 1)
        ]

        # === 1) CENTER HEX (radius 4) ===
        center = []
        for x in range(-4, 5):
            for y in range(-4, 5):
                z = -x - y
                if max(abs(x), abs(y), abs(z)) <= 4:
                    center.append((x, y, z))

        # convert cube to axial (q=x, r=z)
        for (x, y, z) in center:
            self.board[(x, z)] = 0

        # === 2) 6 CORNER TRIANGLES (correct shape!) ===
        corner_triangles = []

        for d in range(6):
            dx, dy, dz = cube_dirs[d]
            dx2, dy2, dz2 = cube_dirs[(d + 1) % 6]  # next direction clockwise

            # apex distance MUST be 6
            apex = (dx * 7, dy * 7, dz * 7)


            tri = []

            # rows: 4 + 3 + 2 + 1 = 10
            for i in range(5):
                for j in range(5 - i):
                    # but ignore center-most 5 positions
                    if i == 4:  # only apex row is single point
                        if j > 0:
                            continue
                    x = apex[0] - i * dx - j * dx2
                    y = apex[1] - i * dy - j * dy2
                    z = apex[2] - i * dz - j * dz2

                    tri.append((x, y, z))
                    self.board[(x, z)] = 0  # axial coords

            corner_triangles.append(tri)

        # === 3) ASSIGN PLAYERS ===
        final = {pos: 0 for pos in self.board}

        if self.player_count == 2:
            assign = {1: [0], 2: [3]}

        elif self.player_count == 3:
            assign = {1: [0], 2: [2], 3: [4]}

        else:
            assign = {pid: [pid - 1] for pid in range(1, 7)}

        for pid, tri_ids in assign.items():
            for tid in tri_ids:
                for (x, y, z) in corner_triangles[tid]:
                    final[(x, z)] = pid

        self.board = final

    # === Move Logic ===
    def get_valid_moves(self, player_id):
        moves = []
        pieces = [pos for pos, pid in self.board.items() if pid == player_id]
        directions = [(1, 0), (1, -1), (0, -1),
                      (-1, 0), (-1, 1), (0, 1)]

        for q, r in pieces:
            # step
            for dq, dr in directions:
                nq, nr = q + dq, r + dr
                if (nq, nr) in self.board and self.board[(nq, nr)] == 0:
                    moves.append(((q, r), (nq, nr)))

            # jump
            for dq, dr in directions:
                aq, ar = q + dq, r + dr
                jq, jr = q + 2 * dq, r + 2 * dr
                if (aq, ar) in self.board and self.board[(aq, ar)] != 0:
                    if (jq, jr) in self.board and self.board[(jq, jr)] == 0:
                        moves.append(((q, r), (jq, jr)))

        return moves

    def apply_move(self, start, end):
        if self.board[start] == 0:
            return False
        p = self.board[start]
        self.board[start] = 0
        self.board[end] = p
        return True

    def check_winner(self):
        return 0
