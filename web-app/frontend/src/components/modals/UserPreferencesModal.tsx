import { useStore } from "@nanostores/react";
import { useEffect, useState } from "react";
import { mealPlanStore, preferencesStore, setPreferences as savePreferences } from "../../stores";
import type { UserPreferences } from "../../types";
import Modal from "./Modal";

interface UserPreferencesProps {
	isOpen: boolean;
	onClose: () => void;
}

const preferenceWeights = [
	{
		key: "pantryWeight",
		label: "Pantry Utilisation",
		description: "How strongly to reward meals that use ingredients already in your pantry.",
	},
	{
		key: "wasteWeight",
		label: "Food Waste",
		description: "How strongly to penalise meal plans that let pantry items expire unused.",
	},
	{
		key: "budgetWeight",
		label: "Budget Adherence",
		description: "How strongly to penalise meal plans that exceed your weekly budget.",
	},
	{
		key: "dietaryWeight",
		label: "Dietary Targets",
		description: "How strongly to penalise meal plans that miss your calorie and protein goals.",
	},
] as const;

const validate = (preferences: UserPreferences): string | null => {
	if (!preferences.dailyCalories) return "Caloric intake is required.";
	if (!preferences.dailyProtein) return "Protein intake is required.";
	if (!preferences.weeklyBudget) return "Weekly budget is required.";
	if (Number.isNaN(Number(preferences.dailyCalories)) || Number(preferences.dailyCalories) < 0)
		return "Caloric intake must be a non-negative number.";
	if (Number.isNaN(Number(preferences.dailyProtein)) || Number(preferences.dailyProtein) < 0)
		return "Protein intake must be a non-negative number.";
	if (Number.isNaN(Number(preferences.weeklyBudget)) || Number(preferences.weeklyBudget) < 0)
		return "Weekly budget must be a non-negative number.";

	if (
		preferences.pantryWeight &&
		(Number.isNaN(Number(preferences.pantryWeight)) || preferences.pantryWeight < 0 || preferences.pantryWeight > 1)
	) {
		return "Pantry weight must be a number between 0 and 1.";
	}
	if (
		preferences.wasteWeight &&
		(Number.isNaN(Number(preferences.wasteWeight)) || preferences.wasteWeight < 0 || preferences.wasteWeight > 1)
	) {
		return "Waste weight must be a number between 0 and 1.";
	}
	if (
		preferences.budgetWeight &&
		(Number.isNaN(Number(preferences.budgetWeight)) || preferences.budgetWeight < 0 || preferences.budgetWeight > 1)
	) {
		return "Budget weight must be a number between 0 and 1.";
	}
	if (
		preferences.dietaryWeight &&
		(Number.isNaN(Number(preferences.dietaryWeight)) ||
			preferences.dietaryWeight < 0 ||
			preferences.dietaryWeight > 1)
	) {
		return "Dietary weight must be a number between 0 and 1.";
	}

	return null;
};

export default function UserPreferencesModal({ isOpen, onClose }: UserPreferencesProps) {
	const savedPreferences = useStore(preferencesStore);

	const [preferences, setPreferences] = useState({
		dailyCalories: savedPreferences?.dailyCalories ?? "",
		dailyProtein: savedPreferences?.dailyProtein ?? "",
		weeklyBudget: savedPreferences?.weeklyBudget ?? "",
		glutenIntolerant: savedPreferences?.glutenIntolerant ?? false,
		lactoseIntolerant: savedPreferences?.lactoseIntolerant ?? false,
		vegetarian: savedPreferences?.vegetarian ?? false,
		vegan: savedPreferences?.vegan ?? false,
		pantryWeight: savedPreferences?.pantryWeight ?? 1.0,
		wasteWeight: savedPreferences?.wasteWeight ?? 1.0,
		budgetWeight: savedPreferences?.budgetWeight ?? 1.0,
		dietaryWeight: savedPreferences?.dietaryWeight ?? 1.0,
	});

	useEffect(() => {
		if (savedPreferences) {
			setPreferences({
				dailyCalories: savedPreferences.dailyCalories ?? "",
				dailyProtein: savedPreferences.dailyProtein ?? "",
				weeklyBudget: savedPreferences.weeklyBudget ?? "",
				glutenIntolerant: savedPreferences.glutenIntolerant ?? false,
				lactoseIntolerant: savedPreferences.lactoseIntolerant ?? false,
				vegetarian: savedPreferences.vegetarian ?? false,
				vegan: savedPreferences.vegan ?? false,
				pantryWeight: savedPreferences.pantryWeight ?? 1.0,
				wasteWeight: savedPreferences.wasteWeight ?? 1.0,
				budgetWeight: savedPreferences.budgetWeight ?? 1.0,
				dietaryWeight: savedPreferences.dietaryWeight ?? 1.0,
			});
		}
	}, [isOpen]);

	const handleSubmit = (e: React.SyntheticEvent<HTMLFormElement>) => {
		e.preventDefault();

		const error = validate(preferences);

		if (error) {
			(globalThis as any).showSnackbar(error, "error");
			return;
		}

		savePreferences(preferences);

		onClose();

		if (mealPlanStore.get()) {
			(globalThis as any).showSnackbar(
				"Preferences saved successfully. You might want to regenerate your meal plan.",
				"info"
			);
			return;
		}

		(globalThis as any).showSnackbar("Preferences saved successfully!", "success");
	};

	return (
		<Modal title="Your Preferences" isOpen={isOpen} onClose={onClose}>
			<form className="flex max-h-[65vh] flex-col gap-5 overflow-y-auto pr-4" onSubmit={handleSubmit}>
				<fieldset className="flex flex-col gap-2">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Dietary Restrictions
					</legend>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="gluten-intolerant"
							checked={preferences.glutenIntolerant}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPreferences((p) => ({ ...p, glutenIntolerant: e.target.checked }))}
						/>
						<span className="text-sm text-gray-700">Gluten-intolerant / Celiac</span>
					</label>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="lactose-intolerant"
							checked={preferences.lactoseIntolerant}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPreferences((p) => ({ ...p, lactoseIntolerant: e.target.checked }))}
						/>
						<span className="text-sm text-gray-700">Lactose-intolerant</span>
					</label>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="vegetarian"
							checked={preferences.vegetarian}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPreferences((p) => ({ ...p, vegetarian: e.target.checked }))}
							disabled={preferences.vegan}
						/>
						<span className="text-sm text-gray-700">Vegetarian</span>
					</label>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="vegan"
							checked={preferences.vegan}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPreferences((p) => ({ ...p, vegan: e.target.checked }))}
						/>
						<span className="text-sm text-gray-700">Vegan</span>
					</label>
				</fieldset>

				<fieldset className="flex flex-col gap-3">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Daily targets
					</legend>

					<div className="flex flex-col gap-1">
						<label htmlFor="calories" className="text-sm font-medium text-gray-600">
							Caloric intake
						</label>
						<div className="relative">
							<input
								type="number"
								id="calories"
								name="calories"
								min="0"
								placeholder="e.g 2000"
								value={preferences.dailyCalories}
								className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-12 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
								onChange={(e) =>
									setPreferences((preferences) => ({ ...preferences, dailyCalories: e.target.value }))
								}
							/>
							<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
								kcal
							</span>
						</div>
					</div>

					<div className="flex flex-col gap-1">
						<label htmlFor="protein" className="text-sm font-medium text-gray-600">
							Protein intake
						</label>
						<div className="relative">
							<input
								type="number"
								id="protein"
								name="protein"
								min="0"
								placeholder="e.g 50"
								value={preferences.dailyProtein}
								className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-12 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
								onChange={(e) =>
									setPreferences((preferences) => ({ ...preferences, dailyProtein: e.target.value }))
								}
							/>
							<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
								g
							</span>
						</div>
					</div>
				</fieldset>

				<fieldset className="flex flex-col gap-3">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Fiscal Targets
					</legend>

					<div className="flex flex-col gap-1">
						<label htmlFor="budget" className="text-sm font-medium text-gray-600">
							Weekly Budget (EUR)
						</label>
						<div className="relative">
							<input
								type="number"
								id="budget"
								name="budget"
								min="0"
								placeholder="e.g 50"
								value={preferences.weeklyBudget}
								className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-12 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
								onChange={(e) =>
									setPreferences((preferences) => ({ ...preferences, weeklyBudget: e.target.value }))
								}
							/>
							<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
								EUR
							</span>
						</div>
					</div>
				</fieldset>

				<fieldset className="flex flex-col gap-3">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Meal Planner Weights (optional)
					</legend>

					{preferenceWeights.map(({ key, label, description }) => (
						<div key={key} className="flex flex-col gap-1">
							<label htmlFor={key} className="text-sm font-medium text-gray-600">
								{label}
							</label>

							<p className="text-xs text-gray-400">{description}</p>

							<div className="relative">
								<input
									type="number"
									id={key}
									name={key}
									min="0"
									max="1"
									step="0.1"
									value={preferences[key]}
									className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-16 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
									onChange={(e) =>
										setPreferences((preferences) => ({
											...preferences,
											[key]: Number(e.target.value),
										}))
									}
								/>
								<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
									0 - 1
								</span>
							</div>
						</div>
					))}
				</fieldset>

				<button
					type="submit"
					className="bg-sage-600 hover:bg-sage-800 mt-1 w-full rounded-lg py-2 text-sm font-medium text-white transition-colors"
				>
					Save preferences
				</button>
			</form>
		</Modal>
	);
}
