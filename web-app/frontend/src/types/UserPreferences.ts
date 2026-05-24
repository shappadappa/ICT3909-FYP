export interface UserPreferences {
	dailyCalories: number | string;
	dailyProtein: number | string;
	weeklyBudget: number | string;
	glutenIntolerant: boolean;
	lactoseIntolerant: boolean;
	vegetarian: boolean;
	vegan: boolean;
	pantryWeight?: number;
	wasteWeight?: number;
	budgetWeight?: number;
	dietaryWeight?: number;
}
