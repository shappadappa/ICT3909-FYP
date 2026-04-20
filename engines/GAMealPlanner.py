from datetime import datetime

import pandas as pd
from pygad import GA

from models import MealPlanningEnvironment


class GAMealPlanner:
    def __init__(
        self,
        meal_planning_environment: MealPlanningEnvironment,
        waste_penalty_multiplier: float = 0.001,
        panty_score_weight: float = 1.0,
        budget_penalty_multiplier: float = 2.0,
        calorie_penalty_weight: float = 0.01,
        protein_penalty_weight: float = 0.1,
    ):
        """
        The `GAMealPlanner` class supports a genetic-algorithm-based meal planner that optimises meal plans based on dietary compliance, ingredient expiry, waste reduction, and budget adherence

        :meal_planning_environment: the meal planning environment containing recipes, pantry stock, and user preferences
        :type meal_planning_environment: MealPlanningEnvironment
        :param waste_penalty_multiplier: multiplier for calculating the penalty score for leaving ingredients unused that are close to expiring (higher = less tolerance for waste; default = 0.001)
        :type waste_penalty_multiplier: float
        :param panty_score_weight: weight applied to the pantry score (higher = more importance; default = 1.0)
        :type panty_score_weight: float
        :param budget_penalty_multiplier: multiplier for calculating the penalty score for exceeding the budget (higher = worse; default = 2.0)
        :type budget_penalty_multiplier: float
        :param calorie_penalty_weight: weight applied to the absolute difference between daily calories and the calorie target (higher = stricter calorie adherence; default = 0.01)
        :type calorie_penalty_weight: float
        :param protein_penalty_weight: weight applied to the absolute difference between daily protein and the protein target (higher = stricter protein adherence; default = 0.1)
        :type protein_penalty_weight: float
        """

        self.meal_planning_environment = meal_planning_environment
        self.waste_penalty_urgency_multiplier = waste_penalty_multiplier
        self.panty_score_weight = panty_score_weight
        self.budget_penalty_multiplier = budget_penalty_multiplier
        self.calorie_penalty_weight = calorie_penalty_weight
        self.protein_penalty_weight = protein_penalty_weight

        self.recipes = self.meal_planning_environment.recipes
        self.pantry_stock = self.meal_planning_environment.pantry.stock
        self.days_until_expiry = self.meal_planning_environment.pantry.get_days_until_expiry(datetime.now())
        self.ingredient_costs = self.meal_planning_environment.pantry.ingredient_costs
        self.preferences = self.meal_planning_environment.preferences

    def generate_meal_plan(
        self,
        num_days: int = 7,
        meals_per_day: int = 3,
        num_generations: int = 1000,
        num_parents_mating: int = 20,
        population_size: int = 100,
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
        :param generation_print_interval: how often (in generations) to print progress; 0 to disable
        :type generation_print_interval: int

        :return: tuple of (best meal plan as a list of recipe indices, best fitness score)
        :rtype: tuple[list[int], float]
        """

        num_genes = num_days * meals_per_day

        def fitness_function(_ga_instance, solution, _solution_index):
            return self._evaluate_meal_plan(solution)

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
            parent_selection_type="tournament",
            K_tournament=5,
            keep_elitism=1,
            crossover_type="single_point",
            crossover_probability=0.8,
            mutation_type="random",
            mutation_probability=0.1,
            on_generation=on_generation,
            random_seed=seed,
        )

        ga_instance.run()

        self.best_meal_plan, self.best_fitness, _ = ga_instance.best_solution()

        return list(self.best_meal_plan), float(self.best_fitness)

    def get_pantry_consumption(self) -> pd.DataFrame:
        """
        Calculates how much of each pantry ingredient is consumed across the best meal plan, and returns a DataFrame showing available, consumed, and unused quantities along with days until expiry

        :return: DataFrame with columns "Ingredient", "Available", "Consumed", "Unused", and "Expires in"
        :rtype: pd.DataFrame
        """

        # going through the best meal plan and calculating how much of each ingredient is consumed from the pantry

        self.consumed_stock = dict.fromkeys(self.meal_planning_environment.pantry.stock.keys(), 0)

        for index in self.best_meal_plan:
            recipe = self.recipes[int(index)]

            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = self.pantry_stock.get(ingredient_name, 0) - self.consumed_stock.get(ingredient_name, 0)
                from_pantry = max(0, min(available, quantity_needed))
                self.consumed_stock[ingredient_name] = self.consumed_stock.get(ingredient_name, 0) + from_pantry

        pantry_data = []

        for ingredient in self.meal_planning_environment.pantry.ingredients:
            available = self.pantry_stock[ingredient.name]
            used = self.consumed_stock.get(ingredient.name, 0)
            unused = max(0, available - used)
            days = self.days_until_expiry[ingredient.name]
            expiry_str = str(days) + "d"
            pantry_data.append(
                {
                    "Ingredient": ingredient.name,
                    "Available": available,
                    "Consumed": used,
                    "Unused": unused,
                    "Expires in": expiry_str,
                }
            )

        pantry_data_df = pd.DataFrame(pantry_data)

        return pantry_data_df

    def get_shopping_list(self) -> tuple[pd.DataFrame, int, float]:
        """
        Generates a shopping list based on the best meal plan, considering pantry stock and ingredient costs, and returns a DataFrame with the shopping list along with total number of ingredients to buy and total estimated cost

        :return: tuple of (shopping list DataFrame with columns "Ingredient", "Quantity to Buy (g)", and "Cost (€)", total number of ingredients to buy, total estimated cost)
        :rtype: tuple[pd.DataFrame, int, float]
        """

        shopping_list = {}

        for index in self.best_meal_plan:
            recipe = self.recipes[int(index)]

            for ingredient_name, quantity_needed in recipe.ingredients.items():
                available = self.pantry_stock.get(ingredient_name, 0) - self.consumed_stock.get(ingredient_name, 0)
                to_buy = max(0, quantity_needed - available)
                if to_buy > 0:
                    shopping_list[ingredient_name] = shopping_list.get(ingredient_name, 0.0) + to_buy

        shopping_data = [
            {
                "Ingredient": name,
                "Quantity to Buy (g)": round(qty, 1),
                "Cost (€)": round(
                    (qty / 100.0) * self.meal_planning_environment.pantry.ingredient_costs.get(name, 1.0), 2
                ),
            }
            for name, qty in sorted(shopping_list.items())
        ]

        shopping_df = pd.DataFrame(shopping_data)

        total_cost = shopping_df["Cost (€)"].sum()
        total_row = pd.DataFrame([{"Ingredient": "TOTAL", "Quantity to Buy (g)": "", "Cost (€)": round(total_cost, 2)}])
        shopping_df = pd.concat([shopping_df, total_row], ignore_index=True)

        return shopping_df, len(shopping_data), total_cost

    def get_daily_nutrition(self) -> pd.DataFrame:
        """
        Calculates the total calories and protein for each day in the best meal plan, and returns a DataFrame showing daily calories, daily protein, and how they compare to the user's targets

        :return: DataFrame with columns "Day", "Calories", "Protein (g)", "Calorie Target", "Protein Target (g)", "Calorie Difference", and "Protein Difference"
        :rtype: pd.DataFrame
        """

        num_days = len(self.best_meal_plan) // 3

        daily_nutrition_data = []

        for day in range(num_days):
            day_indices = self.best_meal_plan[day * 3 : day * 3 + 3]

            daily_calories = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
            )
            daily_protein = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
            )

            calorie_diff = daily_calories - self.preferences.calorie_target_per_day
            protein_diff = daily_protein - self.preferences.protein_target_per_day

            daily_nutrition_data.append(
                {
                    "Day": f"Day {day + 1}",
                    "Calories": f"{round(daily_calories, 1)} kcal",
                    "Protein": f"{round(daily_protein, 1)} g",
                    "Δ Calories and Target Calories": f"{round(calorie_diff, 1)} kcal",
                    "Δ Protein and Target Protein": f"{round(protein_diff, 1)} g",
                }
            )

        daily_nutrition_df = pd.DataFrame(daily_nutrition_data, index=[d["Day"] for d in daily_nutrition_data]).drop(
            columns=["Day"]
        )

        return daily_nutrition_df

    def get_meal_plan_recipes(self) -> pd.DataFrame:
        """
        Returns a DataFrame showing the names of the meals planned for each day based on the best meal plan

        :return: DataFrame with columns "Day", "Meal 1", "Meal 2", and "Meal 3"
        :rtype: pd.DataFrame
        """

        meal_plan = []

        for day in range(7):
            meal_indices = self.best_meal_plan[day * 3 : day * 3 + 3]
            meal_names = [self.recipes[int(index)].name for index in meal_indices]
            meal_plan.append(
                {
                    "Day": day + 1,
                    "Meal 1": meal_names[0],
                    "Meal 2": meal_names[1],
                    "Meal 3": meal_names[2],
                }
            )

        meal_plan_df = pd.DataFrame(meal_plan)

        return meal_plan_df

    def _get_waste_penalty(self, quantity_unused: int, days_until_expiry: int) -> float:
        """
        Calculates a penalty score for leaving an ingredient unused that is close to expiring (higher = worse)

        :param quantity_unused: quantity of the ingredient that goes unused across the week
        :type quantity_unused: int
        :param days_until_expiry: number of days until the ingredient expires
        :type days_until_expiry: int

        :return: penalty score for leaving the ingredient unused based on how close it is to expiring
        :rtype: float
        """

        # no penalty if the ingredient is not expiring within the week
        if days_until_expiry > 7:
            return 0.0

        urgency = max(1, 8 - days_until_expiry)
        penalty = quantity_unused * urgency * self.waste_penalty_urgency_multiplier

        return penalty

    def _get_pantry_score(self, total_units_from_pantry: float, total_units_needed: float) -> float:
        """
        Calculates a score for how well the meal plan makes use of existing pantry stock (higher = better)

        :param total_units_from_pantry: total quantity of ingredients sourced from the pantry across the meal plan
        :type total_units_from_pantry: float
        :param total_units_needed: total quantity of ingredients required across the meal plan
        :type total_units_needed: float

        :return: percentage of ingredient units covered by pantry stock, or 0 if no ingredients are needed
        :rtype: float
        """

        # if no ingredients are needed, we can consider the pantry score to be 0 (neutral) rather than 100%
        if total_units_needed == 0:
            return 0.0

        return (total_units_from_pantry / total_units_needed) * 100.0 * self.panty_score_weight

    def _get_budget_penalty(self, total_cost: float, budget: float) -> float:
        """
        Calculates a penalty score for exceeding the weekly grocery budget (higher = worse)

        :param total_cost: total cost of the ingredients needed for the meal plan
        :type total_cost: float
        :param budget: user's weekly grocery budget
        :type budget: float

        :return: penalty score for exceeding the budget
        :rtype: float
        """

        if total_cost <= budget:
            return 0.0

        excess = total_cost - budget
        penalty = excess * self.budget_penalty_multiplier

        return penalty

    def _evaluate_meal_plan(
        self,
        recipe_indices: list[int],
    ) -> float:
        """
        Evaluates a meal plan (encoded as recipe indices) and returns a fitness score

        Higher scores are better. The score rewards:
            - covering recipe ingredients from existing pantry stock (pantry score)
        and penalises:
            - leaving expiring items unused (waste penalty)
            - not meeting dietary preferences (dietary penalty)
            - exceeding the weekly grocery budget (budget penalty)

        :param recipe_indices: list of recipe indices representing the meal plan (length should be num_days * meals_per_day)
        :type recipe_indices: list[int]

        :return: fitness score for the meal plan
        :rtype: float
        """

        consumed_stock: dict[str, int] = dict.fromkeys(self.pantry_stock, 0)

        total_units_needed = 0
        total_units_from_pantry = 0
        expiry_bonus_total = 0.0
        purchase_cost = 0.0

        for recipe_position, index in enumerate(recipe_indices):
            day = recipe_position // 3
            recipe = self.recipes[index]

            for ingredient_name, quantity_needed in recipe.ingredients.items():
                total_units_needed += quantity_needed

                # only can be sourced from pantry if the ingredient has not expired by this day
                if day < self.days_until_expiry.get(ingredient_name, 999):
                    available = self.pantry_stock.get(ingredient_name, 0) - consumed_stock.get(ingredient_name, 0)
                    from_pantry = max(0, min(available, quantity_needed))
                else:
                    from_pantry = 0

                to_buy = quantity_needed - from_pantry

                consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0) + from_pantry

                total_units_from_pantry += from_pantry
                purchase_cost += (to_buy / 100.0) * self.ingredient_costs.get(ingredient_name, 1.0)

        pantry_score = self._get_pantry_score(total_units_from_pantry, total_units_needed)

        waste_penalty_total = 0.0

        for ingredient_name, quantity_available in self.pantry_stock.items():
            quantity_unused = max(0, quantity_available - consumed_stock.get(ingredient_name, 0))
            waste_penalty_total += self._get_waste_penalty(
                quantity_unused, self.days_until_expiry.get(ingredient_name, 999)
            )

        budget_penalty_total = self._get_budget_penalty(purchase_cost, self.preferences.weekly_budget)

        # per-day nutritional penalty: compare the sum of each day's 3 meals against daily targets
        # (must not be done per-recipe, as individual meals will never reach daily calorie/protein goals)

        num_days = len(recipe_indices) // 3

        dietary_penalty_total = 0.0

        for day in range(num_days):
            day_indices = recipe_indices[day * 3 : day * 3 + 3]

            daily_calories = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
            )
            daily_protein = sum(
                (self.recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
            )

            dietary_penalty_total += (
                abs(daily_calories - self.preferences.calorie_target_per_day) * self.calorie_penalty_weight
            )
            dietary_penalty_total += (
                abs(daily_protein - self.preferences.protein_target_per_day) * self.protein_penalty_weight
            )

        fitness_score = (
            pantry_score + expiry_bonus_total - dietary_penalty_total - waste_penalty_total - budget_penalty_total
        )

        return fitness_score
