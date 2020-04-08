from w2_dice_aiplayer import AI
from w2_dice_game import Game
import numpy as np
from numpy import random
import random
from typing import List


class Trainer:
    bodo_linear_factor = np.array([1, -0.5, 1, -0.5, 1, 0.5, 1, 0.5, -2.5])
    bodo_bias = np.array([0, 0, 0, 0, 0, -6, 0, -6, 0])

    def __init__(self, group_size=1, population_size=100, survivor_rate=0.95, child_rate=0.5, mutation_rate=0.005,
                 generations=300, saved_ais_rate=0.15):
        self.group_size = group_size
        self.population_size = population_size
        self.survivor_rate = survivor_rate
        self.child_rate = child_rate
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.saved_ais_rate = saved_ais_rate

    def _group(self, population) -> List[AI]:
        random.shuffle(population)
        groups = []
        for ai_index in range(0, len(population), self.group_size):
            groups.append(population[ai_index: ai_index + self.group_size])
        return groups

    def _rank(self, groups) -> List[AI]:
        placement_groups = [[] for _ in range(self.group_size)]
        for group in groups:
            game = Game(group)
            game.play()
            group_ranking = game.compute_ranking()
            placement = 0
            for ai, points in group_ranking:
                placement_groups[placement].append(ai)
                placement += 1
        ranking = []
        for placement_group in placement_groups:
            ranking.extend(placement_group)
        assert(len(ranking) == self.population_size)
        return ranking

    def _select(self, population_ranked) -> List[AI]:
        return population_ranked[0: int(self.survivor_rate * self.population_size)]  # slice operation

    def _mix_strategies(self, parent1, parent2) -> AI:
        child_linear_factor = np.array([x / 2 for x in (parent1.linear_factor + parent2.linear_factor)])
        child_bias = np.array([x / 2 for x in (parent1.bias + parent2.bias)])
        assert (len(child_linear_factor) == len(parent1.linear_factor) and len(child_linear_factor) == len(
            parent2.linear_factor))
        return AI("", self.group_size - 1, child_linear_factor, child_bias)

    def _recombine(self, population) -> List[AI]:
        children = []
        children_count = int((self.population_size - len(population)) * self.child_rate)  # = 25 (default value)
        for child_index in range(children_count):  # build pairs
            child = self._mix_strategies(population[child_index * 2], population[child_index * 2 + 1])
            children.append(child)
        population.extend(children)
        return population

    def _mutate_strategy(self, ai) -> AI:
        for value_index in range(len(ai.linear_factor)):
            if random.random() < self.mutation_rate:
                ai.linear_factor[value_index] = random.random()
            if random.random() < self.mutation_rate:
                ai.bias[value_index] = random.random()
        return ai

    def _mutate(self, population) -> List[AI]:
        mutated_population = []
        for ai in population:
            self.append = mutated_population.append(self._mutate_strategy(ai))
        return mutated_population

    def _add_random_ais(self, population) -> List[AI]:
        missing_ais = self.population_size - len(population)
        population.extend(
            [AI("", self.group_size - 1, Trainer.bodo_linear_factor, Trainer.bodo_bias) for _ in range(missing_ais)])
        # [AI("", self.group_size - 1, np.random.rand(self.group_size * 9)) for _ in range(missing_ais)])
        return population

    def _find_max_points(self, population):
        max_points = -100
        for ai in population:
            max_points = max(ai.get_points(), max_points)
        return max_points

    def _find_avg_points(self, population):
        sum_points = 0
        for ai in population:
            sum_points += ai.get_points()
        return sum_points / self.population_size

    def _compute_next_generation(self, population) -> List[AI]:
        population = self._select(population)
        best_ais = population[:int(self.population_size*self.saved_ais_rate)]
        self._save_best_ais(best_ais)
        population = self._recombine(population)
        population = self._mutate(population)
        population = self._add_random_ais(population)
        population = self._group(population)
        population = self._rank(population)
        return population

    def _build_initial_population(self) -> List[AI]:
        # return [AI("", self.group_size - 1, np.random.rand(self.group_size * 9), random.randint(-1, 1))for _ in
        # range(self.population_size)]  # fill in linear_factor
        return [AI("", self.group_size - 1, Trainer.bodo_linear_factor, Trainer.bodo_bias)
                for _ in range(self.population_size)]
        # return [AI("", self.group_size - 1, np.zeros((self.group_size * 9,)), random.randint(-1, 1)) for _ in
        # range(self.population_size)]

    def train(self) -> AI:
        population = self._build_initial_population()
        population = self._group(population)
        population = self._rank(population)
        for generation in range(self.generations):
            new_population = self._compute_next_generation(population)
            max_points = self._find_max_points(new_population)
            new_avg_points = self._find_avg_points(new_population)
            avg_points = new_avg_points
            population = new_population
            print("Generation: {} \t Max: {} \t Avg: {}".format(generation, max_points, avg_points))
        print("evolution finished")
        best_ai = population[0]
        return best_ai

    def _save_best_ais(self, best_ais):
        np.save("best_ais_file", best_ais, allow_pickle=True, fix_imports=True)      # where is the file saved?
        # os.system("cmd")
        # best_ais = [best_ais]
        # pickle.dump(best_ais, open("best_ais.dat", "wb"))        # todo test function -> doesn't work

    def _load_best_ais(self):                                # todo apply function
        # best_ais = np.load(best_ais_file.npy)
        best_ais = np.load("best_ais_file")
        return best_ais


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()