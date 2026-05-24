import { useStore } from "@nanostores/react";
import { useEffect, useState } from "react";
import { mealPlanStore, pantryStore } from "../stores";
import type { Ingredient } from "../types";
import AddIngredientModal from "./modals/AddIngredientModal";
import IngredientModal from "./modals/IngredientModal";
import ShoppingListModal from "./modals/ShoppingListModal";
import { fetchRecipesByIds } from "./utils/recipes";

export default function Pantry() {
	const pantryIngredients = useStore(pantryStore);
	const mealPlan = useStore(mealPlanStore);
	const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
	const [query, setQuery] = useState("");
	const [isAddIngredientModalOpen, setIsAddIngredientModalOpen] = useState(false);
	const [isShoppingListOpen, setIsShoppingListOpen] = useState(false);
	const [quantitiesUsedInMealPlan, setQuantitiesUsedInMealPlan] = useState<Record<string, number>>({});

	useEffect(() => {
		if (!mealPlan) {
			setQuantitiesUsedInMealPlan({});
			return;
		}

		const allIds = [...mealPlan.breakfastIds, ...mealPlan.lunchIds, ...mealPlan.dinnerIds];

		fetchRecipesByIds(allIds)
			?.then((recipes) => {
				const totals: Record<string, number> = {};
				for (const id of allIds) {
					const recipe = recipes.find((recipe) => recipe.id === id);
					if (!recipe) continue;

					for (const { ingredient, quantity } of recipe.ingredients) {
						totals[ingredient] = (totals[ingredient] ?? 0) + quantity;
					}
				}

				setQuantitiesUsedInMealPlan(totals);
			})
			.catch(console.error);
	}, [mealPlan]);

	const today = new Date();
	today.setHours(0, 0, 0, 0);

	return (
		<aside className="flex w-72 shrink-0 flex-col">
			<div className="mb-4 flex items-center justify-between">
				<h2 className="font-display text-walnut-800 text-lg font-semibold">Pantry</h2>
				<button
					className="text-sage-600 hover:text-sage-800 bg-sage-50 border-sage-100 hover:bg-sage-100 rounded-lg border px-2.5 py-1 text-xs font-medium transition-colors"
					onClick={() => setIsAddIngredientModalOpen(true)}
				>
					+ Add Item
				</button>
			</div>

			<div className="border-walnut-100 flex flex-1 flex-col overflow-hidden rounded-2xl border bg-white">
				<div className="border-walnut-50 border-b p-3">
					<div className="relative">
						<svg
							className="text-walnut-300 absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							strokeWidth="2"
						>
							<circle cx="11" cy="11" r="8"></circle>
							<path d="M21 21l-4.35-4.35"></path>
						</svg>
						<input
							type="text"
							placeholder="Search pantry…"
							value={query}
							className="bg-parchment border-walnut-100 text-walnut-700 placeholder-walnut-300 focus:ring-sage-300 w-full rounded-lg border py-2 pr-3 pl-8 text-xs focus:ring-1 focus:outline-none"
							onChange={(e) => setQuery(e.currentTarget.value)}
						/>
					</div>
				</div>

				<div className="flex-1 space-y-1 overflow-y-auto p-3">
					{pantryIngredients.length === 0 ? (
						<div className="flex h-full flex-col items-center justify-center gap-2 py-8">
							<p className="text-walnut-400 text-xs">Your pantry is empty.</p>
							<button
								className="text-sage-600 hover:text-sage-800 bg-sage-50 border-sage-100 hover:bg-sage-100 rounded-lg border px-2.5 py-1 text-xs font-medium transition-colors"
								onClick={() => setIsAddIngredientModalOpen(true)}
							>
								Add Item
							</button>
						</div>
					) : (
						pantryIngredients
							.filter((ingredient) => ingredient.name.toLowerCase().includes(query.trim().toLowerCase()))
							.map((ingredient, index) => (
								<button
									key={ingredient.id + index}
									type="button"
									className="pantry-item flex w-full items-center justify-between rounded-lg px-3 py-2 text-left transition-colors"
									onClick={() => setSelectedIngredient(ingredient)}
								>
									<div>
										<p className="text-walnut-700 text-xs font-medium capitalize">
											{ingredient.name}
										</p>
										<p className="text-walnut-400 text-xs">Quantity (g): {ingredient.quantity}</p>
										{mealPlan && (
											<p className="text-2xs text-amber-600">
												{quantitiesUsedInMealPlan[ingredient.name]
													? `${Math.round(quantitiesUsedInMealPlan[ingredient.name] * 100) / 100}g used in meal plan`
													: "Unused in meal plan"}
											</p>
										)}
										{new Date(ingredient.expirationDate) < today ? (
											<p className="text-2xs text-red-500">Expired</p>
										) : (
											<p className="text-walnut-400 text-xs">
												Expiring on:{" "}
												{ingredient.expirationDate
													? new Date(ingredient.expirationDate).toLocaleDateString(
															undefined,
															{
																day: "2-digit",
																month: "2-digit",
																year: "numeric",
															}
														)
													: "N/A"}
											</p>
										)}
										<p className="text-walnut-400 text-xs">
											Price: {ingredient.cost ? `€${ingredient.cost.toFixed(2)}` : "N/A"}
										</p>
									</div>
								</button>
							))
					)}
				</div>

				<footer className="border-walnut-100 bg-parchment flex items-center justify-between border-t px-4 py-3">
					<div className="flex gap-3">
						<span className="text-walnut-500 text-xs">
							<span className="text-sage-600 font-semibold">{pantryIngredients.length}</span> items
						</span>
					</div>
					{mealPlan && (
						<button
							className="text-terra-600 hover:bg-terra-100 bg-terra-50 border-terra-100 rounded-lg border px-2.5 py-1 text-xs font-medium transition-colors"
							onClick={() => setIsShoppingListOpen(true)}
						>
							Shopping List
						</button>
					)}
				</footer>
			</div>

			<IngredientModal
				ingredient={selectedIngredient}
				isOpen={selectedIngredient !== null}
				onClose={() => setSelectedIngredient(null)}
			/>
			<AddIngredientModal isOpen={isAddIngredientModalOpen} onClose={() => setIsAddIngredientModalOpen(false)} />

			{mealPlan && (
				<ShoppingListModal
					isOpen={isShoppingListOpen}
					onClose={() => setIsShoppingListOpen(false)}
					mealPlan={mealPlan}
					pantry={pantryIngredients}
				/>
			)}
		</aside>
	);
}
