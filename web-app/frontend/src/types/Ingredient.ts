import type { NutritionalInformation } from "./NutritionalInformation";

export interface Ingredient {
	id: string;
	name: string;
	quantity: number;
	expirationDate: string;
	nutritionalInformation: NutritionalInformation;
}
