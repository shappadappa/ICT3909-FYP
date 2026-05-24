from models import Recipe


def get_waste_penalty(quantity_unused: float, days_until_expiry: int) -> float:
    """
    Returns the raw waste score for a single pantry ingredient (quantity × urgency)

    Normalisation against total pantry stock is handled by the caller inside ``fitness_score``

    :param quantity_unused: quantity of the ingredient that goes unused across the week
    :type quantity_unused: float
    :param days_until_expiry: number of days until the ingredient expires
    :type days_until_expiry: int

    :return: raw waste contribution (quantity x urgency), or 0 if not expiring within the week
    :rtype: float
    """

    # no penalty if the ingredient is not expiring within the week
    if days_until_expiry > 7:
        return 0.0

    urgency = max(1, 8 - days_until_expiry)  # urgency in [1, 7]
    return quantity_unused * urgency


def _get_pantry_score(total_units_from_pantry: float, total_units_needed: float) -> float:
    """
    Returns pantry utilisation as a fraction in [0, 1]

    :param total_units_from_pantry: total quantity of ingredients sourced from the pantry across the meal plan
    :type total_units_from_pantry: float
    :param total_units_needed: total quantity of ingredients required across the meal plan
    :type total_units_needed: float

    :return: fraction of ingredient units covered by pantry stock, or 0 if no ingredients are needed
    :rtype: float
    """

    # if no ingredients are needed, we can consider the pantry score to be 0 (neutral) rather than 100%
    if total_units_needed == 0:
        return 0.0

    return total_units_from_pantry / total_units_needed


def _get_budget_penalty(total_cost: float, budget: float) -> float:
    """
    Returns budget overspend as a fraction of the weekly budget, clamped to [0, 1]

    :param total_cost: total cost of the ingredients needed for the meal plan
    :type total_cost: float
    :param budget: user's weekly grocery budget
    :type budget: float

    :return: fractional budget overspend in [0, 1], or 0 if within budget
    :rtype: float
    """

    if total_cost <= budget or budget == 0:
        return 0.0

    return min(1.0, (total_cost - budget) / budget)


def fitness_score(
    recipe_indices: list[int],
    recipes: list[Recipe],
    pantry_stock: dict[str, float],
    days_until_expiry: dict[str, int],
    ingredient_costs: dict[str, float],
    weekly_budget: float,
    calorie_target_per_day: float,
    protein_target_per_day: float,
    meals_per_day: int = 3,
    pantry_weight: float = 1.0,
    waste_weight: float = 1.0,
    budget_weight: float = 1.0,
    dietary_weight: float = 1.0,
    recipe_calories: list[float] | None = None,
    recipe_protein: list[float] | None = None,
) -> float:
    """
    Evaluates a meal plan (encoded as recipe indices) and returns a fitness score

    All four components are normalised to [0, 1] before weights are applied, so the weights are directly comparable across features. The overall score ranges from -3 to 1 when all weights are 1.0 (one reward, three penalties).

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
    :param pantry_weight: importance weight for the pantry utilisation reward, in [0, 1] (default = 1.0)
    :type pantry_weight: float
    :param waste_weight: importance weight for the food waste penalty, in [0, 1] (default = 1.0)
    :type waste_weight: float
    :param budget_weight: importance weight for the budget overspend penalty, in [0, 1] (default = 1.0)
    :type budget_weight: float
    :param dietary_weight: importance weight for the dietary target penalty, in [0, 1] (default = 1.0)
    :type dietary_weight: float

    :return: composite fitness score (higher is better); range is [-3, 1] when all weights are 1.0
    :rtype: float
    """

    consumed_stock: dict[str, float] = dict.fromkeys(pantry_stock, 0.0)

    total_units_needed = 0.0
    total_units_from_pantry = 0.0
    purchase_cost = 0.0

    for recipe_position, index in enumerate(recipe_indices):
        day = recipe_position // meals_per_day
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

    pantry_score = _get_pantry_score(total_units_from_pantry, total_units_needed) * pantry_weight

    # normalise waste by the theoretical maximum (all pantry stock unused at maximum urgency of 7)
    total_pantry_stock = sum(pantry_stock.values())
    raw_waste = 0.0

    for ingredient_name, quantity_available in pantry_stock.items():
        quantity_unused = max(0.0, quantity_available - consumed_stock.get(ingredient_name, 0.0))
        raw_waste += get_waste_penalty(quantity_unused, days_until_expiry.get(ingredient_name, 999))

    if total_pantry_stock > 0:
        waste_penalty = min(1.0, raw_waste / (total_pantry_stock * 7)) * waste_weight
    else:
        waste_penalty = 0.0

    budget_penalty = _get_budget_penalty(purchase_cost, weekly_budget) * budget_weight

    # compare the sum of each day's meals against daily targets, not per-recipe
    # (individual meals will never reach daily calorie/protein goals on their own)
    # each daily deviation is normalised by the target and clamped to [0, 1],
    # then averaged equally across calories and protein and across all days

    num_days = len(recipe_indices) // meals_per_day
    dietary_penalty = 0.0

    for day in range(num_days):
        day_indices = recipe_indices[day * meals_per_day : (day + 1) * meals_per_day]

        if recipe_calories is not None and recipe_protein is not None:
            daily_calories = sum(recipe_calories[i] for i in day_indices)
            daily_protein = sum(recipe_protein[i] for i in day_indices)
        else:
            daily_calories = sum(
                (recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
            )
            daily_protein = sum(
                (recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
            )

        calorie_dev = (
            min(1.0, abs(daily_calories - calorie_target_per_day) / calorie_target_per_day)
            if calorie_target_per_day > 0
            else 0.0
        )
        protein_dev = (
            min(1.0, abs(daily_protein - protein_target_per_day) / protein_target_per_day)
            if protein_target_per_day > 0
            else 0.0
        )
        dietary_penalty += (calorie_dev + protein_dev) / 2

    if num_days > 0:
        dietary_penalty = (dietary_penalty / num_days) * dietary_weight

    return pantry_score - dietary_penalty - waste_penalty - budget_penalty
