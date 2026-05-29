import { API_BASE_URL } from "../../config";
import type { Recipe } from "../../types";
import type { DietaryTag } from "../../types/DietaryTag";

const RECIPE_NOT_FOUND: Recipe = {
	id: "RECIPE_NOT_FOUND",
	name: "Recipe not found",
	ingredients: [],
	dietaryTags: [],
	instructions: [],
	nutritionalInformation: null as any,
};

export const fetchRecipesByIds = async (ids: string[]): Promise<Recipe[]> => {
	const uniqueIds = Array.from(new Set(ids));
	const params = new URLSearchParams(uniqueIds.map((id) => ["ids", id]));

	const res = await fetch(`${API_BASE_URL}/api/recipes?${params}`);
	if (!res.ok) throw new Error("Failed to fetch recipes");

	const rawRecipes = await res.json();

	return rawRecipes.map(
		(recipe: any): Recipe => ({
			...recipe,
			dietaryTags: recipe.dietary_tags as DietaryTag[],
			nutritionalInformation: recipe.nutritional_information,
		})
	);
};

export const fetchMeals = async (breakfastIds: string[], lunchIds: string[], dinnerIds: string[]) => {
	const recipes = await fetchRecipesByIds([...breakfastIds, ...lunchIds, ...dinnerIds]);

	return {
		breakfastRecipes: breakfastIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
		lunchRecipes: lunchIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
		dinnerRecipes: dinnerIds.map((id) => recipes.find((r) => r.id === id) ?? RECIPE_NOT_FOUND),
	};
};
