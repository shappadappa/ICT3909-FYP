import type { Ingredient, MealPlan } from "../types";
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
				{Object.keys(mealPlan.shoppingList).length === 0 ? (
					<p className="text-walnut-600 text-sm">Your shopping list is empty!</p>
				) : (
					<ul className="text-walnut-600 text-sm">
						{Object.entries(mealPlan.shoppingList).map(([item, [quantity, cost]]) => (
							<li
								key={item}
								className={`my-1 list-disc capitalize ${pantry.find((ingredient) => ingredient.name === item) && "line-through"}`}
								title={pantry.find((ingredient) => ingredient.name === item) && "Already in pantry"}
							>
								{item}: {quantity}g (&euro;{cost.toFixed(2)})
							</li>
						))}
					</ul>
				)}
			</div>
		</Modal>
	);
}
