import pygame
import random
import copy

pygame.init()
WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Trap")
FONT = pygame.font.SysFont("arial", 20)

BOARD_ROWS = 5
TILE_SIZE = 60
TRAPS_PER_PLAYER = 2
NUM_PLAYERS = 3
PLAYER_COLORS = [(255, 0, 0), (0, 128, 0), (0, 0, 255)]
AI_PLAYER_ID = 2
MINIMAX_DEPTH = 2

def create_board():
    board = []
    for r in range(BOARD_ROWS):
        for c in range(r + 1):
            x = WIDTH // 2 + (c - r / 2) * TILE_SIZE
            y = 100 + r * TILE_SIZE * 0.9
            board.append(((r, c), (x, y)))
    return board

triangle_board = create_board()
all_positions = [p for p, _ in triangle_board]

def get_neighbors(pos):
    r, c = pos
    moves = [(1, 0), (1, 1), (-1, 0), (-1, -1), (0, 1), (0, -1)]
    return [(r + dr, c + dc) for dr, dc in moves if (r + dr, c + dc) in all_positions]

def heuristic(player, others):
    score = 10 * len(player["towers"])
    for pt in player["towers"]:
        for other in others:
            for ot in other["towers"]:
                if abs(ot[0] - pt[0]) <= 1 and abs(ot[1] - pt[1]) <= 1:
                    score += 5
        if all(n in [t for p in others for t in p["towers"]] or n in traps for n in get_neighbors(pt)):
            score -= 3
    return score

def minimax(state, traps, depth, maximizing):
    if depth == 0:
        ai = state[AI_PLAYER_ID]
        others = [p for i, p in enumerate(state) if i != AI_PLAYER_ID]
        return heuristic(ai, others), None
    best_score = float('-inf') if maximizing else float('inf')
    best_move = None
    player = state[AI_PLAYER_ID]
    for tower in player["towers"]:
        for move in get_neighbors(tower):
            if move not in [t for p in state for t in p["towers"]]:
                sim = copy.deepcopy(state)
                sim[AI_PLAYER_ID]["towers"].remove(tower)
                if move not in traps:
                    sim[AI_PLAYER_ID]["towers"].append(move)
                score, _ = minimax(sim, traps.copy(), depth - 1, not maximizing)
                if maximizing and score > best_score:
                    best_score, best_move = score, (tower, move)
                elif not maximizing and score < best_score:
                    best_score, best_move = score, (tower, move)
    return best_score, best_move

def all_moves(player, traps, players):
    moves = []
    for tower in player["towers"]:
        for n in get_neighbors(tower):
            if n not in [t for p in players for t in p["towers"]]:
                moves.append((tower, n))
    return moves

def place_trap(player, traps, players):
    used = set(t for p in players for t in p["towers"])
    options = [p for p in all_positions if p not in traps and p not in used]
    if len(player["traps"]) < TRAPS_PER_PLAYER and options:
        return random.choice(options)
    return None

def draw(players, traps, winner=None):
    SCREEN.fill((240, 240, 240))
    for (pos, (x, y)) in triangle_board:
        pygame.draw.circle(SCREEN, (200, 200, 200), (int(x), int(y)), 25)
        pygame.draw.circle(SCREEN, (0, 0, 0), (int(x), int(y)), 25, 2)
        for i, p in enumerate(players):
            if pos in p["towers"]:
                pygame.draw.circle(SCREEN, PLAYER_COLORS[i], (int(x), int(y)), 15)
        if pos in traps:
            pygame.draw.circle(SCREEN, (0, 0, 0), (int(x), int(y)), 5)
    if winner is not None:
        text = FONT.render(f"Player {winner + 1} Wins!" if winner != -1 else "It's a Draw!", True, (255, 0, 0))
        SCREEN.blit(text, (WIDTH // 2 - 80, 30))

def get_tile(pos):
    for (tile, (x, y)) in triangle_board:
        if (pos[0] - x)**2 + (pos[1] - y)**2 < 25**2:
            return tile
    return None

def check_win(players):
    alive = [p for p in players if len(p["towers"]) > 0]
    if len(alive) == 1:
        return alive[0]["id"]
    if len(alive) == 0:
        return -1
    return None

def next_turn(cur, players):
    for i in range(1, NUM_PLAYERS + 1):
        nxt = (cur + i) % NUM_PLAYERS
        if players[nxt]["towers"]:
            return nxt
    return None

players = [{"towers": [pos], "traps": set(), "id": i} for i, pos in enumerate([(0, 0), (4, 0), (4, 4)])]
traps = {}
turn = next_turn(-1, players)
winner = None
selected = None
run = True


while run:
    draw(players, traps, winner)
    if not winner:
        msg = f"Player {turn + 1}'s Turn"
        SCREEN.blit(FONT.render(msg, True, (0, 0, 0)), (20, 20))
    pygame.display.flip()

    if not winner and turn == AI_PLAYER_ID:
        ai = players[turn]
        moves = all_moves(ai, traps, players)
        safe = [(f, t) for f, t in moves if t not in traps]
        move = safe[0] if safe else (moves[0] if moves else None)
        if move:
            f, t = move
            ai["towers"].remove(f)
            if t not in traps:
                ai["towers"].append(t)
        tp = place_trap(ai, traps, players)
        if tp:
            traps[tp] = turn
            ai["traps"].add(tp)
        winner = check_win(players)
        if not winner:
            turn = next_turn(turn, players)
        pygame.time.delay(500)
        continue

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

        if not winner and turn != AI_PLAYER_ID and e.type == pygame.MOUSEBUTTONDOWN:
            tile = get_tile(e.pos)
            if not tile:
                continue
            player = players[turn]

            if tile in [t for p in players for t in p["towers"]]:
                if tile in player["towers"]:
                    selected = tile
                continue

            if selected:
                if tile in get_neighbors(selected) and tile not in [t for p in players for t in p["towers"]]:
                    player["towers"].remove(selected)
                    if tile not in traps:
                        player["towers"].append(tile)
                    selected = None
                    winner = check_win(players)
                    if not winner:
                        turn = next_turn(turn, players)
                elif tile not in traps:


                    traps[tile] = turn
                    player["traps"].add(tile)
                    selected = None
                    winner = check_win(players)
                    if not winner:
                        turn = next_turn(turn, players)
            else:
                if tile in player["towers"]:
                    selected = tile
                elif tile not in traps and tile not in [t for p in players for t in p["towers"]]:

                    traps[tile] = turn
                    player["traps"].add(tile)
                    winner = check_win(players)
                    if not winner:
                        turn = next_turn(turn, players)

pygame.quit()

