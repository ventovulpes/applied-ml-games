from neural_network import NeuralNetwork, run_game
import random
from matplotlib import pyplot as plt

H_RANGE = 10
INITIAL_WEIGHT_RANGE = 0.5

NUM_TRIALS = 20
NUM_ORIGINAL_PARENTS = 50
NUM_GENERATIONS = 800

sum_max_payoffs = [0 for _ in range(NUM_GENERATIONS)]
best_player = None
best_player_score = -999999

for t in range(NUM_TRIALS):
    # create initial population
    neural_networks = []
    for _ in range(NUM_ORIGINAL_PARENTS):
        H = random.randint(1, H_RANGE)
        weights = [
            [
                [random.uniform(-INITIAL_WEIGHT_RANGE, INITIAL_WEIGHT_RANGE) for _ in range(10)] for _ in range(9)
            ],
            [
                [random.uniform(-INITIAL_WEIGHT_RANGE, INITIAL_WEIGHT_RANGE) for _ in range(10)] for _ in range(H)
            ],
            [
                [random.uniform(-INITIAL_WEIGHT_RANGE, INITIAL_WEIGHT_RANGE) for _ in range(H + 1)] for _ in range(9)
            ]
        ]
        neural_networks.append(NeuralNetwork(weights, H_RANGE))

    max_payoffs = []
    for g in range(NUM_GENERATIONS):
        # create children
        new_networks = []
        for nn in neural_networks:
            new_networks.append(nn.create_child())
        neural_networks += new_networks

        # calculate payoffs playing against near-perfect opponent
        payoffs = []
        for nn in neural_networks:
            payoff_sum = 0
            for _ in range(32):
                payoff_sum += run_game(nn)
            payoffs.append(payoff_sum)
        max_payoffs.append(max(payoffs))

        # compare payoffs to others in generation
        scores = []
        for i in range(len(neural_networks)):
            payoff = payoffs[i]
            score = 0
            for _ in range(10):
                index = random.randint(0, NUM_ORIGINAL_PARENTS * 2 - 1)
                while index == i:
                    index = random.randint(0, NUM_ORIGINAL_PARENTS * 2 - 1)
                if payoff > payoffs[index]:
                    score += 1
            scores.append(score)

        # keep top 50% nns
        paired = [(s, nn) for (s, nn) in zip(scores, neural_networks)]
        paired.sort(key=lambda p: p[0])
        neural_networks = [p[1] for p in paired[NUM_ORIGINAL_PARENTS:]]
        print(f'trial {t}: generation {len(max_payoffs)}: {max_payoffs[-1]}')

        if g == NUM_GENERATIONS - 1:
            if paired[0][0] > best_player_score:
                best_player = paired[0][1]
    for i in range(len(max_payoffs)):
        sum_max_payoffs[i] += max_payoffs[i]

mean_max_payoffs = [p / NUM_TRIALS for p in sum_max_payoffs]

print(best_player.weights)

plt.plot(mean_max_payoffs)
plt.show()