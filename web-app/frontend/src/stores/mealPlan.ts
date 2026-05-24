import { persistentAtom } from "@nanostores/persistent";
import type { MealPlan } from "../types";

export const mealPlanStore = persistentAtom<MealPlan | null>("meal-plan", null, {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const mealPlanStaleStore = persistentAtom<boolean>("meal-plan-stale", false, {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const setMealPlan = (mealPlan: MealPlan) => {
	mealPlanStore.set(mealPlan);
	mealPlanStaleStore.set(false);
};

export const setMealPlanStale = (isStale: boolean) => {
	mealPlanStaleStore.set(isStale);
};
