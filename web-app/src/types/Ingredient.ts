import type { IngredientGroup } from "./IngredientGroup";

export interface Ingredient {
	name: string;
	description: string;
	status: "OK" | "LOW";
	group: IngredientGroup;
}
