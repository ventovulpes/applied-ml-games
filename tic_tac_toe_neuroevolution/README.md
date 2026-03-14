# Tic Tac Toe AI (Neuroevolution)
A reimplementation of Fogel's Tic Tac Toe paper which creates a Tic Tac Toe AI using a neural network. The AI is trained over 20 trials of 800 generations. Each generation begins with 50 networks which replicate and create children with modified weights determined with a normal distribution. Each network plays against a set heuristic opponent and receives a payoff depending on if it wins or loses. The payoffs of each network are then compared to each other and the top 50 networks move on to the next generation.

## Usage
To run and plot the performance of the evolution:

`python evolution.py`

To compare my best weights from evolution to the heuristic opponent:

`python neural_network.py`
