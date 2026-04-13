import type { Ingredient, Meal } from "./types";

export const breakfastMeals: Meal[] = [
	{ title: "Avocado Toast", description: "2 slices" },
	{ title: "Greek Yogurt & Berries", description: "1 bowl" },
	{ title: "Oat Porridge", description: "Honey & banana" },
	{ title: "Scrambled Eggs", description: "3 eggs, toast" },
	{ title: "Smoothie Bowl", description: "Mango & spinach" },
	{ title: "Pancakes", description: "Maple syrup" },
	{ title: "Bagel & Cream Cheese", description: "Smoked salmon" },
];

export const lunchMeals: Meal[] = [
	{ title: "Chicken Caesar Salad", description: "Croutons, parmesan" },
	{ title: "Lentil Soup", description: "Sourdough bread" },
	{ title: "Turkey Wrap", description: "Lettuce, tomato" },
	{ title: "Tomato Pasta", description: "Basil & olive oil" },
	{ title: "Falafel Bowl", description: "Tzatziki, pita" },
	{ title: "BLT Sandwich", description: "Sourdough" },
	{ title: "Roasted Veg Soup", description: "Crusty roll" },
];

export const dinnerMeals: Meal[] = [
	{ title: "Grilled Salmon", description: "Asparagus, rice" },
	{ title: "Chicken Stir Fry", description: "Noodles, sesame" },
	{ title: "Beef Tacos", description: "Guac, salsa" },
	{ title: "Mushroom Risotto", description: "Parmesan, thyme" },
	{ title: "Lamb Chops", description: "Roast potatoes" },
	{ title: "Prawn Linguine", description: "White wine sauce" },
	{ title: "Veggie Pizza", description: "Mozzarella, peppers" },
];

export const pantryIngredients: Ingredient[] = [
	{ name: "Spinach", description: "200g remaining", status: "LOW", group: "Produce" },
	{ name: "Cherry Tomatoes", description: "1 punnet", status: "OK", group: "Produce" },
	{ name: "Avocados", description: "2 pieces", status: "OK", group: "Produce" },
	{ name: "Bananas", description: "3 left", status: "LOW", group: "Produce" },

	{ name: "Chicken Breast", description: "500g frozen", status: "OK", group: "Proteins" },
	{ name: "Salmon Fillets", description: "2 fillets", status: "OK", group: "Proteins" },
	{ name: "Eggs", description: "4 remaining", status: "LOW", group: "Proteins" },

	{ name: "Basmati Rice", description: "1kg bag", status: "OK", group: "Grains" },
	{ name: "Oats", description: "Half bag left", status: "OK", group: "Grains" },
	{ name: "Pasta (linguine)", description: "1 pack", status: "OK", group: "Grains" },
	{ name: "Sourdough Bread", description: "3 slices", status: "LOW", group: "Grains" },

	{ name: "Greek Yogurt", description: "500g tub", status: "OK", group: "Dairy" },
	{ name: "Parmesan", description: "100g block", status: "OK", group: "Dairy" },
	{ name: "Whole Milk", description: "200ml left", status: "LOW", group: "Dairy" },

	{ name: "Olive Oil", description: "Full bottle", status: "OK", group: "Condiments" },
	{ name: "Soy Sauce", description: "Nearly empty", status: "LOW", group: "Condiments" },
	{ name: "Honey", description: "1 jar", status: "OK", group: "Condiments" },
];
