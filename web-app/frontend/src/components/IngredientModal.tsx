import { useState, useEffect } from "react";
import { DietaryTag, type Ingredient } from "../types";
import { modifyPantryItem, removePantryItem } from "../stores";
import DietaryTagBadge from "./DietaryTagBadge";
import Modal from "./Modal";
import NutritionalInformationCard from "./NutritionalInformationCard";

interface IngredientModalProps {
	readonly ingredient: Ingredient | null;
	readonly isOpen: boolean;
	readonly onClose: () => void;
}

export default function IngredientModal({ ingredient, isOpen, onClose }: IngredientModalProps) {
	const [isEditing, setIsEditing] = useState(false);
	const [quantity, setQuantity] = useState("");
	const [expirationDate, setExpirationDate] = useState("");

	useEffect(() => {
		if (ingredient) {
			setQuantity(String(ingredient.quantity ?? ""));
			setExpirationDate(ingredient.expirationDate ?? "");
		}
		setIsEditing(false);
	}, [ingredient]);

	if (!isOpen || !ingredient) return null;

	const handleSave = () => {
		if (!quantity) {
			(window as any).showSnackbar("Please enter a quantity.", "error");
			return;
		}
		if (isNaN(Number(quantity))) {
			(window as any).showSnackbar("Please enter a valid quantity.", "error");
			return;
		}
		if (Number(quantity) <= 0) {
			(window as any).showSnackbar("Quantity must be greater than 0.", "error");
			return;
		}

		if (!expirationDate) {
			(window as any).showSnackbar("Please enter an expiration date.", "error");
			return;
		}
		if (new Date(expirationDate) < new Date()) {
			(window as any).showSnackbar("Expiration date cannot be in the past.", "error");
			return;
		}

		modifyPantryItem({
			...ingredient,
			quantity: Number(quantity),
			expirationDate,
		});
		setIsEditing(false);
	};

	return (
		<Modal title={ingredient.name} isOpen={isOpen} onClose={onClose}>
			<div className="max-h-[65vh] space-y-4 overflow-y-auto px-0.5 pr-1">
				<div className="grid grid-cols-2 gap-3 text-sm">
					<div className="flex flex-col gap-1">
						<label htmlFor="edit-quantity" className="text-xs text-gray-400">
							Quantity (g)
						</label>
						<input
							id="edit-quantity"
							type="number"
							min="0"
							value={quantity}
							onChange={(e) => setQuantity(e.target.value)}
							readOnly={!isEditing}
							disabled={!isEditing}
							className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-semibold text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						/>
					</div>
					<div className="flex flex-col gap-1">
						<label htmlFor="edit-expiration" className="text-xs text-gray-400">
							Expiration Date
						</label>
						<input
							id="edit-expiration"
							type="date"
							value={expirationDate}
							onChange={(e) => setExpirationDate(e.target.value)}
							readOnly={!isEditing}
							disabled={!isEditing}
							className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-semibold text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						/>
					</div>
				</div>

				<div>
					<h4 className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Nutritional Information <span className="font-normal normal-case">(per 100g)</span>
					</h4>

					<NutritionalInformationCard nutritionalInformation={ingredient.nutritionalInformation} />
				</div>

				<div className="flex flex-wrap gap-1.5">
					{ingredient.nutritionalInformation.is_gluten_free && (
						<DietaryTagBadge dietaryTag={DietaryTag.GlutenFree} />
					)}
					{ingredient.nutritionalInformation.is_lactose_free && (
						<DietaryTagBadge dietaryTag={DietaryTag.LactoseFree} />
					)}
					{ingredient.nutritionalInformation.is_vegetarian && (
						<DietaryTagBadge dietaryTag={DietaryTag.Vegetarian} />
					)}
					{ingredient.nutritionalInformation.is_vegan && <DietaryTagBadge dietaryTag={DietaryTag.Vegan} />}
				</div>

				<div className="flex justify-end gap-2 border-t border-gray-100 pt-3">
					{isEditing ? (
						<>
							<button
								type="button"
								onClick={() => setIsEditing(false)}
								className="rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
							>
								Cancel
							</button>
							<button
								type="button"
								onClick={handleSave}
								className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
							>
								Save Changes
							</button>
						</>
					) : (
						<>
							<button
								type="button"
								onClick={() => setIsEditing(true)}
								className="flex items-center gap-1.5 rounded-md border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
							>
								<svg
									width="13"
									height="13"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									strokeWidth="2"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a2 2 0 01-1.414.586H9v-2a2 2 0 01.586-1.414z"
									/>
								</svg>
								Edit
							</button>
							<button
								type="button"
								onClick={() => {
									removePantryItem(ingredient.id);
									onClose();
								}}
								className="flex items-center gap-1.5 rounded-md border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50"
							>
								<svg
									width="13"
									height="13"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									strokeWidth="2"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"
									/>
								</svg>
								Remove
							</button>
						</>
					)}
				</div>
			</div>
		</Modal>
	);
}
