"""
main.py — Entry point for the GA Meal Planner proof-of-concept.

Loads mock pantry data and recipes, runs the Genetic Algorithm, then prints
the optimised weekly meal plan along with a pantry-usage summary.
"""

from mock_data import CURRENT_DATE, create_mock_pantry, create_mock_recipes, create_default_preferences
from ga_engine import GAMealPlanner


def main():
    pantry = create_mock_pantry()
    recipes = create_mock_recipes()
    preferences = create_default_preferences()

    print("=== Pantry contents ===")
    pantry.print()

    print("\nRunning Genetic Algorithm  (population=100, generations=200)…")
    planner = GAMealPlanner(
        recipes=recipes,
        pantry=pantry,
        preferences=preferences,
        current_date=CURRENT_DATE,
        population_size=100,
        generations=200,
        seed=42,
    )

    best_plan, best_fitness, _ = planner.run()

    planner.print_meal_plan(best_plan)
    print(f"\nBest fitness score : {best_fitness:.2f}")

    print("\n=== Pantry usage summary ===")
    usage = planner.summarise_pantry_usage(best_plan)
    for name, info in sorted(usage.items(), key=lambda x: x[1]["days_until_expiry"]):
        expiry_flag = " ⚠ EXPIRES THIS WEEK" if info["expires_this_week"] else ""
        print(
            f"  {name:<15s}  available={info['available']}  "
            f"consumed={info['consumed']}  unused={info['unused']}"
            f"  (expires in {info['days_until_expiry']} days){expiry_flag}"
        )


if __name__ == "__main__":
    main()