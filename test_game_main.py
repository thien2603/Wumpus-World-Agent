import time
from world import create_world, move_wumpuses
from agents import SmartAgent
from constants import N

def simulate_one_game(max_steps=200, move_interval=5):
    """Chạy 1 ván game và trả về (win, score)"""
    world, agent = create_world()
    agent = SmartAgent()

    for step in range(max_steps):
        agent.act(world)

        if step % move_interval == 0:
            move_wumpuses(world)
            agent.on_wumpus_moved(world)

        if not agent.alive:
            return False, agent.score  # thua
        if agent.found_gold and (agent.x, agent.y) == (0, 0):
            if not (agent.action_history and agent.action_history[-1][0] == "climb_out"):
                agent.climb_out(world)
            return True, agent.score  # thắng
    return False, agent.score  # hết bước nhưng chưa thắng => coi là thua

def batch_test(num_games=10):
    wins = 0
    total_score = 0
    scores = []

    for i in range(num_games):
        win, score = simulate_one_game()
        scores.append(score)
        total_score += score
        if win:
            wins += 1
        print(f"Game {i+1}: {'WIN' if win else 'LOSE'} | Score={score}")

    avg_score = total_score / num_games
    print("\n===== SUMMARY =====")
    print(f"Total games: {num_games}")
    print(f"Wins: {wins}")
    print(f"Losses: {num_games - wins}")
    print(f"Win rate: {wins/num_games:.2%}")
    print(f"Average score: {avg_score:.2f}")

    return wins, num_games - wins, avg_score

if __name__ == "__main__":
    batch_test(100)