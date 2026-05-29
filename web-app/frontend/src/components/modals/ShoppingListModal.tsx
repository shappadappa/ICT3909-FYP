import type { Ingredient, MealPlan } from "../../types";
import Modal from "./Modal";

interface ShoppingListModalProps {
	mealPlan: MealPlan;
	pantry: Ingredient[];
	isOpen: boolean;
	onClose: () => void;
}

export default function ShoppingListModal({ mealPlan, pantry, isOpen, onClose }: ShoppingListModalProps) {
	return (
		<Modal title="Shopping List" isOpen={isOpen} onClose={onClose}>
			<div className="max-h-[65vh] overflow-y-auto p-4">
				{mealPlan.shoppingList.length === 0 ? (
					<p className="text-walnut-600 text-sm">Your shopping list is empty!</p>
				) : (
					<ul className="text-walnut-600 text-sm">
						{mealPlan.shoppingList.map(({ name, quantity, cost }) => {
							const pantryItem = pantry.find((ingredient) => ingredient.name === name);
							const pantryQuantity = pantryItem?.quantity ?? 0;
							const adjustedQuantity = Math.max(0, quantity - pantryQuantity);
							const reduced = pantryQuantity > 0 && adjustedQuantity < quantity;
							const adjustedCost = quantity > 0 ? cost * (adjustedQuantity / quantity) : 0;

							return (
								<li
									key={name}
									className="my-1 list-disc capitalize"
									title={reduced ? `${pantryQuantity}g already in pantry` : undefined}
								>
									{name}:{" "}
									{reduced && (
										<span className="mr-1 line-through opacity-50">
											{Math.round(quantity * 100) / 100}g (&euro;{cost.toFixed(2)})
										</span>
									)}
									{Math.round(adjustedQuantity * 100) / 100}g (&euro;{adjustedCost.toFixed(2)})
								</li>
							);
						})}
					</ul>
				)}
			</div>
		</Modal>
	);
}
