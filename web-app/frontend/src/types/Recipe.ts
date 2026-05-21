import type { NutritionalInformation } from "./NutritionalInformation";
import type { DietaryTag } from "./DietaryTag";

export interface Recipe {
	id: string;
	name: string;
	ingredients: { ingredient: string; quantity: number }[];
	dietaryTags: DietaryTag[];
	instructions: string[];
	nutritionalInformation: NutritionalInformation;
}
