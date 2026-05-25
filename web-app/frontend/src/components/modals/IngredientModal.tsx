import { useEffect, useState } from "react";
import { BinIcon, PencilIcon } from "../../assets";
import { modifyPantryItem, removePantryItem } from "../../stores";
import { DietaryTag, type Ingredient } from "../../types";
import DietaryTagBadge from "../badges/DietaryTagBadge";
import NutritionalInformationCard from "../NutritionalInformationCard";
import Modal from "./Modal";

interface IngredientModalProps {
	readonly ingredient: Ingredient | null;
	readonly isOpen: boolean;
	readonly onClose: () => void;
}

export default function IngredientModal({ ingredient, isOpen, onClose }: IngredientModalProps) {
	const [isEditing, setIsEditing] = useState(false);
	const [quantity, setQuantity] = useState("");
	const [expirationDate, setExpirationDate] = useState("");
	const [price, setPrice] = useState("");

	const today = new Date();
	today.setHours(0, 0, 0, 0);

	useEffect(() => {
		if (ingredient) {
			setQuantity(String(ingredient.quantity ?? ""));
			setExpirationDate(ingredient.expirationDate ?? "");
			setPrice(ingredient.cost !== undefined ? String(ingredient.cost) : "");
		}
		setIsEditing(false);
	}, [ingredient]);

	if (!isOpen || !ingredient) return null;

	const handleCancel = () => {
		setIsEditing(false);
		setQuantity(String(ingredient.quantity ?? ""));
		setExpirationDate(ingredient.expirationDate ?? "");
		setPrice(ingredient.cost !== undefined ? String(ingredient.cost) : "");
	};

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
		if (new Date(expirationDate) < today) {
			(window as any).showSnackbar("Expiration date cannot be in the past.", "error");
			return;
		}

		if (!price) {
			(window as any).showSnackbar("Please enter a price.", "error");
			return;
		}
		if (isNaN(Number(price))) {
			(window as any).showSnackbar("Please enter a valid price.", "error");
			return;
		}
		if (Number(price) < 0) {
			(window as any).showSnackbar("Price cannot be negative.", "error");
			return;
		}

		modifyPantryItem({
			...ingredient,
			quantity: Number(quantity),
			expirationDate,
			cost: Math.trunc(Number(price) * 100) / 100,
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
							onChange={(e) => {
								setQuantity(e.target.value);

								const newQuantity = Number(e.target.value);
								const originalQuantity = ingredient.quantity;
								const originalCost = ingredient.cost;

								if (
									originalQuantity &&
									originalCost !== undefined &&
									!isNaN(newQuantity) &&
									newQuantity > 0
								) {
									setPrice(((originalCost / originalQuantity) * newQuantity).toFixed(2));
								}
							}}
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
					<div className="flex flex-col gap-1">
						<label htmlFor="edit-price" className="text-xs text-gray-400">
							Price (EUR)
						</label>
						<input
							id="edit-price"
							type="number"
							min="0"
							step="0.01"
							value={price}
							onChange={(e) => setPrice(e.target.value)}
							readOnly={!isEditing}
							disabled={!isEditing}
							className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-semibold text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						/>
					</div>
					<div className="flex items-center self-end pb-2">
						<p className="text-xs text-gray-400 italic">Auto-estimated from quantity, but adjustable</p>
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
								onClick={handleCancel}
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
								<PencilIcon />
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
								<BinIcon />
								Remove
							</button>
						</>
					)}
				</div>
			</div>
		</Modal>
	);
}
