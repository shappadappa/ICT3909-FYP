import { persistentAtom } from "@nanostores/persistent";

interface MealPlanIds {
	breakfastIds: string[];
	lunchIds: string[];
	dinnerIds: string[];
}

export const mealPlanStore = persistentAtom<MealPlanIds | null>("meal-plan", null, {
	encode: JSON.stringify,
	decode: JSON.parse,
});

export const setMealPlan = (ids: MealPlanIds) => {
	mealPlanStore.set(ids);
};
