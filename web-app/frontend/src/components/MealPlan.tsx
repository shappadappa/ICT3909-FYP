import { useStore } from "@nanostores/react";
import { useEffect, useRef, useState } from "react";
import { useGenerateMealPlan } from "../hooks/useGenerateMealPlan";
import { isLoadingStore, mealPlanStaleStore, mealPlanStore, pantryStore, preferencesStore } from "../stores";
import type { Recipe } from "../types";
import Badge from "./badges/Badge";
import LoadingSpinner from "./LoadingSpinner";
import MealPlanSummary from "./MealPlanSummary";
import ConfirmGenerationModal from "./modals/ConfirmGenerationModal";
import DayModal from "./modals/DayModal/DayModal";
import RecipeModal from "./modals/RecipeModal";
import { fetchMeals } from "./utils/recipes";

const DAY_NAMES_SHORT_TO_LONG: Record<string, string> = {
	Mon: "Monday",
	Tue: "Tuesday",
	Wed: "Wednesday",
	Thu: "Thursday",
	Fri: "Friday",
	Sat: "Saturday",
	Sun: "Sunday",
};

export default function MealPlan() {
	const mealPlan = useStore(mealPlanStore);
	const mealPlanStale = useStore(mealPlanStaleStore);
	const preferences = useStore(preferencesStore);
	const isLoading = useStore(isLoadingStore);

	const [breakfast, setBreakfast] = useState<Recipe[]>([]);
	const [lunch, setLunch] = useState<Recipe[]>([]);
	const [dinner, setDinner] = useState<Recipe[]>([]);
	const generateMealPlan = useGenerateMealPlan();
	const [isFetchingMeals, setIsFetchingMeals] = useState(false);
	const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
	const [selectedDayShort, setSelectedDayShort] = useState<string | null>(null);
	const [isConfirmOpen, setIsConfirmOpen] = useState(false);
	const [confirmWarnings, setConfirmWarnings] = useState<string[]>([]);
	const [activeDayIndex, setActiveDayIndex] = useState(0);
	const scrollContainerRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!mealPlan) return;

		setIsFetchingMeals(true);
		fetchMeals(mealPlan.breakfastIds, mealPlan.lunchIds, mealPlan.dinnerIds)
			?.then(({ breakfastRecipes, lunchRecipes, dinnerRecipes }) => {
				setBreakfast(breakfastRecipes);
				setLunch(lunchRecipes);
				setDinner(dinnerRecipes);
			})
			.catch(() => {
				(globalThis as any).showSnackbar("Something went wrong. Please try again later.", "error");
			})
			.finally(() => setIsFetchingMeals(false));
	}, [mealPlan]);

	const isEmpty = breakfast?.length == 0 && lunch?.length == 0 && dinner?.length == 0;

	const handleDayClick = (shortDay: string) => {
		if (shortDay === "" || isEmpty) return;

		setSelectedDayShort(shortDay);
	};

	const handleGenerateClick = () => {
		if (isLoading) return;

		const warnings: string[] = [];

		if (!preferences)
			warnings.push(
				"You haven't set your dietary preferences yet. The meal planner will default to a 2500 calorie and 50g protein target with no dietary restrictions and a weekly budget of 50 EUR."
			);

		if (pantryStore.get().length === 0)
			warnings.push("Your pantry is empty. The planner won't be able to use any ingredients you already have.");

		if (warnings.length > 0) {
			setConfirmWarnings(warnings);
			setIsConfirmOpen(true);
		} else {
			generateMealPlan();
		}
	};

	const selectedDayIndex = selectedDayShort ? Object.keys(DAY_NAMES_SHORT_TO_LONG).indexOf(selectedDayShort) : -1;
	const selectedDayName = selectedDayShort ? DAY_NAMES_SHORT_TO_LONG[selectedDayShort] : null;

	const mealRows = [
		{
			label: "Breakfast",
			recipes: breakfast,
			cardClass: "bg-terra-50 border-terra-100",
			textClass: "text-terra-800",
			badgeClass: "border-terra-100 text-terra-600 bg-terra-50",
		},
		{
			label: "Lunch",
			recipes: lunch,
			cardClass: "bg-sage-50 border-sage-100",
			textClass: "text-sage-800",
			badgeClass: "border-sage-100 text-sage-600 bg-sage-50",
		},
		{
			label: "Dinner",
			recipes: dinner,
			cardClass: "bg-walnut-50 border-walnut-100",
			textClass: "text-walnut-800",
			badgeClass: "border-walnut-100 text-walnut-600 bg-walnut-50",
		},
	];

	const renderLoading = () => (
		<div>
			<h2 className="font-display text-walnut-800 text-lg font-semibold">Generating Meal Plan...</h2>

			<LoadingSpinner />
		</div>
	);

	const renderEmpty = () => (
		<div className="flex h-full flex-col items-center justify-center gap-4">
			<p className="text-walnut-600 text-sm">No meals planned for this week.</p>
			<button
				className="bg-sage-600 hover:bg-sage-800 rounded-md px-4 py-2 text-sm font-medium text-white transition-colors duration-150"
				onClick={handleGenerateClick}
			>
				Plan Meals
			</button>

			<ConfirmGenerationModal
				isOpen={isConfirmOpen}
				onClose={() => setIsConfirmOpen(false)}
				confirmWarnings={confirmWarnings}
				generateMealPlan={generateMealPlan}
			/>
		</div>
	);

	const renderContent = () => {
		if (isLoading || isFetchingMeals) return renderLoading();

		if (isEmpty) return renderEmpty();

		return (
			<div>
				<div className="mb-4 flex flex-col items-center justify-between sm:flex-row">
					<h2 className="font-display text-walnut-800 text-lg font-semibold">Weekly Meal Plan</h2>
					<div className="flex gap-2 text-xs font-medium">
						<Badge label="Breakfast" additionalClasses="bg-terra-50 text-terra-600 border-terra-100" />
						<Badge label="Lunch" additionalClasses="bg-sage-50 text-sage-600 border-sage-100" />
						<Badge label="Dinner" additionalClasses="bg-walnut-50 text-walnut-600 border-walnut-100" />
					</div>
				</div>

				{/* mobile: horizontal snap-scroll, one day at a time */}
				<div className="lg:hidden">
					<div
						ref={scrollContainerRef}
						className="flex snap-x snap-mandatory overflow-x-auto"
						onScroll={(e) => {
							const el = e.currentTarget;
							setActiveDayIndex(Math.round(el.scrollLeft / el.clientWidth));
						}}
					>
						{Object.entries(DAY_NAMES_SHORT_TO_LONG).map(([short, long], dayIndex) => (
							<div key={short} className="w-full shrink-0 snap-start">
								<div className="border-walnut-100 overflow-hidden rounded-2xl border bg-white">
									<div
										className="bg-parchment border-walnut-100 text-walnut-600 flex cursor-pointer items-center justify-between border-b p-4 text-center text-xs font-medium tracking-wider uppercase"
										onClick={() => handleDayClick(short)}
									>
										<span className="text-walnut-700 text-sm font-semibold tracking-wide">
											{long}
										</span>
										<span className="text-walnut-400 text-xs">Tap for details</span>
									</div>

									<div className="divide-walnut-50 divide-y">
										{mealRows.map(({ label, recipes, cardClass, textClass, badgeClass }) => (
											<div key={label} className="flex items-start gap-3 p-3">
												<Badge
													label={label}
													additionalClasses={`rounded-md ${badgeClass} uppercase tracking-wider font-semibold shrink-0`}
												/>
												{recipes[dayIndex] ? (
													<div
														className={`recipe-card ${cardClass} flex-1`}
														onClick={() => setSelectedRecipe(recipes[dayIndex])}
													>
														<p className={textClass}>{recipes[dayIndex].name}</p>
													</div>
												) : (
													<p className="text-walnut-300 py-1 text-xs italic">—</p>
												)}
											</div>
										))}
									</div>
								</div>
							</div>
						))}
					</div>

					<div className="mt-2.5 flex justify-center gap-1.5">
						{Object.keys(DAY_NAMES_SHORT_TO_LONG).map((short, i) => (
							<div
								key={short}
								className={`h-1.5 rounded-full transition-all duration-200 ${
									i === activeDayIndex ? "bg-walnut-600 w-4" : "bg-walnut-200 w-1.5"
								}`}
							/>
						))}
					</div>
				</div>

				{/* desktop: full week table */}
				<div className="border-walnut-100 hidden overflow-hidden rounded-2xl border bg-white lg:flex lg:flex-1 lg:flex-col">
					<div className="flex-1 overflow-auto">
						<table className="w-full table-fixed" style={{ minWidth: "700px" }}>
							<thead>
								<tr className="border-walnut-100 bg-parchment border-b">
									{["", ...Object.keys(DAY_NAMES_SHORT_TO_LONG)].map((day) => (
										<th
											key={day}
											className={`text-walnut-600 px-3 py-3 text-center text-xs font-medium tracking-wider uppercase ${day === "" && "w-28"} ${day !== "" && !isEmpty ? "cursor-pointer" : ""}`}
											onClick={() => handleDayClick(day)}
										>
											{day}
										</th>
									))}
								</tr>
							</thead>
							<tbody className="divide-walnut-50 divide-y">
								{mealRows.map(({ label, recipes, cardClass, textClass, badgeClass }) => (
									<tr key={label} className="h-36">
										<td className="px-4 py-3 align-top">
											<Badge
												label={label}
												additionalClasses={`rounded-md ${badgeClass} uppercase tracking-wider font-semibold`}
											/>
										</td>
										{recipes?.map((recipe, index) => (
											<td key={recipe.id + index} className="h-full px-2 py-3">
												<div
													className={`recipe-card ${cardClass}`}
													onClick={() => setSelectedRecipe(recipe)}
												>
													<p className={textClass}>{recipe.name}</p>
												</div>
											</td>
										))}
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>

				<MealPlanSummary mealPlan={mealPlan} preferences={preferences} isStale={mealPlanStale} />

				<RecipeModal
					recipe={selectedRecipe}
					isOpen={selectedRecipe !== null}
					isError={selectedRecipe?.id === "RECIPE_NOT_FOUND"}
					onClose={() => setSelectedRecipe(null)}
				/>

				<DayModal
					dayName={selectedDayName}
					meals={{
						breakfast: selectedDayIndex >= 0 ? (breakfast[selectedDayIndex] ?? null) : null,
						lunch: selectedDayIndex >= 0 ? (lunch[selectedDayIndex] ?? null) : null,
						dinner: selectedDayIndex >= 0 ? (dinner[selectedDayIndex] ?? null) : null,
					}}
					isOpen={selectedDayShort !== null}
					onClose={() => setSelectedDayShort(null)}
				/>
			</div>
		);
	};

	return <section className="flex min-w-0 flex-1 flex-col">{renderContent()}</section>;
}
