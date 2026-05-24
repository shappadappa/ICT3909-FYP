import { persistentAtom } from "@nanostores/persistent";
import type { MealPlan } from "../types";

export const mealPlanStore = persistentAtom<MealPlan | null>("meal-plan", null, {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const setMealPlan = (mealPlan: MealPlan) => {
	mealPlanStore.set(mealPlan);
};
