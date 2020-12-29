"""This file creates a trainer that finds the best (fittest) AI"""
from ai_player import AiPlayer
from game import Game, SampleStrategies
import numpy as np
from numpy import random
import random
from typing import List
import pickle
from copy import copy, deepcopy


class AiLogEntry:
    """data to track evolution of AIs across generations during training"""
    def __init__(self, points_average, points_variance, events):
        self.points_average = points_average
        self.points_variance = points_variance
        self.events = events

    def __repr__(self):
        return "(" + str(self.points_average) + ", " + str(self.points_variance) + ", " + str(self.events) + ")"


class Trainer:
    """trains AIs (with a genetic algorithm) in order to get the best AI out of all;
    7 parameters therefore given manually"""

    strategy_parameter_min = -10
    strategy_parameter_max = 10

    def __init__(self, group_size=5, population_size=100, survivor_rate=0.74, child_rate=1, mutation_rate=0.05,
                 mutation_copy_rate=0, lowest_variance_rate=0.95, num_generations=100):
        assert (population_size % group_size == 0)
        self.group_size = group_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_copy_rate = mutation_copy_rate
        self.lowest_variance_rate = lowest_variance_rate
        self.num_generations = num_generations
        self.num_survivors = int(survivor_rate * self.population_size)
        self.num_children = int((self.population_size - self.num_survivors) * child_rate) # child_rate is relative amount of died AIs that is 'reborn' by recombination
        self.num_parents = self.num_children * 2
        self.fitness_game_number = 1   # empiric value
        self.points_per_ai = None
        self.ai_histories = dict()
        self.generation = 0
        self.population = []

    def _group(self) -> List[List[AiPlayer]]:
        """puts the individuals (AIs) of a population into random groups of the same size"""
        random.shuffle(self.population)
        groups = []
        for ai_index in range(0, len(self.population), self.group_size):
            groups.append(self.population[ai_index: ai_index + self.group_size])
        return groups

    def _select_extreme_ais(self, point_sum_per_ai, num_extreme_ais, selects_best_ais, variance_threshold) -> List[AiPlayer]:
        """selects strongest or weakest AIs of a population"""
        extreme_ais = []
        for _ in range(num_extreme_ais):
            max_points = float("-inf")
            min_points = float("inf")
            extreme_ai = None
            for ai, points in point_sum_per_ai.items():
                if self.ai_histories[ai][self.generation].points_variance > variance_threshold:
                    continue    # ignore AIs with high points variance in ranking -> middle field (extreme good/bad daily form)
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

    def _compute_avg_points_per_ai(self, point_sum_per_ai, point_list_per_ai) -> None:
        """creates a dictionary with average points of every AI"""
        self.points_per_ai = dict()
        for ai, points in point_sum_per_ai.items():
            self.points_per_ai[ai] = int(points / self.fitness_game_number)
            points_variance = Trainer._compute_variance(point_list_per_ai, self.points_per_ai[ai])
            if self.generation in self.ai_histories[ai]:
                self.ai_histories[ai][self.generation].points_average = self.points_per_ai[ai]
                self.ai_histories[ai][self.generation].points_variance = points_variance
            else:
                self.ai_histories[ai][self.generation] = AiLogEntry(self.points_per_ai[ai], points_variance, [])

    @staticmethod
    def _compute_variance(numbers, average) -> int:
        """calculates the corrected sample variance of any list of numbers with a given average"""
        variance = 0                            # korrigierte Stichprobenvarianz
        for number in numbers:
            variance += (number - average) ** 2
        return int(variance / len(numbers))

    def _play_in_groups(self, point_sum_per_ai, point_list_per_ai) -> None:
        """part of _rank(); lets AIs play in groups"""
        groups = self._group()
        for group in groups:
            game = Game(group)
            game.play()
            for ai in group:
                points = ai.get_points()
                point_sum_per_ai[ai] += points
                point_list_per_ai.append(points)

    def _split_ais_by_fitness(self, point_sum_per_ai):
        """part of _rank(); splits AIs by fitness after playing in groups"""
        variances = []
        for ai in self.population:
            variances.append(self.ai_histories[ai][self.generation].points_variance)
        variance_threshold = list(sorted(variances))[int(self.lowest_variance_rate * self.population_size) - 1]
        # todo calculate variance_th in extra function
        point_sum_per_ai_temp = copy(point_sum_per_ai)
        strongest_ais = self._select_extreme_ais(point_sum_per_ai_temp, self.num_parents,
                                                    True, variance_threshold)  # side-effect intentional
        weakest_ais = self._select_extreme_ais(point_sum_per_ai_temp, self.population_size - self.num_survivors,
                                                  False, variance_threshold)
        weakest_ais = list(reversed(weakest_ais))
        middle_field = point_sum_per_ai_temp.keys()  # keys() only selects the AIs, not the points
        return strongest_ais, middle_field, weakest_ais

    def _create_ranking(self, point_sum_per_ai):
        """part of _rank(); creates a ranking based on the fitness of an AI"""
        strongest_ais, middle_field, weakest_ais = self._split_ais_by_fitness(point_sum_per_ai)
        ranking = copy(strongest_ais)
        ranking.extend(middle_field)
        ranking.extend(weakest_ais)
        assert (len(ranking) == self.population_size)
        return ranking

    def _rank(self) -> None:
        """lets the groups play and ranks them inside these groups by performance"""
        point_sum_per_ai = dict()
        point_list_per_ai = dict()
        for ai in self.population:
            point_sum_per_ai[ai] = 0
            point_list_per_ai = []

        for game_count in range(self.fitness_game_number):
            self._play_in_groups(point_sum_per_ai, point_list_per_ai)
        self._compute_avg_points_per_ai(point_sum_per_ai, point_list_per_ai)
        self.population = self._create_ranking(point_sum_per_ai)

    def _select(self) -> None:
        """selects the best AIs, these survive -> rate of survivors given by parameter"""
        dead_ais = self.population[self.num_survivors:]
        for ai in dead_ais:
            self._add_event_to_ai_history(ai, "SELEction")
        self.population = self.population[: self.num_survivors]

    def _mix_strategies(self, parent1, parent2) -> AiPlayer:
        """mixes the strategies of the parents by creating averages of the different factors / bias to be their child's
         strategy"""
        child_quadratic_factor = np.array([x / 2 for x in (parent1.quadratic_factor + parent2.quadratic_factor)])
        child_linear_factor = np.array([x / 2 for x in (parent1.linear_factor + parent2.linear_factor)])
        child_bias = np.array([x / 2 for x in (parent1.bias + parent2.bias)])
        assert (len(child_linear_factor) == len(parent1.linear_factor) and len(child_linear_factor) == len(
            parent2.linear_factor))
        self._add_event_to_ai_history(parent1, "PAREnt")
        self._add_event_to_ai_history(parent2, "PAREnt")
        ai_number = len(self.ai_histories)
        return AiPlayer(str(ai_number), child_quadratic_factor, child_linear_factor, child_bias)

    def _add_event_to_ai_history(self, ai, event) -> None:
        if self.generation in self.ai_histories[ai]:
            self.ai_histories[ai][self.generation].events.append(event)
        else:
            self.ai_histories[ai][self.generation] = AiLogEntry(None, None, [event])

    def _recombine(self) -> None:
        """extends the population by children that are created by recombination of their parents strategies"""
        children = []
        for child_index in range(self.num_children):  # build pairs
            child = self._mix_strategies(self.population[child_index * 2], self.population[child_index * 2 + 1])
            children.append(child)
            self.ai_histories[child] = dict()
            self._add_event_to_ai_history(child, "RECOmbination")
        self.population.extend(children)
        assert(len(self.population) <= self.population_size)

    def _mutate_strategy(self, ai) -> int:
        """mutates randomly small parts of the strategy of an AI"""
        mutation_counter = 0
        for value_index in range(AiPlayer.strategy_length):
            if random.random() < self.mutation_rate:
                ai.quadratic_factor[value_index] = Trainer._adjust_strategy_range(random.random())
                mutation_counter += 1
            if random.random() < self.mutation_rate:
                ai.linear_factor[value_index] = Trainer._adjust_strategy_range(random.random())
                mutation_counter += 1
            if random.random() < self.mutation_rate:
                ai.bias[value_index] = Trainer._adjust_strategy_range(random.random())
                mutation_counter += 1
        return mutation_counter                 # call by reference on ai (pointer)

    def _mutate(self) -> None:
        """creates a list of mutated AIs"""
        copied_ais = []
        max_copies = (self.population_size - len(self.population)) * self.mutation_copy_rate
        for ai in self.population:
            ai_copy = deepcopy(ai)
            ai_number = len(self.ai_histories)
            ai_copy.name = str(ai_number)
            ai_history_copy = deepcopy(self.ai_histories[ai])
            mutation_counter = self._mutate_strategy(ai)
            if mutation_counter > 0:
                self._add_event_to_ai_history(ai, f"MUTAtion, {mutation_counter}")
                if len(copied_ais) < max_copies:
                    copied_ais.append(ai_copy)
                    self.ai_histories[ai_copy] = ai_history_copy
                    self._add_event_to_ai_history(ai_copy, f"COPY from {ai}")
        self.population.extend(copied_ais)
        assert (len(self.population) <= self.population_size)

    def _add_random_ais(self) -> None:
        """adds random AIs to the population in order to reach the original population size"""
        missing_ais = self.population_size - len(self.population)
        ais = []
        for ai_number in range(len(self.ai_histories), len(self.ai_histories) + missing_ais):
            # ai = AiPlayer(str(ai_number), Trainer._build_random_strategy(),
                          # Trainer._build_random_strategy(), Trainer._build_random_strategy())
            ai = AiPlayer(str(ai_number), SampleStrategies.bodo_quadratic_factor,
                          SampleStrategies.bodo_linear_factor, SampleStrategies.bodo_bias)
            self.ai_histories[ai] = dict()
            self._add_event_to_ai_history(ai, "INITialization")
            ais.append(ai)
        self.population.extend(ais)
        assert (len(self.population) <= self.population_size)

    def _find_strongest_ai(self):
        """finds the highest scoring ai in a population"""
        max_points = float("-inf")
        strongest_ai = None
        for ai in self.population:
            if max_points < self.points_per_ai[ai]:
                max_points = self.points_per_ai[ai]
                strongest_ai = ai
        return strongest_ai, max_points

    def _compute_points_statistics(self):
        """calculates the average points that were scored in a generation"""
        sum_points = 0
        for ai in self.population:
            sum_points += self.points_per_ai[ai]
        avg_points = int(sum_points / self.population_size)

        var_points = Trainer._compute_variance(self.points_per_ai.values(), avg_points)
        return avg_points, var_points

    def _compute_next_generation(self) -> None:
        """directs all steps that have to be done to create the next generation / a (partly) new population"""
        self._select()
        self._recombine()
        self._mutate()    # &[(index, self.ai_histories[ai],ai) for (index, ai) in enumerate(population)]
        self._add_random_ais()
        self._rank()  # [(index, ai, list(reversed(list(self.ai_histories[ai].items())))) for (index, ai) in enumerate(population)]

    @staticmethod
    def _build_random_strategy():
        """builds any part of strategy (quadratic, linear, bias)"""
        return Trainer._adjust_strategy_range(np.random.rand(AiPlayer.strategy_length))

    @staticmethod
    def _adjust_strategy_range(array_or_value):
        width = Trainer.strategy_parameter_max - Trainer.strategy_parameter_min
        return array_or_value * width + Trainer.strategy_parameter_min

    def train(self, load_population_from_file, save_population_in_file) -> None:
        """trains the AIs due to the parameters and returns the final and best AI"""
        if load_population_from_file:
            self._load_population()
        else:
            assert(self.generation == 0 and self.population == [])
            self._add_random_ais()
            self._rank()         # todo generation 0 two times -> only one time

        stop_generation = self.num_generations + self.generation
        while self.generation < stop_generation:
            self._compute_next_generation()
            _, max_points = self._find_strongest_ai()
            avg_points, variance = self._compute_points_statistics()
            print(f"Generation: {self.generation} \t Max: {max_points} \t Avg: {avg_points} \t Var: {variance}")
            self.generation += 1
        print("evolution finished")
        # best_ai, _ = self._find_strongest_ai(population)
        if save_population_in_file:
            self._save_final_population()

    def _save_final_population(self) -> None:
        """saves the final population of a train cycle """
        pickle.dump((self.population, self.ai_histories, self.generation), open("final_population.dat", "wb"))  # todo date in name

    def _load_population(self) -> None:
        """loads the population that was saved"""
        file = open("final_population.dat", "rb")
        self.population, self.ai_histories, self.generation = pickle.load(file)
        file.close()


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train(load_population_from_file=False, save_population_in_file=False)
