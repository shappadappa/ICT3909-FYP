"""
Chromosome  : list[Recipe] of length `meals_per_week` (default 21 = 3 meals × 7 days)
Selection   : tournament selection
Crossover   : single-point crossover (probability 0.8)
Mutation    : random meal swap (per-gene probability 0.1)
Elitism     : the best individual always survives to the next generation
"""

import random
from datetime import datetime

from models.Pantry import Pantry
from models.Recipe import Recipe
from models.UserPreferences import UserPreferences
from mock_data import INGREDIENT_UNIT_COSTS

class GAMealPlanner:
    def __init__(
        self,
        recipes: list[Recipe],
        pantry: Pantry,
        preferences: UserPreferences,
        current_date: datetime | None = None,
        population_size: int = 100,
        generations: int = 200,
        meals_per_week: int = 21,
        tournament_size: int = 5,
        crossover_prob: float = 0.8,
        mutation_rate: float = 0.10,
        seed: int | None = None,
    ):
        """
        A genetic algorithm engine for weekly meal planning optimisation

        A population of candidate meal plans (chromosomes) evolves to maximise a fitness score that rewards:
        - Using pantry ingredients that are close to expiring (expiry bonus)
        - Covering as many recipe ingredients as possible from existing stock (pantry score)
        and penalises:
        - Leaving expiring pantry ingredients unused at week's end (waste penalty)
        - Exceeding the user's weekly grocery budget (budget penalty)
        - Meals that violate the user's dietary preferences (dietary penalty)

        :param recipes: pool of recipes the GA can select from
        :type recipes: list[Recipe]
        :param pantry: current pantry state
        :type pantry: Pantry
        :param preferences: user dietary and budget constraints
        :type preferences: UserPreferences
        :param current_date: simulation date (default = datetime.now())
        :type current_date: datetime | None
        :param population_size: number of chromosomes per generation (default = 100)
        :type population_size: int
        :param generations: number of evolution generations (default = 200)
        :type generations: int
        :param meals_per_week: chromosome length, number of meals to plan for the week (default = 21)
        :type meals_per_week: int
        :param tournament_size: number of competitors in each tournament round (default = 5)
        :type tournament_size: int
        :param crossover_prob: probability of applying crossover vs cloning parents (default = 0.8)
        :type crossover_prob: float
        :param mutation_rate: per-gene probability of random meal replacement (default = 0.1)
        :type mutation_rate: float
        :param seed: optional random seed for reproducibility
        :type seed: int | None
        """

        self.recipes = recipes
        self.pantry = pantry
        self.preferences = preferences
        self.current_date = current_date or datetime.now()
        self.population_size = population_size
        self.generations = generations
        self.meals_per_week = meals_per_week
        self.tournament_size = tournament_size
        self.crossover_prob = crossover_prob
        self.mutation_rate = mutation_rate

        if seed is not None:
            random.seed(seed)

        # pre-computing pantry metadata
        self._pantry_stock: dict[str, int] = {
            ing.name: ing.quantity for ing in self.pantry.ingredients
        }

        self._days_until_expiry: dict[str, int] = {
            ing.name: (ing.estimated_expiration_date - self.current_date).days for ing in self.pantry.ingredients
        }

    def _create_chromosome(self) -> list[Recipe]:
        """
        Creates a random meal plan (chromosone) by sampling recipes uniformly at random from the pool

        :return: a list of `meals_per_week` recipes
        :rtype: list[Recipe]
        """

        return [random.choice(self.recipes) for _ in range(self.meals_per_week)]

    def _initialise_population(self) -> list[list[Recipe]]:
        """
        Initialises the GA population with random meal plans

        :return: list of meal plans (chromosomes), each a list of `meals_per_week` recipes
        :rtype: list[list[Recipe]]
        """

        return [self._create_chromosome() for _ in range(self.population_size)]

    # fitness function helpers
    def _dietary_penalty_for(self, recipe: Recipe) -> float:
        """
        Returns a penalty score for a recipe that violates the user's dietary preferences

        ? Should the penalty be a parameter to the class, showing the user's relative weighting of dietary compliance vs other factors? For now it's a fixed large penalty to strongly discourage non-compliant meals

        :param recipe: the recipe to evaluate
        :type recipe: Recipe

        :return: penalty score (0 if compliant)
        :rtype: float
        """
       
        penalty = 0.0

        if self.preferences.is_vegan and not recipe.is_vegan:
            penalty += 50
        if self.preferences.is_vegetarian and not recipe.is_vegetarian:
            penalty += 50
        if self.preferences.requires_gluten_free and not recipe.is_gluten_free:
            penalty += 50
        if self.preferences.requires_lactose_free and not recipe.is_lactose_free:
            penalty += 50

        return penalty

    def _expiry_bonus_for(self, ing_name: str, qty: int) -> float:
        """
        Returns a bonus score for using `qty` units of an ingredient that is close to expiring

        ! These weights should be tuned eventually

        :param ing_name: name of the ingredient
        :type ing_name: str
        :param qty: quantity of the ingredient used in the meal plan
        :type qty: int

        :return: bonus score (higher for more urgent expiring items)
        :rtype: float
        """

        days_left = self._days_until_expiry.get(ing_name, 999)

        if days_left <= 1:
            return qty * 30
        if days_left <= 3:
            return qty * 20
        if days_left <= 7:
            return qty * 10
        
        return 0.0

    def _consume_ingredient(
        self,
        ing_name: str,
        qty_needed: int,
        consumed: dict[str, int],
    ) -> tuple[int, float, float]:
        """
        Attempts to fill `qty_needed` units from pantry stock, buying the shortfall

        :param ing_name: name of the ingredient
        :type ing_name: str
        :param qty_needed: quantity of the ingredient required by the recipe
        :type qty_needed: int
        :param consumed: dict tracking how many units of each ingredient have been consumed from the pantry so far
        :type consumed: dict[str, int]

        :return: tuple of (units taken from pantry, expiry bonus for those units, additional cost incurred by buying shortfall)
        :rtype: tuple[int, float, float]
        """

        available = self._pantry_stock.get(ing_name, 0) - consumed.get(ing_name, 0)

        if available >= qty_needed:
            consumed [ing_name] = consumed.get(ing_name, 0) + qty_needed
            return qty_needed, self._expiry_bonus_for(ing_name, qty_needed), 0.0

        from_pantry = max(0, available)
        to_buy = qty_needed - from_pantry
        consumed [ing_name] = consumed.get(ing_name, 0) + from_pantry
        cost = to_buy * INGREDIENT_UNIT_COSTS.get(ing_name, 1.0)

        return from_pantry, 0.0, cost

    def _waste_penalty(self, consumed: dict[str, int]) -> float:
        """
        Penalty for expiring ingredients left unused at the end of the week
        
        :param consumed: dict tracking how many units of each ingredient have been consumed from the pantry
        :type consumed: dict[str, int]

        :return: penalty score (higher for more unused urgent expiring items)
        :rtype: float
        """

        penalty = 0.0

        for ing in self.pantry.ingredients:
            days_left = self._days_until_expiry.get(ing.name, 999)

            if days_left > 7:
                continue

            qty_unused = max(0, ing.quantity - consumed.get(ing.name, 0))

            if qty_unused > 0:
                urgency = max(1, 8 - days_left)
                penalty += qty_unused * urgency * 5

        return penalty

    def calculate_fitness(self, chromosome: list[Recipe]) -> float:
        """
        Evaluates a meal plan chromosome and return its fitness score.

        :param chromosome: list of recipes representing a weekly meal plan
        :type chromosome: list[Recipe]

        :return: fitness score (higher is better)
        :rtype: float
        """

        consumed: dict[str, int] = dict.fromkeys(self._pantry_stock, 0)
        total_units_needed = 0
        total_units_from_pantry = 0
        expiry_bonus = 0.0
        dietary_penalty = 0.0
        additional_purchase_cost = 0.0

        for recipe in chromosome:
            dietary_penalty += self._dietary_penalty_for(recipe)

            for ing_name, qty_needed in recipe.ingredients.items():
                total_units_needed += qty_needed
                from_pantry, bonus, cost = self._consume_ingredient(ing_name, qty_needed, consumed)
                total_units_from_pantry += from_pantry
                expiry_bonus += bonus
                additional_purchase_cost += cost

        pantry_score = (
            total_units_from_pantry / total_units_needed * 100
            if total_units_needed > 0
            else 0.0
        )
        
        waste_penalty = self._waste_penalty(consumed)
        budget_penalty = max(0.0, additional_purchase_cost - self.preferences.weekly_budget) * 10

        return pantry_score + expiry_bonus - waste_penalty - budget_penalty - dietary_penalty

    # genetic operators

    def _tournament_selection(self, population: list[list[Recipe]], fitnesses: list[float]) -> list[Recipe]:
        """
        Selects a chromosome from the population using tournament selection

        :param population: list of meal plan chromosomes
        :type population: list[list[Recipe]]
        :param fitnesses: pre-computed fitness scores for the population
        :type fitnesses: list[float]

        :return: selected chromosome (meal plan)
        :rtype: list[Recipe]
        """

        idx = random.sample(range(len(population)), self.tournament_size)
        best = max(idx, key = lambda i: fitnesses[i])
        return population [best] [:]

    def _crossover(self, parent1: list[Recipe], parent2: list[Recipe]) -> tuple[list[Recipe], list[Recipe]]:
        """
        Performs single-point crossover between two parent chromosomes with probability `crossover_prob`, otherwise returns clones of the parents

        :param parent1: first parent chromosome
        :type parent1: list[Recipe]
        :param parent2: second parent chromosome
        :type parent2: list[Recipe]

        :return: tuple of two child chromosomes resulting from crossover (or clones of the parents)
        :rtype: tuple[list[Recipe], list[Recipe]]
        """

        if random.random() < self.crossover_prob:
            point = random.randint(1, self.meals_per_week - 1)
            return parent1 [:point] + parent2 [point:], parent2 [:point] + parent1 [point:]
        
        return parent1 [:], parent2 [:]

    def _mutate(self, chromosome: list[Recipe]) -> list[Recipe]:
        """
        Randomly mutates a chromosome by replacing individual meals with random recipes from the pool with probability `mutation_rate`

        :param chromosome: the meal plan chromosome to mutate
        :type chromosome: list[Recipe]

        :return: mutated chromosome
        :rtype: list[Recipe]
        """
        
        return [
            random.choice(self.recipes) if random.random() < self.mutation_rate else meal
            for meal in chromosome
        ]

    def run(self) -> tuple[list[Recipe], float, list[dict]]:
        """
        Executes the genetic algorithm

        :return: tuple of (best meal plan found, its fitness score, history of best and average fitness per generation)
        :rtype: tuple[list[Recipe], float, list[dict]]
        """

        population = self._initialise_population()
        best_chromosome: list[Recipe] = []
        best_fitness = float("-inf")
        history: list[dict] = []

        for generation in range(self.generations):
            fitnesses = [self.calculate_fitness(chrom) for chrom in population]

            gen_best_idx = max(range(len(fitnesses)), key = lambda i, f = fitnesses: f[i])
            gen_best_fitness = fitnesses[gen_best_idx]

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_chromosome = population[gen_best_idx][:]

            avg_fitness = sum(fitnesses) / len(fitnesses)
            history.append(
                {
                    "generation": generation,
                    "best_fitness": best_fitness,
                    "avg_fitness": avg_fitness,
                }
            )

            # builds next generation with elitism (keep best individual)
            new_population: list[list[Recipe]] = [population [gen_best_idx] [:]]

            while len(new_population) < self.population_size:
                p1 = self._tournament_selection(population, fitnesses)
                p2 = self._tournament_selection(population, fitnesses)
                c1, c2 = self._crossover(p1, p2)
                new_population.append(self._mutate(c1))
                new_population.append(self._mutate(c2))

            population = new_population[: self.population_size]

        return best_chromosome, best_fitness, history

    def print_meal_plan(self, plan: list[Recipe]) -> None:
        """
        Prints the meal plan in a readable format

        :param plan: list of recipes representing the meal plan
        :type plan: list[Recipe]
        """
        
        day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"]
        meal_labels = ["Breakfast", "Lunch", "Dinner"]
        days = self.meals_per_week // 3

        print("=" * 50)
        print("          OPTIMISED WEEKLY MEAL PLAN")
        print("=" * 50)
        for day in range(days):
            print(f"\n  {day_labels[day]}")
            print("  " + "-" * 30)
            for meal in range(3):
                recipe = plan[day * 3 + meal]
                print(f"    {meal_labels[meal]:10s} → {recipe.name}")
        print("\n" + "=" * 50)

    def summarise_pantry_usage(self, plan: list[Recipe]) -> dict:
        """
        Computes how much of each pantry ingredient is consumed by the plan and how much (if any) would expire unused

        :param plan: list of recipes representing the meal plan
        :type plan: list[Recipe]

        :return: dict mapping ingredient name to usage summary (available, consumed, unused, days until expiry, expires this week)
        :rtype: dict[str, dict]
        """

        consumed: dict[str, int] = dict.fromkeys(self._pantry_stock, 0)

        for recipe in plan:
            for ing_name, qty_needed in recipe.ingredients.items():
                available = self._pantry_stock.get(ing_name, 0) - consumed.get(ing_name, 0)
                take = min(qty_needed, max(0, available))
                consumed[ing_name] = consumed.get(ing_name, 0) + take

        summary = {}
        for ing in self.pantry.ingredients:
            days = self._days_until_expiry[ing.name]
            summary [ing.name] = {
                "available": ing.quantity,
                "consumed": consumed.get(ing.name, 0),
                "unused": max(0, ing.quantity - consumed.get(ing.name, 0)),
                "days_until_expiry": days,
                "expires_this_week": days <= 7,
            }
        return summary
