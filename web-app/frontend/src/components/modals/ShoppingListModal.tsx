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
				{Object.keys(mealPlan.shoppingList).length === 0 ? (
					<p className="text-walnut-600 text-sm">Your shopping list is empty!</p>
				) : (
					<ul className="text-walnut-600 text-sm">
						{mealPlan.shoppingList.map(({ name, quantity, cost }) => (
							<li
								key={name}
								className="my-1 list-disc capitalize"
								title={pantry.find((ingredient) => ingredient.name === name) && "Already in pantry"}
							>
								{name}: {quantity}g (&euro;{cost.toFixed(2)})
							</li>
						))}
					</ul>
				)}
			</div>
		</Modal>
	);
}
