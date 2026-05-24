import { useStore } from "@nanostores/react";
import { useState } from "react";
import { pantryStore } from "../stores";
import type { MealPlan, UserPreferences } from "../types";
import ShoppingListModal from "./ShoppingListModal";

interface MealPlanSummaryProps {
	mealPlan: MealPlan;
	preferences: UserPreferences;
}

export default function MealPlanSummary({ mealPlan, preferences }: MealPlanSummaryProps) {
	const pantry = useStore(pantryStore);

	const [isShoppingListOpen, setIsShoppingListOpen] = useState(false);

	return (
		<div className="mt-3 flex gap-3">
			<div className="border-walnut-100 flex flex-1 items-center gap-3 rounded-xl border bg-white px-4 py-3">
				<div className="bg-terra-50 flex h-8 w-8 items-center justify-center rounded-lg">
					<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#C96B46" strokeWidth="2">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
						></path>
					</svg>
				</div>
				<div>
					<p className="text-walnut-400 text-xs">Total Meals</p>
					<p className="text-walnut-800 text-sm font-semibold">
						{mealPlan.breakfastIds.length + mealPlan.lunchIds.length + mealPlan.dinnerIds.length} planned
					</p>
				</div>
			</div>
			<div
				className="border-walnut-100 hover:bg-sage-50 flex flex-1 cursor-pointer items-center gap-3 rounded-xl border bg-white px-4 py-3"
				onClick={() => setIsShoppingListOpen(true)}
			>
				<div className="bg-sage-50 flex h-8 w-8 items-center justify-center rounded-lg">
					<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#4F7A47" strokeWidth="2">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
						></path>
					</svg>
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
						<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#6E5438" strokeWidth="2">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							></path>
						</svg>
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
	);
}
