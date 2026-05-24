import { useStore } from "@nanostores/react";
import { useEffect, useState } from "react";
import { useGenerateMealPlan } from "../hooks/useGenerateMealPlan";
import { isLoadingStore, mealPlanStaleStore, mealPlanStore, pantryStore, preferencesStore } from "../stores";
import type { Recipe } from "../types";
import Badge from "./badges/Badge";
import LoadingSpinner from "./LoadingSpinner";
import MealPlanSummary from "./MealPlanSummary";
import ConfirmGenerationModal from "./modals/ConfirmGenerationModal";
import DayModal from "./modals/DayModal/DayModal";
import RecipeModal from "./modals/RecipeModal";
import { fetchMeals } from "./utils/recipes";

const DAY_NAMES_SHORT_TO_LONG: Record<string, string> = {
	Mon: "Monday",
	Tue: "Tuesday",
	Wed: "Wednesday",
	Thu: "Thursday",
	Fri: "Friday",
	Sat: "Saturday",
	Sun: "Sunday",
};

export default function MealPlan() {
	const mealPlan = useStore(mealPlanStore);
	const mealPlanStale = useStore(mealPlanStaleStore);
	const preferences = useStore(preferencesStore);
	const isLoading = useStore(isLoadingStore);

	const [breakfast, setBreakfast] = useState<Recipe[]>([]);
	const [lunch, setLunch] = useState<Recipe[]>([]);
	const [dinner, setDinner] = useState<Recipe[]>([]);
	const generateMealPlan = useGenerateMealPlan();
	const [isFetchingMeals, setIsFetchingMeals] = useState(false);
	const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
	const [selectedDayShort, setSelectedDayShort] = useState<string | null>(null);
	const [isConfirmOpen, setIsConfirmOpen] = useState(false);
	const [confirmWarnings, setConfirmWarnings] = useState<string[]>([]);

	useEffect(() => {
		if (!mealPlan) return;

		setIsFetchingMeals(true);
		fetchMeals(mealPlan.breakfastIds, mealPlan.lunchIds, mealPlan.dinnerIds)
			?.then(({ breakfastRecipes, lunchRecipes, dinnerRecipes }) => {
				setBreakfast(breakfastRecipes);
				setLunch(lunchRecipes);
				setDinner(dinnerRecipes);
			})
			.catch(() => {
				(globalThis as any).showSnackbar("Something went wrong. Please try again later.", "error");
			})
			.finally(() => setIsFetchingMeals(false));
	}, [mealPlan]);

	const isEmpty = breakfast.length == 0 && lunch.length == 0 && dinner.length == 0;

	const handleDayClick = (shortDay: string) => {
		if (shortDay === "" || isEmpty) return;

		setSelectedDayShort(shortDay);
	};

	const handleGenerateClick = () => {
		if (isLoading) return;

		const warnings: string[] = [];

		if (!preferences)
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

	const selectedDayIndex = selectedDayShort ? Object.keys(DAY_NAMES_SHORT_TO_LONG).indexOf(selectedDayShort) : -1;
	const selectedDayName = selectedDayShort ? DAY_NAMES_SHORT_TO_LONG[selectedDayShort] : null;

	const renderLoading = () => (
		<div>
			<h2 className="font-display text-walnut-800 text-lg font-semibold">Generating Meal Plan...</h2>

			<LoadingSpinner />
		</div>
	);

	const renderEmpty = () => (
		<div className="flex h-full flex-col items-center justify-center gap-4">
			<p className="text-walnut-600 text-sm">No meals planned for this week.</p>
			<button
				className="bg-sage-600 hover:bg-sage-800 rounded-md px-4 py-2 text-sm font-medium text-white transition-colors duration-150"
				onClick={handleGenerateClick}
			>
				Plan Meals
			</button>

			<ConfirmGenerationModal
				isOpen={isConfirmOpen}
				onClose={() => setIsConfirmOpen(false)}
				confirmWarnings={confirmWarnings}
				generateMealPlan={generateMealPlan}
			/>
		</div>
	);

	const renderContent = () => {
		if (isLoading || isFetchingMeals) return renderLoading();

		if (isEmpty) return renderEmpty();

		return (
			<div>
				<div className="mb-4 flex items-center justify-between">
					<h2 className="font-display text-walnut-800 text-lg font-semibold">Weekly Meal Plan</h2>
					<div className="flex gap-2 text-xs font-medium">
						<Badge label="Breakfast" additionalClasses="bg-terra-50 text-terra-600 border-terra-100" />
						<Badge label="Lunch" additionalClasses="bg-sage-50 text-sage-600 border-sage-100" />
						<Badge label="Dinner" additionalClasses="bg-walnut-50 text-walnut-600 border-walnut-100" />
					</div>
				</div>

				<div className="border-walnut-100 flex flex-1 flex-col overflow-hidden rounded-2xl border bg-white">
					<div className="flex-1 overflow-auto">
						<table className="w-full table-fixed" style={{ minWidth: "700px" }}>
							<thead>
								<tr className="border-walnut-100 bg-parchment border-b">
									{["", ...Object.keys(DAY_NAMES_SHORT_TO_LONG)].map((day) => (
										<th
											key={day}
											className={`text-walnut-600 px-3 py-3 text-center text-xs font-medium tracking-wider uppercase ${day === "" && "w-28"} ${day !== "" && !isEmpty ? "cursor-pointer" : ""}`}
											onClick={() => handleDayClick(day)}
										>
											{day}
										</th>
									))}
								</tr>
							</thead>
							<tbody className="divide-walnut-50 divide-y">
								<tr className="h-36">
									<td className="px-4 py-3 align-top">
										<Badge
											label="Breakfast"
											additionalClasses="rounded-md border-terra-100 text-terra-600 bg-terra-50 uppercase tracking-wider font-semibold"
										/>
									</td>
									{breakfast?.map((recipe, index) => (
										<td key={recipe.id + index} className="h-full px-2 py-3">
											<div
												className="recipe-card bg-terra-50 border-terra-100"
												onClick={() => setSelectedRecipe(recipe)}
											>
												<p className="text-terra-800">{recipe.name}</p>
											</div>
										</td>
									))}
								</tr>
								<tr className="bg-sage-50/30 h-36">
									<td className="px-4 py-3 align-top">
										<Badge
											label="Lunch"
											additionalClasses="rounded-md border-sage-100 text-sage-600 bg-sage-50 uppercase tracking-wider font-semibold"
										/>
									</td>
									{lunch?.map((recipe, index) => (
										<td key={recipe.id + index} className="h-full px-2 py-3">
											<div
												className="recipe-card bg-sage-50 border-sage-100"
												onClick={() => setSelectedRecipe(recipe)}
											>
												<p className="text-sage-800">{recipe.name}</p>
											</div>
										</td>
									))}
								</tr>
								<tr className="h-36">
									<td className="px-4 py-3 align-top">
										<Badge
											label="Dinner"
											additionalClasses="rounded-md border-walnut-100 text-walnut-600 bg-walnut-50 uppercase tracking-wider font-semibold"
										/>
									</td>
									{dinner?.map((meal, index) => (
										<td key={meal.id + index} className="h-full px-2 py-3">
											<div
												className="recipe-card bg-walnut-50 border-walnut-100"
												onClick={() => setSelectedRecipe(meal)}
											>
												<p className="text-walnut-800">{meal.name}</p>
											</div>
										</td>
									))}
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<MealPlanSummary mealPlan={mealPlan} preferences={preferences} isStale={mealPlanStale} />

				<RecipeModal
					recipe={selectedRecipe}
					isOpen={selectedRecipe !== null}
					isError={selectedRecipe?.id === "RECIPE_NOT_FOUND"}
					onClose={() => setSelectedRecipe(null)}
				/>

				<DayModal
					dayName={selectedDayName}
					meals={{
						breakfast: selectedDayIndex >= 0 ? (breakfast[selectedDayIndex] ?? null) : null,
						lunch: selectedDayIndex >= 0 ? (lunch[selectedDayIndex] ?? null) : null,
						dinner: selectedDayIndex >= 0 ? (dinner[selectedDayIndex] ?? null) : null,
					}}
					isOpen={selectedDayShort !== null}
					onClose={() => setSelectedDayShort(null)}
				/>
			</div>
		);
	};

	return <section className="flex min-w-0 flex-1 flex-col">{renderContent()}</section>;
}
