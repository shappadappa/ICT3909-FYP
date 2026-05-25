import { API_BASE_URL } from "../config";
import { isLoadingStore, pantryStore, preferencesStore, setIsLoading, setMealPlan } from "../stores";

export function useGenerateMealPlan() {
	const isLoading = isLoadingStore.get();
	const preferences = preferencesStore.get();
	const pantry = pantryStore.get();

	const generateMealPlan = async () => {
		if (isLoading) return;
		setIsLoading(true);

		try {
			const requestBody = {
				user_preferences: {
					weekly_budget: preferences ? Number(preferences.weeklyBudget) || 50.0 : 50.0,
					calorie_target_per_day: preferences ? Number(preferences.dailyCalories) || 2500.0 : 2500.0,
					protein_target_per_day: preferences ? Number(preferences.dailyProtein) || 50.0 : 50.0,
					is_vegetarian: preferences?.vegetarian ?? false,
					is_vegan: preferences?.vegan ?? false,
					requires_gluten_free: preferences?.glutenIntolerant ?? false,
					requires_lactose_free: preferences?.lactoseIntolerant ?? false,
					pantry_weight: preferences?.pantryWeight ?? 1.0,
					waste_weight: preferences?.wasteWeight ?? 1.0,
					budget_weight: preferences?.budgetWeight ?? 1.0,
					dietary_weight: preferences?.dietaryWeight ?? 1.0,
				},
				pantry_items: pantry.map((ingredient) => ({
					id: ingredient.id,
					ingredient_name: ingredient.name,
					quantity_grams: ingredient.quantity ?? 0,
					expiry_date: ingredient.expirationDate ?? null,
				})),
				num_days: 7,
				meals_per_day: 3,
				num_generations: 100,
			};

			const res = await fetch(`${API_BASE_URL}/api/meal-plan`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(requestBody),
			});

			if (!res.ok) {
				throw new Error(`API error: ${res.status}`);
			}

			const data = await res.json();

			const mealPlan = data.meal_plan;
			const [breakfastIds, lunchIds, dinnerIds] = [0, 1, 2].map((index) =>
				mealPlan.map((day: string[]) => day[index])
			);

			setMealPlan({
				breakfastIds,
				lunchIds,
				dinnerIds,
				cost: data.estimated_cost,
				dailyCalories: data.calories_per_day,
				dailyProtein: data.protein_per_day,
				shoppingList: data.shopping_list.map((item: any) => ({
					name: item.ingredient_name,
					quantity: item.quantity_grams,
					cost: item.estimated_cost,
				})),
			});
		} catch (err) {
			console.error("Failed to generate meal plan:", err);
		} finally {
			setIsLoading(false);
		}
	};

	return generateMealPlan;
}
