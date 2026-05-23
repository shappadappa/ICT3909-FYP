import type { Recipe } from "../../types";

interface MealRowProps {
	readonly mealKey: keyof typeof MEAL_STYLES;
	readonly recipe: Recipe | null;
}

const MEAL_STYLES = {
	breakfast: {
		label: "Breakfast",
		badge: "bg-terra-50 text-terra-600 border border-terra-100",
		text: "text-terra-800",
	},
	lunch: {
		label: "Lunch",
		badge: "bg-sage-50 text-sage-600 border border-sage-100",
		text: "text-sage-800",
	},
	dinner: {
		label: "Dinner",
		badge: "bg-walnut-50 text-walnut-600 border border-walnut-100",
		text: "text-walnut-800",
	},
};

export function MealRow({ mealKey, recipe }: MealRowProps) {
	const style = MEAL_STYLES[mealKey];

	return (
		<div className="flex items-start gap-3 rounded-lg bg-gray-50 px-3 py-2.5">
			<span
				className={`mt-0.5 shrink-0 rounded-md px-2 py-0.5 text-xs font-semibold tracking-wide uppercase ${style.badge}`}
			>
				{style.label}
			</span>
			<div className="min-w-0 flex-1">
				<p className={`truncate text-sm font-medium ${style.text}`}>{recipe?.name ?? "—"}</p>
				{recipe?.nutritionalInformation ? (
					<p className="mt-0.5 text-xs text-gray-400">
						{Math.round(recipe?.nutritionalInformation.calories)} kcal &middot;{" "}
						{recipe?.nutritionalInformation.protein.toFixed(1)}g protein &middot;{" "}
						{recipe?.nutritionalInformation.carbohydrates.toFixed(1)}g carbs &middot;{" "}
						{recipe?.nutritionalInformation.fat.toFixed(1)}g fat
					</p>
				) : (
					<p className="mt-0.5 text-xs text-gray-400">No nutritional data</p>
				)}
			</div>
		</div>
	);
}
