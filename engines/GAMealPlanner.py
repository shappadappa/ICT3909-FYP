from pygad import GA

from engines.fitness_score import fitness_score
from engines.MealPlanner import MealPlanner
from models import MealPlanningEnvironment


class GAMealPlanner(MealPlanner):
    def __init__(
        self,
        meal_planning_environment: MealPlanningEnvironment,
        pantry_weight: float = 1.0,
        waste_weight: float = 1.0,
        budget_weight: float = 1.0,
        dietary_weight: float = 1.0,
    ):
        """
        The `GAMealPlanner` class supports a genetic-algorithm-based meal planner that optimises meal plans based on dietary compliance, ingredient expiry, waste reduction, and budget adherence

        :meal_planning_environment: the meal planning environment containing recipes, pantry stock, and user preferences
        :type meal_planning_environment: MealPlanningEnvironment
        :param pantry_weight: importance weight for the pantry utilisation reward, in [0, 1] (default = 1.0)
        :type pantry_weight: float
        :param waste_weight: importance weight for the food waste penalty, in [0, 1] (default = 1.0)
        :type waste_weight: float
        :param budget_weight: importance weight for the budget overspend penalty, in [0, 1] (default = 1.0)
        :type budget_weight: float
        :param dietary_weight: importance weight for the dietary target penalty, in [0, 1] (default = 1.0)
        :type dietary_weight: float
        """

        super().__init__(meal_planning_environment)

        self.pantry_weight = pantry_weight
        self.waste_weight = waste_weight
        self.budget_weight = budget_weight
        self.dietary_weight = dietary_weight

        self.recipe_calories = [recipe.nutritional_information.calories or 0.0 for recipe in self.recipes]
        self.recipe_protein = [recipe.nutritional_information.protein or 0.0 for recipe in self.recipes]

    def generate_meal_plan(
        self,
        num_days: int = 7,
        meals_per_day: int = 3,
        num_generations: int = 1000,
        num_parents_mating: int = 20,
        population_size: int = 100,
        parent_selection_type: str = "tournament",
        K_tournament: int = 5,
        keep_elitism: int = 1,
        crossover_type: str = "single_point",
        crossover_probability: float = 0.8,
        mutation_type: str = "random",
        mutation_probability: float = 0.1,
        generation_print_interval: int | None = 10,
        seed: int | None = 1,
    ) -> tuple[list[int], float]:
        """
        Runs the genetic algorithm to find an optimised meal plan

        :param num_days: number of days to plan meals for
        :type num_days: int
        :param meals_per_day: number of meals per day
        :type meals_per_day: int
        :param num_generations: number of GA generations to run
        :type num_generations: int
        :param num_parents_mating: number of parents selected for mating each generation
        :type num_parents_mating: int
        :param population_size: number of solutions in the population
        :type population_size: int
        :param parent_selection_type: parent selection method (e.g. "tournament", "sss", "rws", "sus", "random")
        :type parent_selection_type: str
        :param K_tournament: number of solutions competing in each tournament (only used when parent_selection_type="tournament")
        :type K_tournament: int
        :param keep_elitism: number of best solutions to carry over unchanged each generation
        :type keep_elitism: int
        :param crossover_type: crossover method (e.g. "single_point", "two_points", "uniform", "scattered")
        :type crossover_type: str
        :param crossover_probability: probability of crossover occurring for each pair of parents
        :type crossover_probability: float
        :param mutation_type: mutation method (e.g. "random", "swap", "inversion", "scramble", "adaptive")
        :type mutation_type: str
        :param mutation_probability: probability of mutating each gene
        :type mutation_probability: float
        :param generation_print_interval: how often (in generations) to print progress; None to disable
        :type generation_print_interval: int | None
        :param seed: random seed for reproducibility
        :type seed: int | None

        :return: tuple of (best meal plan as a list of recipe indices, best fitness score)
        :rtype: tuple[list[int], float]
        """

        num_genes = num_days * meals_per_day

        def fitness_function(_ga_instance, solution, _solution_index):
            return fitness_score(
                recipe_indices=solution,
                recipes=self.recipes,
                pantry_stock=self.pantry_stock,
                days_until_expiry=self.days_until_expiry,
                ingredient_costs=self.ingredient_costs,
                weekly_budget=self.preferences.weekly_budget,
                calorie_target_per_day=self.preferences.calorie_target_per_day,
                protein_target_per_day=self.preferences.protein_target_per_day,
                pantry_weight=self.pantry_weight,
                waste_weight=self.waste_weight,
                budget_weight=self.budget_weight,
                dietary_weight=self.dietary_weight,
                recipe_calories=self.recipe_calories,
                recipe_protein=self.recipe_protein,
            )

        def on_generation(ga_instance):
            if generation_print_interval is None:
                return

            if generation_print_interval > 0 and ga_instance.generations_completed % generation_print_interval == 0:
                best_fitness = ga_instance.best_solution()[1]
                print(f"Generation {ga_instance.generations_completed}, Best Fitness: {best_fitness:.2f}")

        ga_instance = GA(
            num_generations=num_generations,
            num_parents_mating=num_parents_mating,
            fitness_func=fitness_function,
            sol_per_pop=population_size,
            num_genes=num_genes,
            gene_type=int,
            gene_space=list(range(len(self.recipes))),
            parent_selection_type=parent_selection_type,
            K_tournament=K_tournament,
            keep_elitism=keep_elitism,
            crossover_type=crossover_type,
            crossover_probability=crossover_probability,
            mutation_type=mutation_type,
            mutation_probability=mutation_probability,
            on_generation=on_generation,
            random_seed=seed,
        )

        ga_instance.run()

        self.best_meal_plan, self.best_fitness, _ = ga_instance.best_solution()

        return list(self.best_meal_plan), float(self.best_fitness)
