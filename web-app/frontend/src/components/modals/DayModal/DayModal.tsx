import { useStore } from "@nanostores/react";
import { preferencesStore } from "../../../stores";
import type { NutritionalInformation, Recipe } from "../../../types";
import NutritionalInformationCard from "../../NutritionalInformationCard";
import Modal from "../Modal";
import { GoalRow } from "./GoalRow";
import { MealRow } from "./MealRow";

interface DayMeals {
	breakfast: Recipe | null;
	lunch: Recipe | null;
	dinner: Recipe | null;
}

interface DayModalProps {
	dayName: string | null;
	meals: DayMeals;
	isOpen: boolean;
	onClose: () => void;
}

const sumNutrition = (recipes: (Recipe | null)[]): NutritionalInformation => {
	const base: NutritionalInformation = {
		calories: 0,
		carbohydrates: 0,
		sugar: 0,
		protein: 0,
		fat: 0,
		saturated_fat: 0,
		fiber: 0,
		sodium: 0,
		is_gluten_free: false,
		is_lactose_free: false,
		is_vegetarian: false,
		is_vegan: false,
	};

	return recipes.reduce((acc, recipe) => {
		if (!recipe?.nutritionalInformation) return acc;

		const nutritionalInformation = recipe.nutritionalInformation;

		return {
			...acc,
			calories: acc.calories + nutritionalInformation.calories,
			carbohydrates: acc.carbohydrates + nutritionalInformation.carbohydrates,
			sugar: acc.sugar + nutritionalInformation.sugar,
			protein: acc.protein + nutritionalInformation.protein,
			fat: acc.fat + nutritionalInformation.fat,
			saturated_fat: acc.saturated_fat + nutritionalInformation.saturated_fat,
			fiber: acc.fiber + nutritionalInformation.fiber,
			sodium: acc.sodium + nutritionalInformation.sodium,
		};
	}, base);
};

const RISK_WARNINGS = [
	"One or more meals may contain gluten: you marked yourself as gluten intolerant.",
	"One or more meals may contain lactose: you marked yourself as lactose intolerant.",
	"One or more meals may not be vegetarian: you marked yourself as vegetarian.",
	"One or more meals may not be vegan: you marked yourself as vegan.",
];

export default function DayModal({ dayName, meals, isOpen, onClose }: DayModalProps) {
	const preferences = useStore(preferencesStore);

	if (!isOpen || !dayName) return null;

	const totals = sumNutrition([meals.breakfast, meals.lunch, meals.dinner]);

	const calorieTarget = preferences ? Number(preferences.dailyCalories) : null;
	const proteinTarget = preferences ? Number(preferences.dailyProtein) : null;

	const calDiff = calorieTarget !== null && calorieTarget > 0 ? totals.calories - calorieTarget : null;
	const proteinDiff = proteinTarget !== null && proteinTarget > 0 ? totals.protein - proteinTarget : null;

	const allMeals = [meals.breakfast, meals.lunch, meals.dinner].filter((r): r is Recipe => r !== null);
	const hasGlutenRisk =
		preferences?.glutenIntolerant &&
		allMeals.some((recipe) => recipe.nutritionalInformation && !recipe.nutritionalInformation.is_gluten_free);
	const hasLactoseRisk =
		preferences?.lactoseIntolerant &&
		allMeals.some((recipe) => recipe.nutritionalInformation && !recipe.nutritionalInformation.is_lactose_free);
	const hasVegetarianRisk =
		preferences?.vegetarian &&
		allMeals.some((recipe) => recipe.nutritionalInformation && !recipe.nutritionalInformation.is_vegetarian);
	const hasVeganRisk =
		preferences?.vegan &&
		allMeals.some((recipe) => recipe.nutritionalInformation && !recipe.nutritionalInformation.is_vegan);

	return (
		<Modal title={dayName} isOpen={isOpen} onClose={onClose}>
			<div className="max-h-[65vh] space-y-4 overflow-y-auto pr-4">
				{/* While the meal planner should not recommend dietary-violating recipes, the user may change their preferences after generating a plan, meaning that dietary warnings may still be necessary */}
				<div className="space-y-1.5">
					{[hasGlutenRisk, hasLactoseRisk, hasVegetarianRisk, hasVeganRisk]?.map(
						(risk, index) =>
							risk && (
								<div
									className="flex items-center gap-2 rounded-md border border-amber-100 bg-amber-50 px-3 py-2 text-xs text-amber-700"
									key={index}
								>
									⚠️<span>{RISK_WARNINGS[index]}</span>
								</div>
							)
					)}
				</div>

				<div>
					<h4 className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">Meals</h4>
					<div className="space-y-2">
						<MealRow mealKey="breakfast" recipe={meals.breakfast} />
						<MealRow mealKey="lunch" recipe={meals.lunch} />
						<MealRow mealKey="dinner" recipe={meals.dinner} />
					</div>
				</div>

				<NutritionalInformationCard nutritionalInformation={totals} />

				<div>
					<h4 className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">Estimated Cost</h4>
					<div className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2">
						<span className="text-sm text-gray-600">Total</span>
						<span className="text-sm font-semibold text-gray-800">
							&euro;
							{meals
								? Object.values(meals)
										.reduce((acc, meal) => acc + (meal?.estimated_cost ?? 0), 0)
										.toFixed(2)
								: "0.00"}
						</span>
					</div>
				</div>

				{preferences && Boolean(calorieTarget ?? proteinTarget) && (
					<div>
						<h4 className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">
							vs. Your Goals
						</h4>
						<div className="space-y-2">
							{calorieTarget !== null && calorieTarget > 0 && (
								<GoalRow
									label="Calories"
									actual={Math.round(totals.calories)}
									target={calorieTarget}
									diff={calDiff ?? 0}
									unit="kcal"
									higherIsBetter={false}
								/>
							)}
							{proteinTarget !== null && proteinTarget > 0 && (
								<GoalRow
									label="Protein"
									actual={Number(totals.protein.toFixed(1))}
									target={proteinTarget}
									diff={proteinDiff ?? 0}
									unit="g"
									higherIsBetter={true} // typically, more protein is better (up to a point)
								/>
							)}
						</div>
					</div>
				)}
			</div>
		</Modal>
	);
}
