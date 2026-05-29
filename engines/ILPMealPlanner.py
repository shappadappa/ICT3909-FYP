import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix

from engines.fitness_score import fitness_score, get_waste_penalty
from engines.MealPlanner import MealPlanner
from models.MealPlanningEnvironment import MealPlanningEnvironment

HIGHS_STATUS = {
    0: "Optimal",
    1: "Time / iteration limit reached",
    2: "Infeasible",
    3: "Unbounded",
    4: "Other",
}


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
        The `ILPMealPlanner` class uses integer linear programming (ILP) to find a provably near-optimal meal plan,
        making it suitable as an oracle / ground-truth upper bound when comparing meal planning strategies.

        The returned fitness score is recomputed post-solve using the same fitness function as the GA planner to ensure comparability, even though the ILP objective is a linear approximation of the GA formula

        Uses SciPy's ``milp`` function (HiGHS backend) instead of PuLP/CBC

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
        Solves the meal planning problem as an ILP using SciPy's milp (HiGHS backend) to find a provably near-optimal
        plan.

        The ILP maximises a linear approximation of the GA fitness function. The pantry score term is linearised by
        normalising against the average total ingredient weight per plan slot across the recipe pool. All other penalty
        terms are exact linear equivalents of the GA objective

        :param num_days: number of days to plan meals for (default = 7)
        :type num_days: int
        :param meals_per_day: number of meals per day (default = 3)
        :type meals_per_day: int
        :param time_limit: maximum solver time in seconds; returns best incumbent if the limit is reached before proving
            optimality (default = 300)
        :type time_limit: int
        :param mip_gap: relative MIP gap tolerance; solver stops as soon as the best integer solution is within this
            fraction of the LP relaxation bound (default = 0.01, i.e. 1%)
        :type mip_gap: float
        :param msg: whether to print HiGHS solver output (default = True)
        :type msg: bool
        :return: tuple of best meal plan as a list of recipe indices, fitness score computed using the exact GA formula
        :rtype: tuple[list[int], float]
        """

        recipes = self.recipes
        n_recipes = len(recipes)

        if n_recipes == 0:
            raise ValueError("No recipes available in the meal planning environment.")

        pantry_names = [name for name, qty in self.pantry_stock.items() if qty > 0]
        n_pantry = len(pantry_names)

        # x[d, m, r]   : binary - num_days * meals_per_day * n_recipes vars
        # f[i]         : continuous pantry usage - n_pantry vars
        # cal_over[d]  : continuous - num_days vars
        # cal_under[d] : continuous - num_days vars
        # prot_over[d] : continuous - num_days vars
        # prot_under[d]: continuous - num_days vars
        # budget_over  : continuous - 1 var
        n_x = num_days * meals_per_day * n_recipes
        x_start = 0
        f_start = n_x
        cal_over_start = f_start + n_pantry
        cal_under_start = cal_over_start + num_days
        prot_over_start = cal_under_start + num_days
        prot_under_start = prot_over_start + num_days
        budget_over_idx = prot_under_start + num_days
        n_vars = budget_over_idx + 1

        def x_idx(d: int, m: int, r: int) -> int:
            return x_start + (d * meals_per_day + m) * n_recipes + r

        # objective coefficients (milp minimises, so negate the maximisation terms)
        c = np.zeros(n_vars)

        # pantry score coefficient (same normalisation as the PuLP version)
        recipe_total_weights = [sum(recipe.ingredients.values()) for recipe in recipes]
        avg_weight_per_slot = sum(recipe_total_weights) / n_recipes
        avg_total_needed = max(avg_weight_per_slot * num_days * meals_per_day, 1.0)
        pantry_score_coeff = self.pantry_weight / avg_total_needed

        # waste coefficient per pantry ingredient
        total_pantry_stock = max(sum(self.pantry_stock.get(name, 0.0) for name in pantry_names), 1.0)
        for i, name in enumerate(pantry_names):
            waste_c = (
                get_waste_penalty(1, self.days_until_expiry.get(name, 999))
                * self.waste_weight
                / (total_pantry_stock * 7)
            )
            c[f_start + i] = -(pantry_score_coeff + waste_c)  # negative because milp minimises

        # dietary penalty coefficients
        cal_target = max(self.preferences.calorie_target_per_day, 1.0)
        prot_target = max(self.preferences.protein_target_per_day, 1.0)
        dietary_cal_coeff = self.dietary_weight / (2 * num_days * cal_target)
        dietary_prot_coeff = self.dietary_weight / (2 * num_days * prot_target)

        c[cal_over_start : cal_over_start + num_days] = dietary_cal_coeff
        c[cal_under_start : cal_under_start + num_days] = dietary_cal_coeff
        c[prot_over_start : prot_over_start + num_days] = dietary_prot_coeff
        c[prot_under_start : prot_under_start + num_days] = dietary_prot_coeff

        # budget penalty coefficient
        budget_coeff = self.budget_weight / max(self.preferences.weekly_budget, 1.0)
        c[budget_over_idx] = budget_coeff

        # build constraint matrix in COO format, then convert to CSC
        a_rows: list[int] = []
        a_cols: list[int] = []
        a_data: list[float] = []
        con_lb: list[float] = []
        con_ub: list[float] = []
        row = 0

        def _add(r: int, col: int, val: float) -> None:
            a_rows.append(r)
            a_cols.append(col)
            a_data.append(val)

        # 1. assignment: exactly one recipe per meal slot (sum_r x[d,m,r] == 1)
        for d in range(num_days):
            for m in range(meals_per_day):
                for r in range(n_recipes):
                    _add(row, x_idx(d, m, r), 1.0)
                con_lb.append(1.0)
                con_ub.append(1.0)
                row += 1

        # 2. symmetry breaking within a day: enforces non-decreasing recipe index order
        #    across meal slots to prune the branch-and-bound tree
        #    (sum_r r*x[d,m,r] <= sum_r r*x[d,m+1,r])
        for d in range(num_days):
            for m in range(meals_per_day - 1):
                for r in range(n_recipes):
                    _add(row, x_idx(d, m, r), float(r))
                    _add(row, x_idx(d, m + 1, r), -float(r))
                con_lb.append(-np.inf)
                con_ub.append(0.0)
                row += 1

        # 3. pantry usability: f[i] <= pantry consumption before expiry
        #    (f[name] - sum_{d<days_exp, m, r using name} x[d,m,r]*qty <= 0:
        #    upper bound on f[name] via variable bounds handles the pantry_cap constraint)
        ingredient_to_recipes: dict[str, list[tuple[int, float]]] = {}
        for r in range(n_recipes):
            for ing, qty in recipes[r].ingredients.items():
                if qty > 0:
                    ingredient_to_recipes.setdefault(ing, []).append((r, float(qty)))

        for i, name in enumerate(pantry_names):
            _add(row, f_start + i, 1.0)
            days_exp = self.days_until_expiry.get(name, 999)
            for d in range(num_days):
                if d >= days_exp:
                    continue
                for m in range(meals_per_day):
                    for r, qty in ingredient_to_recipes.get(name, []):
                        _add(row, x_idx(d, m, r), -qty)
            con_lb.append(-np.inf)
            con_ub.append(0.0)
            row += 1

        # 4. dietary calorie deviation: cal_over[d] - cal_under[d] == daily_cal - cal_target
        #    rearranged: cal_over[d] - cal_under[d] - sum_{m,r} x[d,m,r]*cal[r] == -cal_target
        for d in range(num_days):
            _add(row, cal_over_start + d, 1.0)
            _add(row, cal_under_start + d, -1.0)
            for m in range(meals_per_day):
                for r in range(n_recipes):
                    if self.recipe_calories[r]:
                        _add(row, x_idx(d, m, r), -self.recipe_calories[r])
            rhs = -self.preferences.calorie_target_per_day
            con_lb.append(rhs)
            con_ub.append(rhs)
            row += 1

        # 5. dietary protein deviation: prot_over[d] - prot_under[d] == daily_prot - prot_target
        for d in range(num_days):
            _add(row, prot_over_start + d, 1.0)
            _add(row, prot_under_start + d, -1.0)
            for m in range(meals_per_day):
                for r in range(n_recipes):
                    if self.recipe_protein[r]:
                        _add(row, x_idx(d, m, r), -self.recipe_protein[r])
            rhs = -self.preferences.protein_target_per_day
            con_lb.append(rhs)
            con_ub.append(rhs)
            row += 1

        # 6. budget overrun: budget_over >= full_cost - pantry_savings - weekly_budget
        #    budget_over - sum_{d,m,r} x[d,m,r]*cost[r] + sum_i f[i]*unit_cost[i] >= -weekly_budget
        recipe_full_costs = [
            sum(qty * self.ingredient_costs.get(ing, 1.0) / 100.0 for ing, qty in recipe.ingredients.items())
            for recipe in recipes
        ]
        _add(row, budget_over_idx, 1.0)
        for d in range(num_days):
            for m in range(meals_per_day):
                for r in range(n_recipes):
                    if recipe_full_costs[r]:
                        _add(row, x_idx(d, m, r), -recipe_full_costs[r])
        for i, name in enumerate(pantry_names):
            cost_per_unit = self.ingredient_costs.get(name, 1.0) / 100.0
            if cost_per_unit:
                _add(row, f_start + i, cost_per_unit)
        con_lb.append(-self.preferences.weekly_budget)
        con_ub.append(np.inf)
        row += 1

        # assemble sparse constraint matrix
        n_constraints = row
        A = csc_matrix((a_data, (a_rows, a_cols)), shape=(n_constraints, n_vars))
        constraints = LinearConstraint(A, np.array(con_lb), np.array(con_ub))  # type: ignore[arg-type]

        # variable bounds
        lb_vars = np.zeros(n_vars)  # all variables >= 0
        ub_vars = np.full(n_vars, np.inf)
        ub_vars[x_start:f_start] = 1.0  # binary variables in [0, 1]
        for i, name in enumerate(pantry_names):
            ub_vars[f_start + i] = self.pantry_stock[name]  # pantry cap per ingredient
        bounds = Bounds(lb=lb_vars, ub=ub_vars)  # type: ignore[arg-type]

        # integrality: 1 = integer, 0 = continuous
        integrality = np.zeros(n_vars)
        integrality[x_start:f_start] = 1.0  # x variables are binary

        # solve
        options: dict = {
            "time_limit": float(time_limit),
            "mip_rel_gap": mip_gap,
            "disp": msg,
        }
        result = milp(c, constraints=constraints, integrality=integrality, bounds=bounds, options=options)
        self.solve_status = result.status

        # extract solution
        sol = result.x if result.x is not None else np.zeros(n_vars)
        meal_plan: list[int] = []
        for d in range(num_days):
            for m in range(meals_per_day):
                x_vals = [sol[x_idx(d, m, r)] for r in range(n_recipes)]
                chosen = int(np.argmax(x_vals))
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

    def get_solve_status(self) -> str:
        """
        Returns a string describing the status of the last ILP solve attempt.

        :return: status message
        :rtype: str
        """

        return HIGHS_STATUS.get(self.solve_status, "Unknown")
