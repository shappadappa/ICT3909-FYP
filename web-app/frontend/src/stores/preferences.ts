import { persistentAtom } from "@nanostores/persistent";
import type { UserPreferences } from "../types";

export const preferencesStore = persistentAtom<UserPreferences | null>("user-preferences", null, {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const setPreferences = (preferences: UserPreferences) => {
	preferencesStore.set({
		dailyCalories: Number(preferences.dailyCalories),
		dailyProtein: Number(preferences.dailyProtein),
		weeklyBudget: Number(preferences.weeklyBudget),
		glutenIntolerant: preferences.glutenIntolerant,
		lactoseIntolerant: preferences.lactoseIntolerant,
		vegetarian: preferences.vegetarian,
		vegan: preferences.vegan,
	});
};
