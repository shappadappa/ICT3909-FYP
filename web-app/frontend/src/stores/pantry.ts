import { persistentAtom } from "@nanostores/persistent";
import type { Ingredient } from "../types";

export const pantryStore = persistentAtom<Ingredient[]>("pantry", [], {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const addPantryItem = (ingredient: Ingredient) => {
	pantryStore.set([...pantryStore.get(), ingredient]);
};

export const modifyPantryItem = (updatedIngredient: Ingredient) => {
	pantryStore.set(
		pantryStore.get().map((ingredient) => (ingredient.id === updatedIngredient.id ? updatedIngredient : ingredient))
	);
};

export const removePantryItem = (ingredientId: string) => {
	pantryStore.set(pantryStore.get().filter((ingredient) => ingredient.id !== ingredientId));
};
