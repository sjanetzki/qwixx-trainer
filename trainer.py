"""This file creates a trainer that finds the best (fittest) AI"""
from ai_player import AiPlayer
from game import Game
import numpy as np
from numpy import random
import random
from typing import List
import pickle
from copy import copy


class AiLogEntry:
    """data to track evolution of AIs across generations during training"""
    def __init__(self, points, events):
        self.points = points
        self.events = events

    def __repr__(self):
        return "(" + str(self.points) + ", " + str(self.events) + ")"


class Trainer:
    """trains AIs (with a genetic algorithm) in order to get the best AI out of all;
    7 parameters therefore given manually"""
   # bodo_quadratic_factor = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
   # bodo_linear_factor = np.array([1, -0.5, 1, -0.5, 1, 0.5, 1, 0.5, -2.5])
   # bodo_bias = np.array([0, 0, 0, 0, 0, -6, 0, -6, 0])

    # caira_quadratic_factor = np.array([0.5, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0])
    # caira_linear_factor = np.array([0.5, 0, 0.5, 0, 0.5, 0, 0.5, 0, -5])
    # caira_bias = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

    # caira_quadratic_factor = np.array([0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0])
    # caira_linear_factor = np.array([0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0.5, 0, 0, 0, -5])
    # caira_bias = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    strategy_parameter_min = -10
    strategy_parameter_max = 10

    def __init__(self, group_size=5, population_size=100, survivor_rate=0.67, child_rate=0.5, mutation_rate=0.01,
                 num_generations=200):
        self.group_size = group_size         # todo what if population_size not multiple of group_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.num_generations = num_generations
        self.num_survivors = int(survivor_rate * self.population_size)
        self.num_children = int((self.population_size - self.num_survivors) * child_rate) # child_rate is relative amount of died AIs that is 'reborn' by recombination
        self.num_parents = self.num_children * 2
        self.fitness_game_limit = 10   # empiric value
        self.points_per_ai = None
        self.ai_histories = dict()

    def _group(self, population) -> List[List[AiPlayer]]:
        """puts the individuals (AIs) of a population into random groups of the same size"""
        random.shuffle(population)
        groups = []
        for ai_index in range(0, len(population), self.group_size):
            groups.append(population[ai_index: ai_index + self.group_size])
        return groups

    def _select_extreme_ais(self, point_sum_per_ai, num_extreme_ais, selects_best_ais) -> List[AiPlayer]:
        """selects strongest or weakest AIs of a population"""
        extreme_ais = []
        for _ in range(num_extreme_ais):
            max_points = float("-inf")
            min_points = float("inf")
            extreme_ai = None
            for ai, points in point_sum_per_ai.items():
                if selects_best_ais and max_points < points:
                    max_points = points
                    extreme_ai = ai
                elif not selects_best_ais and min_points > points:
                    min_points = points
                    extreme_ai = ai
            extreme_ais.append(extreme_ai)
            del point_sum_per_ai[extreme_ai]
        assert(None not in extreme_ais)
        return extreme_ais

    def _compute_avg_points_per_ai(self, point_sum_per_ai, game_count, generation):
        """creates a dictionary with average points of every AI"""
        self.points_per_ai = dict()
        for ai, points in point_sum_per_ai.items():
            self.points_per_ai[ai] = int(points / game_count)
            if generation in self.ai_histories[ai]:
                self.ai_histories[ai][generation].points = self.points_per_ai[ai]
            else:
                self.ai_histories[ai][generation] = AiLogEntry(self.points_per_ai[ai], [])

    def _play_in_groups(self, population, point_sum_per_ai):
        """part of _rank(); lets AIs play in groups"""
        groups = self._group(population)
        for group in groups:
            game = Game(group)
            game.play()
            for ai in group:
                point_sum_per_ai[ai] += ai.get_points()

    def _split_ais_by_fitness(self, point_sum_per_ai):
        """part of _rank(); splits AIs by fitness after playing in groups"""
        point_sum_per_ai_temp = copy(point_sum_per_ai)
        strongest_ais = self._select_extreme_ais(point_sum_per_ai_temp, self.num_parents,
                                                 True)  # side-effect intentional
        weakest_ais = self._select_extreme_ais(point_sum_per_ai_temp, self.population_size - self.num_survivors, False)
        weakest_ais = reversed(weakest_ais)
        middle_field = point_sum_per_ai_temp.keys()  # keys() only selects the AIs, not the points
        return strongest_ais, middle_field, weakest_ais           # [(index, self.ai_histories[ai]) for (index, ai) in enumerate(weakest_ais)]

    def _create_ranking(self, point_sum_per_ai):
        """part of _rank(); creates a ranking based on the fitness of an AI"""
        strongest_ais, middle_field, weakest_ais = self._split_ais_by_fitness(point_sum_per_ai)
        ranking = copy(strongest_ais)
        ranking.extend(middle_field)
        ranking.extend(weakest_ais)
        assert (len(ranking) == self.population_size)
        return ranking, strongest_ais

    def _rank(self, population, generation) -> List[AiPlayer]:
        """lets the groups play and ranks them inside these groups by performance"""
        point_sum_per_ai = dict()
        last_strongest_ais = None
        ranking = None
        for ai in population:
            point_sum_per_ai[ai] = 0

        game_count = 0
        while game_count < self.fitness_game_limit:
            self._play_in_groups(population, point_sum_per_ai)
            game_count += 1
            ranking, strongest_ais = self._create_ranking(point_sum_per_ai)
            strongest_ais = set(strongest_ais)

            # check if strongest AIs are reliable
            if last_strongest_ais == strongest_ais:
                break

            last_strongest_ais = strongest_ais

        self._compute_avg_points_per_ai(point_sum_per_ai, game_count, generation)
        return ranking

    def _select(self, population_ranked, generation) -> List[AiPlayer]:
        """selects the best AIs, these survive -> rate of survivors given by parameter"""
        dead_ais = population_ranked[self.num_survivors:]
        for ai in dead_ais:
            self._add_event_to_ai_history(ai, generation, "SELEction")
        return population_ranked[: self.num_survivors]

    def _mix_strategies(self, parent1, parent2, generation) -> AiPlayer:
        """mixes the strategies of the parents by creating averages of the different factors / bias to be their child's
         strategy"""
        child_quadratic_factor = np.array([x / 2 for x in (parent1.quadratic_factor + parent2.quadratic_factor)])
        child_linear_factor = np.array([x / 2 for x in (parent1.linear_factor + parent2.linear_factor)])
        child_bias = np.array([x / 2 for x in (parent1.bias + parent2.bias)])
        assert (len(child_linear_factor) == len(parent1.linear_factor) and len(child_linear_factor) == len(
            parent2.linear_factor))
        self._add_event_to_ai_history(parent1, generation, "PAREnt")
        self._add_event_to_ai_history(parent2, generation, "PAREnt")
        ai_number = len(self.ai_histories)
        return AiPlayer(str(ai_number), self.group_size - 1, child_quadratic_factor, child_linear_factor, child_bias)

    def _add_event_to_ai_history(self, ai, generation, event):
        if generation in self.ai_histories[ai]:
            self.ai_histories[ai][generation].events.append(event)
        else:
            self.ai_histories[ai][generation] = AiLogEntry(None, [event])

    def _recombine(self, population, generation) -> List[AiPlayer]:
        """extends the population by children that are created by recombination of their parents strategies"""
        children = []
        for child_index in range(self.num_children):  # build pairs
            child = self._mix_strategies(population[child_index * 2], population[child_index * 2 + 1], generation)
            children.append(child)
            self.ai_histories[child] = dict()
            self._add_event_to_ai_history(child, generation, "RECOmbination")
        population.extend(children)
        return population

    def _mutate_strategy(self, ai) -> int:
        """mutates randomly small parts of the strategy of an AI"""
        mutation_counter = 0
        for value_index in range(len(ai.linear_factor)):
            if random.random() < self.mutation_rate:
                ai.quadratic_factor[value_index] = random.random()
                mutation_counter += 1
            if random.random() < self.mutation_rate:
                ai.linear_factor[value_index] = random.random()
                mutation_counter += 1
            if random.random() < self.mutation_rate:
                ai.bias[value_index] = random.random()
                mutation_counter += 1
        return mutation_counter                 # call by reference on ai (pointer)

    def _mutate(self, population, generation) -> List[AiPlayer]:
        """creates a list of mutated AIs"""
        for ai in population:
            mutation_counter = self._mutate_strategy(ai)
            if mutation_counter > 0:
                self._add_event_to_ai_history(ai, generation, "MUTAtion, {}".format(mutation_counter))
        return population               # was mutated by reference

    def _add_random_ais(self, population, generation) -> List[AiPlayer]:
        """adds random AIs to the population in order to reach the original population size"""
        missing_ais = self.population_size - len(population)
        ais = []
        for ai_number in range(len(self.ai_histories), len(self.ai_histories) + missing_ais):
            ai = AiPlayer(str(ai_number), self.group_size - 1, self._build_random_strategy(), self._build_random_strategy(),
                          self._build_random_strategy())
            self.ai_histories[ai] = dict()
            self._add_event_to_ai_history(ai, generation, "INITialization")
            ais.append(ai)

        population.extend(ais)
        return population

    def _find_strongest_ai(self, population):
        """finds the highest scoring ai in a population"""
        max_points = float("-inf")
        strongest_ai = None
        for ai in population:
            if max_points < self.points_per_ai[ai]:
                max_points = self.points_per_ai[ai]
                strongest_ai = ai
        return strongest_ai, max_points

    def _find_avg_points(self, population):
        """calculates the average points that were scored in a generation"""
        sum_points = 0
        for ai in population:
            sum_points += self.points_per_ai[ai]
        return int(sum_points / self.population_size)

    def _compute_next_generation(self, population, generation) -> List[AiPlayer]:
        """directs all steps that have to be done to create the next generation / a (partly) new population"""
        population = self._select(population, generation)
        population = self._recombine(population, generation)
        population = self._mutate(population, generation)
        population = self._add_random_ais(population, generation)
        population = self._rank(population, generation)
        return population

    def _build_random_strategy(self):
        """builds any part of strategy (quadratic, linear, bias)"""
        width = Trainer.strategy_parameter_max - Trainer.strategy_parameter_min
        return (np.random.rand(self.group_size * 9)) * width + Trainer.strategy_parameter_min

    def train(self) -> AiPlayer:
        """trains the AIs due to the parameters and returns the final and best AI"""
        population = self._add_random_ais([], 0)
        population = self._rank(population, 0)              # todo generation 0 two times -> only one time
        for generation in range(self.num_generations):
            new_population = self._compute_next_generation(population, generation)
            _, max_points = self._find_strongest_ai(new_population)
            new_avg_points = self._find_avg_points(new_population)
            avg_points = new_avg_points
            population = new_population
            print("Generation: {} \t Max: {} \t Avg: {}".format(generation, max_points, avg_points))
        print("evolution finished")
        best_ai, _ = self._find_strongest_ai(population)
        self._save_best_ai(best_ai)
        return best_ai

    def _save_best_ai(self, best_ai):
        """saves the best AI of a train cycle """
        pickle.dump(best_ai, open("best_ai.dat", "wb"))        # todo date in name


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()
