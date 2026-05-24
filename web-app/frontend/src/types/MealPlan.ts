export interface MealPlan {
	breakfastIds: string[];
	lunchIds: string[];
	dinnerIds: string[];
	cost: number;
	dailyCalories: number[];
	dailyProtein: number[];
	shoppingList: {
		name: string;
		quantity: number;
		cost: number;
	}[];
}
