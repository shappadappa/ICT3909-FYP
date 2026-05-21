import { useEffect, useState } from "react";
import { mockBreakfastMealIds, mockDinnerMealIds, mockLunchMealIds } from "../mock.const";
import type { Recipe } from "../types";
import type { DietaryTag } from "../types/DietaryTag";
import Badge from "./Badge";
import LoadingSpinner from "./LoadingSpinner";
import RecipeModal from "./RecipeModal";
import MealPlanSummary from "./MealPlanSummary";

const RECIPE_NOT_FOUND: Recipe = {
	id: "RECIPE_NOT_FOUND",
	name: "Recipe not found",
	ingredients: [],
	dietaryTags: [],
	instructions: [],
	nutritionalInformation: null as any,
};

const fetchMeals = async (breakfastIds: string[], lunchIds: string[], dinnerIds: string[]) => {
	const uniqueRecipeIds = Array.from(new Set([...breakfastIds, ...lunchIds, ...dinnerIds]));
	const params = new URLSearchParams(uniqueRecipeIds.map((id) => ["recipe_ids", id]));

	const res = await fetch(`http://localhost:8000/api/recipes?${params}`);
	if (!res.ok) throw new Error("Failed to fetch recipes");

	const rawRecipes = await res.json();

	const recipes: Recipe[] = rawRecipes.map(
		(recipe: any): Recipe => ({
			...recipe,
			dietaryTags: recipe.dietary_tags as DietaryTag[],
			nutritionalInformation: recipe.nutritional_information,
		})
	);

	return {
		breakfastRecipes: breakfastIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
		lunchRecipes: lunchIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
		dinnerRecipes: dinnerIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
	};
};

export default function MealPlan() {
	const [breakfast, setBreakfast] = useState<Recipe[]>([]);
	const [lunch, setLunch] = useState<Recipe[]>([]);
	const [dinner, setDinner] = useState<Recipe[]>([]);
	const [isLoading, setIsLoading] = useState(true);
	const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

	const loadMeals = (breakfastIds: string[], lunchIds: string[], dinnerIds: string[]) => {
		setIsLoading(true);
		fetchMeals(breakfastIds, lunchIds, dinnerIds)
			.then(({ breakfastRecipes, lunchRecipes, dinnerRecipes }) => {
				setBreakfast(breakfastRecipes);
				setLunch(lunchRecipes);
				setDinner(dinnerRecipes);
				setIsLoading(false);
			})
			.catch(() => {
				(window as any).showSnackbar("Something went wrong. Please try again later.", "error");
				setIsLoading(false);
			});
	};

	useEffect(() => {
		loadMeals(mockBreakfastMealIds, mockLunchMealIds, mockDinnerMealIds);

		const handler = (event: Event) => {
			const { breakfastIds, lunchIds, dinnerIds } = (event as CustomEvent).detail;
			loadMeals(breakfastIds, lunchIds, dinnerIds);
		};

		window.updateMealPlan = async (detail: { breakfastIds: string[]; lunchIds: string[]; dinnerIds: string[] }) => {
			loadMeals(detail.breakfastIds, detail.lunchIds, detail.dinnerIds);
		};
		return () => window.removeEventListener("updateMealPlan", handler);
	}, []);

	const isEmpty = breakfast.length == 0 && lunch.length == 0 && dinner.length == 0;

	const renderContent = () => {
		if (isLoading) return <LoadingSpinner />;

		if (isEmpty)
			return (
				<div className="flex h-full flex-col items-center justify-center gap-4">
					<p className="text-walnut-600 text-sm">No meals planned for this week.</p>
					<button className="bg-sage-600 hover:bg-sage-700 rounded-md px-4 py-2 text-sm font-medium text-white transition-colors duration-150">
						Plan Meals
					</button>
				</div>
			);

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
						<table className="w-full" style={{ minWidth: "700px" }}>
							<thead>
								<tr className="border-walnut-100 bg-parchment border-b">
									{["", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
										<th
											key={day}
											className="text-walnut-600 px-3 py-3 text-center text-xs font-medium tracking-wider uppercase"
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
										<td key={recipe.id + index} className="px-2 py-3 align-top">
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
										<td key={recipe.id + index} className="px-2 py-3 align-top">
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
										<td key={meal.id + index} className="px-2 py-3 align-top">
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

				<MealPlanSummary />

				<RecipeModal
					recipe={selectedRecipe}
					isOpen={selectedRecipe !== null}
					isError={selectedRecipe?.id === "RECIPE_NOT_FOUND"}
					onClose={() => setSelectedRecipe(null)}
				/>
			</div>
		);
	};

	return <section className="flex min-w-0 flex-1 flex-col">{renderContent()}</section>;
}
