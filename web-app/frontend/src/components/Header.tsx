import { useState } from "react";
import NavMenu from "./NavMenu";
import Modal from "./Modal";
import { pantryStore, preferencesStore, setMealPlan } from "../stores";

export default function Header() {
	const [isLoading, setIsLoading] = useState(false);
	const [isConfirmOpen, setIsConfirmOpen] = useState(false);
	const [confirmWarnings, setConfirmWarnings] = useState<string[]>([]);

	const currentDate = new Date();
	const day = currentDate.getDay();
	const diff = currentDate.getDate() - day + (day === 0 ? -6 : 1);
	const weekStart = new Date(currentDate.setDate(diff)).toLocaleDateString("en-us", {
		month: "short",
		day: "numeric",
	});
	const weekEnd = new Date(currentDate.setDate(diff + 6)).toLocaleDateString("en-us", {
		month: "short",
		day: "numeric",
	});

	const handleGenerateClick = () => {
		if (isLoading) return;

		const warnings: string[] = [];

		if (!preferencesStore.get())
			warnings.push(
				"You haven't set your dietary preferences yet. The meal planner will default to a 2500 calorie and 50g protein target with no dietary restrictions and a weekly budget of 50 EUR."
			);

		if (pantryStore.get().length === 0)
			warnings.push("Your pantry is empty. The planner won't be able to use any ingredients you already have.");

		if (warnings.length > 0) {
			setConfirmWarnings(warnings);
			setIsConfirmOpen(true);
		} else {
			generateMealPlan();
		}
	};

	const generateMealPlan = async () => {
		if (isLoading) return;
		setIsLoading(true);

		try {
			const preferences = preferencesStore.get();

			const requestBody = {
				user_preferences: {
					weekly_budget: preferences ? Number(preferences.weeklyBudget) : 50.0,
					calorie_target_per_day: preferences ? Number(preferences.dailyCalories) : 2500.0,
					protein_target_per_day: preferences ? Number(preferences.dailyProtein) : 50.0,
					is_vegetarian: false,
					is_vegan: false,
					requires_gluten_free: preferences?.glutenIntolerant ?? false,
					requires_lactose_free: preferences?.lactoseIntolerant ?? false,
				},
				pantry_items: pantryStore.get().map((ingredient) => ({
					id: ingredient.id,
					ingredient_name: ingredient.name,
					quantity_grams: ingredient.quantity ?? 0,
					expiry_date: ingredient.expirationDate ?? null,
				})),
				num_days: 7,
				meals_per_day: 3,
				num_generations: 100,
			};

			const res = await fetch(`http://localhost:8000/api/meal-plan`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(requestBody),
			});

			if (!res.ok) {
				throw new Error(`API error: ${res.status}`);
			}

			const data = await res.json();

			const mealPlan = data.meal_plan;

			const [breakfastIds, lunchIds, dinnerIds] = [0, 1, 2].map((index) => mealPlan.map((day) => day[index]));

			setMealPlan({ breakfastIds, lunchIds, dinnerIds });
		} catch (err) {
			console.error("Failed to generate meal plan:", err);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<header className="border-walnut-100 flex items-center justify-between border-b bg-white px-8 py-4">
			<NavMenu />

			<div className="flex items-center gap-3">
				<span className="text-walnut-400 font-body text-sm">Week of</span>
				<span className="text-walnut-600 bg-parchment border-walnut-100 rounded-full border px-3 py-1 text-sm font-medium">
					{weekStart} - {weekEnd}
				</span>
				<button
					id="generate-meal-plan-btn"
					disabled={isLoading}
					className="bg-sage-600 hover:bg-sage-800 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
					onClick={handleGenerateClick}
				>
					+ Generate Meal Plan
				</button>
			</div>

			<Modal title="Before you Continue" isOpen={isConfirmOpen} onClose={() => setIsConfirmOpen(false)}>
				<div className="flex flex-col gap-4">
					<ul className="flex flex-col gap-2">
						{confirmWarnings.map((w) => (
							<li
								key={w}
								className="flex items-start gap-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2.5 text-sm text-amber-800"
							>
								<span className="mt-0.5 shrink-0">⚠️</span>
								{w}
							</li>
						))}
					</ul>
					<p className="text-sm text-gray-500">
						You can still generate a meal plan, but the results may not match your needs.
					</p>
					<div className="flex justify-end gap-2">
						<button
							className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
							onClick={() => setIsConfirmOpen(false)}
						>
							Cancel
						</button>
						<button
							className="bg-sage-600 hover:bg-sage-800 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors"
							onClick={() => {
								setIsConfirmOpen(false);
								generateMealPlan();
							}}
						>
							Generate Anyway
						</button>
					</div>
				</div>
			</Modal>
		</header>
	);
}
