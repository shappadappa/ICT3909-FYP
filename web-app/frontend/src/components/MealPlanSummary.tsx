import { useStore } from "@nanostores/react";
import { useState } from "react";
import { CalendarIcon, ClipboardIcon, EuroIcon } from "../assets";
import { pantryStore } from "../stores";
import type { MealPlan, UserPreferences } from "../types";
import ShoppingListModal from "./modals/ShoppingListModal";

interface MealPlanSummaryProps {
	mealPlan: MealPlan;
	preferences: UserPreferences;
	isStale: boolean;
}

export default function MealPlanSummary({ mealPlan, preferences, isStale }: MealPlanSummaryProps) {
	const pantry = useStore(pantryStore);

	const [isShoppingListOpen, setIsShoppingListOpen] = useState(false);

	return (
		<div>
			<div className="mt-3 flex flex-col gap-3 xl:flex-row">
				<div className="border-walnut-100 flex flex-1 items-center gap-3 rounded-xl border bg-white px-4 py-3">
					<div className="bg-terra-50 flex h-8 w-8 items-center justify-center rounded-lg">
						<CalendarIcon />
					</div>
					<div>
						<p className="text-walnut-400 text-xs">Total Meals</p>
						<p className="text-walnut-800 text-sm font-semibold">
							{mealPlan.breakfastIds.length + mealPlan.lunchIds.length + mealPlan.dinnerIds.length}{" "}
							planned
						</p>
					</div>
				</div>
				<div
					className="border-walnut-100 hover:bg-sage-50 flex flex-1 cursor-pointer items-center gap-3 rounded-xl border bg-white px-4 py-3"
					onClick={() => setIsShoppingListOpen(true)}
				>
					<div className="bg-sage-50 flex h-8 w-8 items-center justify-center rounded-lg">
						<ClipboardIcon />
					</div>
					<div>
						<p className="text-walnut-400 text-xs">Shopping Items</p>
						<p className="text-walnut-800 text-sm font-semibold">
							{Object.keys(mealPlan.shoppingList).length} items
						</p>
					</div>
				</div>
				{preferences?.weeklyBudget && (
					<div className="border-walnut-100 flex flex-1 items-center gap-3 rounded-xl border bg-white px-4 py-3">
						<div className="bg-walnut-50 flex h-8 w-8 items-center justify-center rounded-lg">
							<EuroIcon />
						</div>
						<div>
							<p className="text-walnut-400 text-xs">Estimated Cost</p>
							<p className="text-walnut-800 text-sm font-semibold">
								<span
									className={
										mealPlan.cost <= preferences.weeklyBudget ? "text-green-600" : "text-red-600"
									}
								>
									&euro;{mealPlan.cost.toFixed(2)}
								</span>
								<span className="pl-2 text-xs opacity-50">
									/ &euro;{preferences.weeklyBudget.toFixed(2)} (Weekly Budget)
								</span>
							</p>
						</div>
					</div>
				)}

				<ShoppingListModal
					mealPlan={mealPlan}
					pantry={pantry}
					isOpen={isShoppingListOpen}
					onClose={() => setIsShoppingListOpen(false)}
				/>
			</div>
			<div
				className="mt-4 rounded-lg bg-yellow-50 p-4 text-sm text-yellow-800"
				style={{ display: isStale ? "block" : "none" }}
			>
				<p>
					⚠️ You updated your preferences without regenerating your meal plan. Your meal plan might not
					reflect your latest preferences.
				</p>
			</div>
		</div>
	);
}
