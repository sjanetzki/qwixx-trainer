"""This file creates a trainer that finds the best (fittest) AI"""
from ai_player import AiPlayer
from game import Game
import numpy as np
from numpy import random
import random
from typing import List
import pickle


class Trainer:
    """trains AIs (with a genetic algorithm) in order to get the best AI out of all;
    7 parameters therefore given manually"""
   # bodo_quadratic_factor = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
   # bodo_linear_factor = np.array([1, -0.5, 1, -0.5, 1, 0.5, 1, 0.5, -2.5])
   # bodo_bias = np.array([0, 0, 0, 0, 0, -6, 0, -6, 0])

    caira_quadratic_factor = np.array([0.5, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0])
    caira_linear_factor = np.array([0.5, 0, 0.5, 0, 0.5, 0, 0.5, 0, -5])
    caira_bias = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

    def __init__(self, group_size=2, population_size=10, survivor_rate=0.95, child_rate=0.5, mutation_rate=0.005,
                 generations=10):
        self.group_size = group_size
        self.population_size = population_size
        self.survivor_rate = survivor_rate
        self.child_rate = child_rate
        self.mutation_rate = mutation_rate
        self.generations = generations

    def _group(self, population) -> List[AiPlayer]:
        """puts the individuals (AIs) of a population into random groups of the same size"""
        random.shuffle(population)
        groups = []
        for ai_index in range(0, len(population), self.group_size):
            groups.append(population[ai_index: ai_index + self.group_size])
        return groups

    def _rank(self, groups) -> List[AiPlayer]:
        """lets the groups play and ranks them inside these groups by performance"""
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

    def _select(self, population_ranked) -> List[AiPlayer]:
        """selects the best AIs, these survive -> rate of survivors given by parameter"""
        return population_ranked[0: int(self.survivor_rate * self.population_size)]  # slice operation

    def _mix_strategies(self, parent1, parent2) -> AiPlayer:
        """mixes the strategies of the parents by creating averages of the different factors / bias to be their child's
         strategy"""
        child_quadratic_factor = np.array([x / 2 for x in (parent1.quadratic_factor + parent2.quadratic_factor)])
        child_linear_factor = np.array([x / 2 for x in (parent1.linear_factor + parent2.linear_factor)])
        child_bias = np.array([x / 2 for x in (parent1.bias + parent2.bias)])
        assert (len(child_linear_factor) == len(parent1.linear_factor) and len(child_linear_factor) == len(
            parent2.linear_factor))
        return AiPlayer("", self.group_size - 1, child_quadratic_factor, child_linear_factor, child_bias)

    def _recombine(self, population) -> List[AiPlayer]:
        """extends the population by children that are created by recombination of their parents strategies"""
        children = []
        children_count = int((self.population_size - len(population)) * self.child_rate)  # = 25 (default value)
        for child_index in range(children_count):  # build pairs
            child = self._mix_strategies(population[child_index * 2], population[child_index * 2 + 1])
            children.append(child)
        population.extend(children)
        return population

    def _mutate_strategy(self, ai) -> AiPlayer:
        """mutates randomly small parts of the strategy of an AI"""
        for value_index in range(len(ai.linear_factor)):
            if random.random() < self.mutation_rate:
                ai.quadratic_factor[value_index] = random.random()
            if random.random() < self.mutation_rate:
                ai.linear_factor[value_index] = random.random()
            if random.random() < self.mutation_rate:
                ai.bias[value_index] = random.random()
        return ai

    def _mutate(self, population) -> List[AiPlayer]:
        """creates a list of mutated AIs"""
        mutated_population = []
        for ai in population:
            self.append = mutated_population.append(self._mutate_strategy(ai))
        return mutated_population

    def _add_random_ais(self, population) -> List[AiPlayer]:
        """adds random AIs to the population in order to reach the original population size"""
        missing_ais = self.population_size - len(population)
        population.extend(
            [AiPlayer("", self.group_size - 1, Trainer.caira_quadratic_factor, Trainer.caira_linear_factor,
                      Trainer.caira_bias) for _ in range(missing_ais)])     # todo not caira
        # [AI("", self.group_size - 1, np.random.rand(self.group_size * 9)) for _ in range(missing_ais)])
        return population

    def _find_strongest_ai(self, population):
        """finds the highest scoring ai in a population"""
        max_points = float("-inf")
        strongest_ai = None
        for ai in population:
            if max_points < ai.get_points():
                max_points = ai.get_points()
                strongest_ai = ai
        return strongest_ai

    def _find_avg_points(self, population):
        """calculates the average points that were scored in an generation"""
        sum_points = 0
        for ai in population:
            sum_points += ai.get_points()
        return sum_points / self.population_size

    def _compute_next_generation(self, population) -> List[AiPlayer]:
        """directs all steps that have to be done to create the next generation / a (partly) new population"""
        population = self._select(population)
        population = self._recombine(population)
        population = self._mutate(population)
        population = self._add_random_ais(population)
        population = self._group(population)
        population = self._rank(population)
        return population

    def _build_initial_population(self) -> List[AiPlayer]:
        """builds the initial population as a list of AIs with random strategies"""
        # return [AI("", self.group_size - 1, np.random.rand(self.group_size * 9), random.randint(-1, 1))for _ in
        # range(self.population_size)]  # fill in linear_factor
        return [AiPlayer("", self.group_size - 1, Trainer.caira_quadratic_factor, Trainer.caira_linear_factor,
                         Trainer.caira_bias)
                for _ in range(self.population_size)]
        # return [AI("", self.group_size - 1, np.zeros((self.group_size * 9,)), random.randint(-1, 1)) for _ in
        # range(self.population_size)]

    def train(self) -> AiPlayer:
        """trains the AIs due to the parameters and returns the final and best AI"""
        population = self._build_initial_population()
        population = self._group(population)
        population = self._rank(population)
        for generation in range(self.generations):
            new_population = self._compute_next_generation(population)
            max_points = self._find_strongest_ai(new_population).get_points()
            new_avg_points = self._find_avg_points(new_population)
            avg_points = new_avg_points
            population = new_population
            print("Generation: {} \t Max: {} \t Avg: {}".format(generation, max_points, avg_points))
        print("evolution finished")
        best_ai = self._find_strongest_ai(population)
        self._save_best_ai(best_ai)
        return best_ai

    def _save_best_ai(self, best_ai):
        """saves the best AI of a train cycle """
        pickle.dump(best_ai, open("best_ai.dat", "wb"))        # todo date in name


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()
