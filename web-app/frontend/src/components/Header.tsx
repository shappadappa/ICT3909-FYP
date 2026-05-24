import { useStore } from "@nanostores/react";
import { useState } from "react";
import { useGenerateMealPlan } from "../hooks/useGenerateMealPlan";
import { pantryStore, preferencesStore } from "../stores";
import { isLoadingStore } from "../stores/loading";
import ConfirmGenerationModal from "./modals/ConfirmGenerationModal";
import NavMenu from "./NavMenu";

export default function Header() {
	const isLoading = useStore(isLoadingStore);

	const generateMealPlan = useGenerateMealPlan();
	const [isConfirmOpen, setIsConfirmOpen] = useState(false);
	const [confirmWarnings, setConfirmWarnings] = useState<string[]>([]);

	const currentDate = new Date();
	const day = currentDate.getDay();
	const diff = currentDate.getDate() - day + (day === 0 ? -6 : 1);
	const weekStart = new Date(currentDate.setDate(diff)).toLocaleDateString("en-us", {
		month: "short",
		day: "numeric",
	});
	const weekEnd = new Date(currentDate.setDate(diff + 6)).toLocaleDateString("en-us", {
		month: "short",
		day: "numeric",
	});

	const handleGenerateClick = () => {
		if (isLoading) return;

		const warnings: string[] = [];

		if (!preferencesStore.get())
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

	return (
		<header className="border-walnut-100 flex items-center justify-between border-b bg-white px-8 py-4">
			<NavMenu />

			<div className="flex items-center gap-3">
				<span className="text-walnut-400 font-body text-sm">Week of</span>
				<span className="text-walnut-600 bg-parchment border-walnut-100 rounded-full border px-3 py-1 text-sm font-medium">
					{weekStart} - {weekEnd}
				</span>
				<button
					id="generate-meal-plan-btn"
					disabled={isLoading}
					className="bg-sage-600 hover:bg-sage-800 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
					onClick={handleGenerateClick}
				>
					+ Generate Meal Plan
				</button>
			</div>

			<ConfirmGenerationModal
				isOpen={isConfirmOpen}
				onClose={() => setIsConfirmOpen(false)}
				confirmWarnings={confirmWarnings}
				generateMealPlan={generateMealPlan}
			/>
		</header>
	);
}
