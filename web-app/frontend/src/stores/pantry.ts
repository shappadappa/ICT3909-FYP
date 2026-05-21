import { atom } from "nanostores";
import type { Ingredient } from "../types";

export const pantryStore = atom<Ingredient[]>([]);

export function addPantryItem(ingredient: Ingredient) {
	pantryStore.set([...pantryStore.get(), ingredient]);
}

export function modifyPantryItem(updatedIngredient: Ingredient) {
	const updatedPantry = pantryStore
		.get()
		.map((ingredient) => (ingredient.id === updatedIngredient.id ? updatedIngredient : ingredient));
	pantryStore.set(updatedPantry);
}

export function removePantryItem(ingredientId: string) {
	const updatedPantry = pantryStore.get().filter((ingredient) => ingredient.id !== ingredientId);
	pantryStore.set(updatedPantry);
}
