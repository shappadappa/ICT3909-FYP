from models import Recipe, UserPreferences

DIETARY_PENALTY_VIOLATION = 50.0


def dietary_penalty(recipe: Recipe, preferences: UserPreferences) -> float:
    """
    Calculates a penalty score for a recipe based on how well it aligns with the user's dietary preferences (higher = worse alignment)

    :param recipe: Recipe object to evaluate
    :type recipe: Recipe
    :param preferences: UserPreferences object representing the user's dietary preferences
    :type preferences: UserPreferences

    :return: penalty score for the recipe based on dietary preferences
    :rtype: float
    """

    penalty = 0.0

    if preferences.is_vegan and not recipe.is_vegan:
        penalty += DIETARY_PENALTY_VIOLATION
    if preferences.is_vegetarian and not recipe.is_vegetarian:
        penalty += DIETARY_PENALTY_VIOLATION
    if preferences.requires_gluten_free and not recipe.is_gluten_free:
        penalty += DIETARY_PENALTY_VIOLATION
    if preferences.requires_lactose_free and not recipe.is_lactose_free:
        penalty += DIETARY_PENALTY_VIOLATION

    return penalty


EXPIRY_BONUS_WEIGHTS = {
    1: 0.03,
    3: 0.02,
    7: 0.01,
}


def expiry_bonus(days_until_expiry: int, quantity_used: int) -> float:
    """
    Calculates a bonus score for using an ingredient that is close to expiring (higher = better)

    :param days_until_expiry: number of days until the ingredient expires
    :type days_until_expiry: int
    :param quantity_used: quantity of the ingredient used in the recipe
    :type quantity_used: int

    :return: bonus score for using the ingredient based on how close it is to expiring
    :rtype: float
    """

    bonus = 0.0

    for threshold, weight in EXPIRY_BONUS_WEIGHTS.items():
        if days_until_expiry <= threshold:
            bonus += quantity_used * weight

    return bonus


WASTE_PENALTY_URGENCY_MULTIPLIER = 0.001


def waste_penalty(quantity_unused: int, days_until_expiry: int) -> float:
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
    penalty = quantity_unused * urgency * WASTE_PENALTY_URGENCY_MULTIPLIER

    return penalty


BUDGET_PENALTY_MULTIPLIER = 2.0


def budget_penalty(total_cost: float, budget: float) -> float:
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
    penalty = excess * BUDGET_PENALTY_MULTIPLIER

    return penalty


def evaluate_meal_plan(
    recipe_indices: list[int],
    recipes: list[Recipe],
    pantry_stock: dict[str, int],
    days_until_expiry: dict[str, int],
    preferences: UserPreferences,
    ingredient_costs: dict[str, float],
) -> float:
    """
    Evaluates a meal plan encoded as recipe indices and returns a fitness score

    Higher scores are better. The score rewards:
      - covering recipe ingredients from existing pantry stock (pantry score)
      - using soon-to-expire ingredients (expiry bonus)
    and penalises:
        - leaving expiring items unused (waste penalty)
        - violating dietary preferences (dietary penalty)
        - exceeding the weekly grocery budget (budget penalty)
    """

    consumed_stock: dict[str, int] = dict.fromkeys(pantry_stock, 0)

    total_units_needed = 0
    total_units_from_pantry = 0
    expiry_bonus_total = 0.0
    dietary_penalty_total = 0.0
    purchase_cost = 0.0

    for index in recipe_indices:
        recipe = recipes[index]

        dietary_penalty_total += dietary_penalty(recipe, preferences)

        for ingredient_name, quantity_needed in recipe.ingredients.items():
            total_units_needed += quantity_needed

            available = pantry_stock.get(ingredient_name, 0) - consumed_stock.get(ingredient_name, 0)
            from_pantry = max(0, min(available, quantity_needed))
            to_buy = quantity_needed - from_pantry

            consumed_stock[ingredient_name] = consumed_stock.get(ingredient_name, 0) + from_pantry

            total_units_from_pantry += from_pantry
            expiry_bonus_total += expiry_bonus(days_until_expiry.get(ingredient_name, 999), from_pantry)
            purchase_cost += (to_buy / 100.0) * ingredient_costs.get(ingredient_name, 1.0)

    pantry_score = (total_units_from_pantry / total_units_needed * 100.0) if total_units_needed > 0 else 0.0

    waste_penalty_total = 0.0

    for ingredient_name, quantity_available in pantry_stock.items():
        quantity_unused = max(0, quantity_available - consumed_stock.get(ingredient_name, 0))
        waste_penalty_total += waste_penalty(quantity_unused, days_until_expiry.get(ingredient_name, 999))

    budget_penalty_total = budget_penalty(purchase_cost, preferences.weekly_budget)

    # Per-day nutritional penalty: compare the sum of each day's 3 meals against daily targets
    # (must not be done per-recipe, as individual meals will never reach daily calorie/protein goals)

    num_days = len(recipe_indices) // 3

    for day in range(num_days):
        day_indices = recipe_indices[day * 3 : day * 3 + 3]
        daily_calories = sum(
            (recipes[i].nutritional_information.get_nutritional_value("calories") or 0.0) for i in day_indices
        )
        daily_protein = sum(
            (recipes[i].nutritional_information.get_nutritional_value("protein") or 0.0) for i in day_indices
        )

        # TODO these weights should be tuned

        dietary_penalty_total += abs(daily_calories - preferences.calorie_target_per_day) / 100.0
        dietary_penalty_total += abs(daily_protein - preferences.protein_target_per_day) / 10.0

    fitness_score = (
        pantry_score + expiry_bonus_total - dietary_penalty_total - waste_penalty_total - budget_penalty_total
    )

    return fitness_score
