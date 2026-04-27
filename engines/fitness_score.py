from models import Recipe


def _get_waste_penalty(quantity_unused: int, days_until_expiry: int, waste_penalty_urgency_multiplier: float) -> float:
    """
    Calculates a penalty score for leaving an ingredient unused that is close to expiring (higher = worse)

    :param quantity_unused: quantity of the ingredient that goes unused across the week
    :type quantity_unused: int
    :param days_until_expiry: number of days until the ingredient expires
    :type days_until_expiry: int
    :param waste_penalty_urgency_multiplier: multiplier for calculating the penalty score (higher = less tolerance for waste)
    :type waste_penalty_urgency_multiplier: float

    :return: penalty score for leaving the ingredient unused based on how close it is to expiring
    :rtype: float
    """

    # no penalty if the ingredient is not expiring within the week
    if days_until_expiry > 7:
        return 0.0

    urgency = max(1, 8 - days_until_expiry)
    penalty = quantity_unused * urgency * waste_penalty_urgency_multiplier

    return penalty


def _get_pantry_score(total_units_from_pantry: float, total_units_needed: float, pantry_score_weight: float) -> float:
    """
    Calculates a score for how well the meal plan makes use of existing pantry stock (higher = better)

    :param total_units_from_pantry: total quantity of ingredients sourced from the pantry across the meal plan
    :type total_units_from_pantry: float
    :param total_units_needed: total quantity of ingredients required across the meal plan
    :type total_units_needed: float
    :param pantry_score_weight: weight applied to the pantry score (higher = more importance)
    :type pantry_score_weight: float

    :return: percentage of ingredient units covered by pantry stock, or 0 if no ingredients are needed
    :rtype: float
    """

    # if no ingredients are needed, we can consider the pantry score to be 0 (neutral) rather than 100%
    if total_units_needed == 0:
        return 0.0

    return (total_units_from_pantry / total_units_needed) * 100.0 * pantry_score_weight


def _get_budget_penalty(total_cost: float, budget: float, budget_penalty_multiplier: float) -> float:
    """
    Calculates a penalty score for exceeding the weekly grocery budget (higher = worse)

    :param total_cost: total cost of the ingredients needed for the meal plan
    :type total_cost: float
    :param budget: user's weekly grocery budget
    :type budget: float
    :param budget_penalty_multiplier: multiplier for calculating the penalty score (higher = worse)
    :type budget_penalty_multiplier: float

    :return: penalty score for exceeding the budget
    :rtype: float
    """

    if total_cost <= budget:
        return 0.0

    excess = total_cost - budget
    penalty = excess * budget_penalty_multiplier

    return penalty


def fitness_score(
    recipe_indices: list[int],
    recipes: list[Recipe],
    pantry_stock: dict[str, float],
    days_until_expiry: dict[str, int],
    ingredient_costs: dict[str, float],
    weekly_budget: float,
    calorie_target_per_day: float,
    protein_target_per_day: float,
    pantry_score_weight: float = 1.0,
    waste_penalty_multiplier: float = 0.001,
    budget_penalty_multiplier: float = 2.0,
    calorie_penalty_weight: float = 0.01,
    protein_penalty_weight: float = 0.1,
) -> float:
    """
    Evaluates a meal plan (encoded as recipe indices) and returns a fitness score

    Higher scores are better. The score rewards:
        - covering recipe ingredients from existing pantry stock (pantry score)
    and penalises:
        - leaving expiring items unused (waste penalty)
        - not meeting daily calorie/protein targets (dietary penalty)
        - exceeding the weekly grocery budget (budget penalty)

    :param recipe_indices: list of recipe indices representing the meal plan (length should be num_days * meals_per_day)
    :type recipe_indices: list[int]
    :param recipes: full list of available recipes
    :type recipes: list[Recipe]
    :param pantry_stock: mapping of ingredient name to available quantity in grams
    :type pantry_stock: dict[str, float]
    :param days_until_expiry: mapping of ingredient name to days until it expires
    :type days_until_expiry: dict[str, int]
    :param ingredient_costs: mapping of ingredient name to cost per 100 g
    :type ingredient_costs: dict[str, float]
    :param weekly_budget: user's weekly grocery budget in EUR
    :type weekly_budget: float
    :param calorie_target_per_day: target daily calorie intake in kcal
    :type calorie_target_per_day: float
    :param protein_target_per_day: target daily protein intake in grams
    :type protein_target_per_day: float
    :param pantry_score_weight: weight applied to the pantry utilisation score (default = 1.0)
    :type pantry_score_weight: float
    :param waste_penalty_multiplier: multiplier for leaving near-expiry ingredients unused (default = 0.001)
    :type waste_penalty_multiplier: float
    :param budget_penalty_multiplier: multiplier for exceeding the weekly budget (default = 2.0)
    :type budget_penalty_multiplier: float
    :param calorie_penalty_weight: weight for absolute daily calorie deviation (default = 0.01)
    :type calorie_penalty_weight: float
    :param protein_penalty_weight: weight for absolute daily protein deviation (default = 0.1)
    :type protein_penalty_weight: float

    :return: composite fitness score (higher is better)
    :rtype: float
    """

    consumed_stock: dict[str, float] = dict.fromkeys(pantry_stock, 0.0)

    total_units_needed = 0.0
    total_units_from_pantry = 0.0
    purchase_cost = 0.0

    for recipe_position, index in enumerate(recipe_indices):
        day = recipe_position // 3
        recipe = recipes[index]

        for ingredient_name, quantity_needed in recipe.ingredients.items():
            total_units_needed += quantity_needed

            # can only be sourced from pantry if the ingredient has not expired by this day
            if day < days_until_expiry.get(ingredient_name, 999):
                available = pantry_stock.get(ingredient_name, 0.0) - consumed_stock.get(ingredient_name, 0.0)
                from_pantry = max(0.0, min(available, quantity_needed))
            else:
                from_pantry = 0.0

            to_buy = quantity_needed - from_pantry
            consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0.0) + from_pantry
            total_units_from_pantry += from_pantry
            purchase_cost += (to_buy / 100.0) * ingredient_costs.get(ingredient_name, 1.0)

    pantry_score = _get_pantry_score(total_units_from_pantry, total_units_needed, pantry_score_weight)

    waste_penalty = 0.0

    for ingredient_name, quantity_available in pantry_stock.items():
        quantity_unused = max(0.0, quantity_available - consumed_stock.get(ingredient_name, 0.0))

        waste_penalty += _get_waste_penalty(
            quantity_unused, days_until_expiry.get(ingredient_name, 999), waste_penalty_multiplier
        )

    budget_penalty = _get_budget_penalty(purchase_cost, weekly_budget, budget_penalty_multiplier)

    # compare the sum of each day's meals against daily targets, not per-recipe
    # (individual meals will never reach daily calorie/protein goals on their own)

    num_days = len(recipe_indices) // 3
    dietary_penalty = 0.0

    for day in range(num_days):
        day_indices = recipe_indices[day * 3 : day * 3 + 3]

        daily_calories = sum(
            (recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
        )
        daily_protein = sum(
            (recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
        )

        dietary_penalty += abs(daily_calories - calorie_target_per_day) * calorie_penalty_weight
        dietary_penalty += abs(daily_protein - protein_target_per_day) * protein_penalty_weight

    return pantry_score - dietary_penalty - waste_penalty - budget_penalty
