from w2_dice_aiplayer import AI
from w2_dice_game import Game
from numpy import random
import numpy as np
import random
from typing import List


class Trainer:
    def __init__(self, group_size=1, population_size=100, survivor_ratio=0.95, child_ratio=0.5, mutation_rate=0.005,
                 generations=1000, accept_all_generations=True):
        self.group_size = group_size
        self.population_size = population_size
        self.survivor_ratio = survivor_ratio
        self.child_ratio = child_ratio
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.accept_all_generations = accept_all_generations

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
        return population_ranked[0: int(self.survivor_ratio * self.population_size)]     # slice operation

    def _mix_strategies(self, parent1, parent2) -> AI:
        child_strategy = (parent1.strategy + parent2.strategy) / 2.0
        return AI("", self.group_size - 1, child_strategy)

    def _recombine(self, population) -> List[AI]:
        children = []
        children_count = int((self.population_size - len(population)) * self.child_ratio)         # = 25 (default value)
        for child_index in range(children_count):                                                     # build pairs
            child = self._mix_strategies(population[child_index * 2], population[child_index * 2 + 1])
            children.append(child)
        population.extend(children)
        return population

    def _mutate_strategy(self, ai) -> AI:
        for value_index in range(len(ai.strategy)):
            if random.random() < self.mutation_rate:
                ai.strategy[value_index] = random.random()
        return ai

    def _mutate(self, population) -> List[AI]:
        mutated_population = []
        for ai in population:
            mutated_population.append(self._mutate_strategy(ai))
        return mutated_population

    def _add_random_ais(self, population) -> List[AI]:
        missing_ais = self.population_size - len(population)
        population.extend(
            [AI("", self.group_size - 1, np.random.rand(self.group_size * 9)) for _ in range(missing_ais)])
        return population

    def _find_max_points(self, population):
        max_points = -100
        for ai in population:
            max_points = max(ai.get_points(), max_points)
        return max_points

    def _find_avg_points(self,population):
        sum_points = 0
        for ai in population:
            sum_points += ai.get_points()
        return sum_points / self.population_size

    def _compute_next_generation(self, population) -> List[AI]:
        population = self._select(population)
        population = self._recombine(population)
        population = self._mutate(population)
        population = self._add_random_ais(population)
        population = self._group(population)
        population = self._rank(population)
        return population

    def _build_initial_population(self) -> List[AI]:
        return [AI("", self.group_size - 1, np.random.rand(self.group_size * 9)) for _ in range(self.population_size)]
        # return [AI("", self.group_size - 1,np.zeros((self.group_size * 9,))) for _ in range(self.population_size)]

    def train(self) -> AI:
        population = self._build_initial_population()
        population = self._group(population)
        population = self._rank(population)
        avg_points = float("-inf")
        for generation in range(self.generations):
            new_population = self._compute_next_generation(population)
            max_points = self._find_max_points(new_population)
            new_avg_points = self._find_avg_points(new_population)
            if new_avg_points > avg_points or self.accept_all_generations:
                avg_points = new_avg_points
                population = new_population
            print("Generation: {} \t Max: {} \t Avg: {}".format(generation, max_points, avg_points))
        print("evolution finished")
        best_ai = population[0]
        return best_ai


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()
