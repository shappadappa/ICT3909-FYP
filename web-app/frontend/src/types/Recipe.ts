import type { NutritionalInformation } from "./NutritionalInformation";

export interface Recipe {
	id: string;
	name: string;
	ingredients: { ingredient: string; quantity: number }[];
	dietaryTags: string[];
	instructions: string[];
	nutritionalInformation: NutritionalInformation;
}
