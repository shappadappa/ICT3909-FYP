from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, lpSum, value

from engines.fitness_score import fitness_score, get_waste_penalty
from engines.MealPlanner import MealPlanner
from models.MealPlanningEnvironment import MealPlanningEnvironment


class ILPMealPlanner(MealPlanner):
    def __init__(
        self,
        meal_planning_environment: MealPlanningEnvironment,
        pantry_weight: float = 1.0,
        waste_weight: float = 1.0,
        budget_weight: float = 1.0,
        dietary_weight: float = 1.0,
    ):
        """
        The `ILPMealPlanner` class uses integer linear programming (ILP) to find a provably near-optimal meal plan, making it suitable as an oracle / ground-truth upper bound when comparing meal planning strategies

        The returned fitness score is recomputed post-solve using the same fitness function as the GA planner to ensure comparability, even though the ILP objective is a linear approximation of the GA formula

        :param meal_planning_environment: the meal planning environment containing recipes, pantry stock, and user preferences
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

        self.solve_status: int = 0

    def generate_meal_plan(
        self,
        num_days: int = 7,
        meals_per_day: int = 3,
        time_limit: int = 300,
        mip_gap: float = 0.01,
        msg: bool = True,
    ) -> tuple[list[int], float]:
        """
        Solves the meal planning problem as an ILP to find a provably near-optimal plan

        The ILP maximises a linear approximation of the GA fitness function. The pantry score term is linearised by normalising against the average total ingredient weight per plan slot across the recipe pool. All other penalty terms are exact linear equivalents of the GA objective

        :param num_days: number of days to plan meals for (default = 7)
        :type num_days: int
        :param meals_per_day: number of meals per day (default = 3)
        :type meals_per_day: int
        :param time_limit: maximum solver time in seconds; returns best incumbent if the limit is reached before proving optimality (default = 300)
        :type time_limit: int
        :param mip_gap: relative MIP gap tolerance; solver stops as soon as the best integer solution is within this fraction of the LP relaxation bound, without needing to prove full optimality (default = 0.01, i.e. 1%)
        :type mip_gap: float
        :param msg: whether to print CBC solver output (default = True)
        :type msg: bool

        :return: tuple of best meal plan as a list of recipe indices, fitness score computed using the exact GA formula
        :rtype: tuple[list[int], float]
        """

        recipes = self.recipes
        n_recipes = len(recipes)

        if n_recipes == 0:
            raise ValueError("No recipes available in the meal planning environment.")

        D = range(num_days)
        M = range(meals_per_day)
        R = range(n_recipes)

        prob = LpProblem("MealPlan_ILP", LpMaximize)

        # decision variables
        # x[d, m, r] = 1 if recipe r is assigned to meal m on day d
        x = {(d, m, r): LpVariable(f"x_{d}_{m}_{r}", cat="Binary") for d in D for m in M for r in R}

        # assignment constraints: each meal slot must be assigned exactly one recipe
        for d in D:
            for m in M:
                prob += lpSum(x[d, m, r] for r in R) == 1, f"assign_{d}_{m}"

        # symmetry breaking: meal slots within a day are interchangeable in the objective,
        # so enforce a non-decreasing recipe-index order to prune the branch-and-bound tree
        for d in D:
            for m in range(meals_per_day - 1):
                prob += (
                    lpSum(r * x[d, m, r] for r in R) <= lpSum(r * x[d, m + 1, r] for r in R),
                    f"sym_break_{d}_{m}",
                )

        f, pantry_names = self._setup_pantry_vars(prob, x, D, M, R)
        cal_over, cal_under, prot_over, prot_under = self._setup_dietary_vars(prob, x, D, M, R)
        budget_over = self._setup_budget_var(prob, x, D, M, R, f, pantry_names)

        # objectives
        # pantry score: normalised by average total ingredient weight across all plan slots
        recipe_total_weights = [sum(recipe.ingredients.values()) for recipe in recipes]
        avg_weight_per_slot = sum(recipe_total_weights) / n_recipes
        avg_total_needed = max(avg_weight_per_slot * num_days * meals_per_day, 1.0)
        pantry_score_coeff = self.pantry_weight / avg_total_needed

        # waste penalty: using pantry items reduces waste; coefficient is urgency normalised by
        # max possible waste (total pantry stock × max urgency of 7)
        total_pantry_stock = max(sum(self.pantry_stock.get(name, 0.0) for name in pantry_names), 1.0)
        waste_coeff: dict[str, float] = {
            name: get_waste_penalty(1, self.days_until_expiry.get(name, 999))
            * self.waste_weight
            / (total_pantry_stock * 7)
            for name in pantry_names
        }

        # dietary penalty: per-day deviation normalised by target, split equally between
        # calories and protein, then averaged over days
        cal_target = max(self.preferences.calorie_target_per_day, 1.0)
        prot_target = max(self.preferences.protein_target_per_day, 1.0)
        dietary_cal_coeff = self.dietary_weight / (2 * num_days * cal_target)
        dietary_prot_coeff = self.dietary_weight / (2 * num_days * prot_target)

        # budget penalty: overspend normalised by the weekly budget
        budget_coeff = self.budget_weight / max(self.preferences.weekly_budget, 1.0)

        prob += (
            pantry_score_coeff * lpSum(f[name] for name in pantry_names)
            + lpSum(waste_coeff.get(name, 0.0) * f[name] for name in pantry_names)
            - dietary_cal_coeff * lpSum(cal_over[d] + cal_under[d] for d in D)
            - dietary_prot_coeff * lpSum(prot_over[d] + prot_under[d] for d in D)
            - budget_coeff * budget_over,
            "objective",
        )

        # solve the ILP
        solver = PULP_CBC_CMD(timeLimit=time_limit, gapRel=mip_gap, msg=1 if msg else 0)
        prob.solve(solver)
        self.solve_status = prob.status

        # extract solution
        meal_plan: list[int] = []
        for d in D:
            for m in M:
                chosen = next(
                    (r for r in R if value(x[d, m, r]) is not None and value(x[d, m, r]) > 0.5),
                    0,
                )
                meal_plan.append(chosen)

        self.best_meal_plan = meal_plan

        self.best_fitness = fitness_score(
            recipe_indices=meal_plan,
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

        return meal_plan, self.best_fitness

    def _setup_pantry_vars(
        self,
        prob: LpProblem,
        x: dict,
        days: range,
        meals: range,
        recipes_range: range,
    ) -> tuple[dict, list[str]]:
        """
        Adds pantry utilisation variables ``f[name]`` to the ILP, bounded by pantry stock
        and the total consumption of each ingredient on days before it expires

        :return: tuple of (f variable dict keyed by ingredient name, list of pantry ingredient names)
        :rtype: tuple[dict, list[str]]
        """

        pantry_names = [name for name, qty in self.pantry_stock.items() if qty > 0]

        f = {name: LpVariable(f"f_{i}", lowBound=0.0) for i, name in enumerate(pantry_names)}

        # pre-build a sparse map from ingredient name to (recipe_index, quantity) pairs,
        # so pantry constraints only iterate over recipes that actually use each ingredient
        ingredient_to_recipes: dict[str, list[tuple[int, float]]] = {}
        for r in recipes_range:
            for ing, qty in self.recipes[r].ingredients.items():
                if qty > 0:
                    ingredient_to_recipes.setdefault(ing, []).append((r, qty))

        for i, name in enumerate(pantry_names):
            prob += f[name] <= self.pantry_stock[name], f"pantry_cap_{i}"

            days_exp = self.days_until_expiry.get(name, 999)
            usable_days = [d for d in days if d < days_exp]

            if usable_days:
                prob += (
                    f[name]
                    <= lpSum(
                        x[d, m, r] * qty
                        for d in usable_days
                        for m in meals
                        for r, qty in ingredient_to_recipes.get(name, [])
                    ),
                    f"pantry_use_{i}",
                )
            else:
                prob += f[name] <= 0, f"pantry_expired_{i}"

        return f, pantry_names

    def _setup_dietary_vars(
        self,
        prob: LpProblem,
        x: dict,
        days: range,
        meals: range,
        recipes_range: range,
    ) -> tuple[dict, dict, dict, dict]:
        """
        Adds daily calorie and protein deviation variables to the ILP to linearise the
        absolute-value terms in the dietary penalty

        :return: tuple of (cal_over, cal_under, prot_over, prot_under) dicts keyed by day index
        :rtype: tuple[dict, dict, dict, dict]
        """

        cal_over = {d: LpVariable(f"cal_over_{d}", lowBound=0.0) for d in days}
        cal_under = {d: LpVariable(f"cal_under_{d}", lowBound=0.0) for d in days}
        prot_over = {d: LpVariable(f"prot_over_{d}", lowBound=0.0) for d in days}
        prot_under = {d: LpVariable(f"prot_under_{d}", lowBound=0.0) for d in days}

        for d in days:
            daily_cal = lpSum(x[d, m, r] * self.recipe_calories[r] for m in meals for r in recipes_range)
            daily_prot = lpSum(x[d, m, r] * self.recipe_protein[r] for m in meals for r in recipes_range)
            prob += (
                cal_over[d] - cal_under[d] == daily_cal - self.preferences.calorie_target_per_day,
                f"cal_dev_{d}",
            )
            prob += (
                prot_over[d] - prot_under[d] == daily_prot - self.preferences.protein_target_per_day,
                f"prot_dev_{d}",
            )

        return cal_over, cal_under, prot_over, prot_under

    def _setup_budget_var(
        self,
        prob: LpProblem,
        x: dict,
        days: range,
        meals: range,
        recipes_range: range,
        f: dict,
        pantry_names: list[str],
    ) -> LpVariable:
        """
        Adds the budget overrun variable and constraint to the ILP

        :return: ``budget_over`` variable (zero when within budget, positive otherwise)
        :rtype: LpVariable
        """

        recipe_full_costs = [
            sum(qty * self.ingredient_costs.get(ing, 1.0) / 100.0 for ing, qty in recipe.ingredients.items())
            for recipe in self.recipes
        ]

        full_cost_expr = lpSum(x[d, m, r] * recipe_full_costs[r] for d in days for m in meals for r in recipes_range)
        pantry_savings = lpSum(f[name] * self.ingredient_costs.get(name, 1.0) / 100.0 for name in pantry_names)

        budget_over = LpVariable("budget_over", lowBound=0.0)
        prob += (
            budget_over >= full_cost_expr - pantry_savings - self.preferences.weekly_budget,
            "budget_constr",
        )

        return budget_over
