import { useEffect, useState, useSyncExternalStore } from "react";
import type { Ingredient } from "../types";
import { DietaryTag } from "../types";
import Modal from "./Modal";
import NutritionalInformationCard from "./NutritionalInformationCard";
import DietaryTagBadge from "./DietaryTagBadge";
import { addPantryItem, pantryStore } from "../stores/pantry";

interface AddIngredientModalProps {
	isOpen: boolean;
	onClose: () => void;
}

const fetchAllIngredients = async () => {
	const res = await fetch("http://localhost:8000/api/ingredients");
	if (!res.ok) throw new Error("Failed to fetch ingredients");

	const rawIngredients = await res.json();

	const ingredients: Ingredient[] = rawIngredients.map(
		(ingredient: any): Ingredient => ({
			...ingredient,
			nutritionalInformation: ingredient.nutritional_information,
		})
	);

	return ingredients;
};

export default function AddIngredientModal({ isOpen, onClose }: AddIngredientModalProps) {
	const pantryIngredients = useSyncExternalStore(pantryStore.subscribe, pantryStore.get, () => []);
	const [allIngredients, setAllIngredients] = useState<Ingredient[]>([]);
	const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
	const [query, setQuery] = useState("");
	const [quantity, setQuantity] = useState("");
	const [expirationDate, setExpirationDate] = useState("");

	useEffect(() => {
		fetchAllIngredients().then(setAllIngredients).catch(console.error);
	}, []);

	const filtered = query.trim()
		? allIngredients.filter((i) => i.name.toLowerCase().includes(query.trim().toLowerCase()))
		: [];

	const handleSubmit = (e: React.SubmitEvent) => {
		e.preventDefault();

		if (!selectedIngredient) {
			(window as any).showSnackbar("Please select an ingredient.", "error");
			return;
		}

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

		if (pantryIngredients.some((ingredient) => ingredient.id === selectedIngredient.id)) {
			(window as any).showSnackbar("Ingredient already in pantry. Please edit the existing item.", "error");
			return;
		}

		addPantryItem({ ...selectedIngredient, quantity: Number(quantity), expirationDate });

		setSelectedIngredient(null);
		setQuery("");
		setQuantity("");
		setExpirationDate("");
		onClose();
	};

	return (
		<Modal
			title="Add Pantry Item"
			isOpen={isOpen}
			onClose={() => {
				onClose();
				setSelectedIngredient(null);
				setQuery("");
				setQuantity("");
				setExpirationDate("");
			}}
		>
			<div className="flex flex-col gap-3">
				<div className="relative">
					<div className="flex w-full items-center rounded-md border border-gray-300 px-3 py-2 text-sm focus-within:ring-2 focus-within:ring-blue-500">
						<input
							type="text"
							placeholder="Start typing to search ingredients"
							value={query}
							onChange={(e) => setQuery(e.target.value)}
							className="flex-1 focus:outline-none"
						/>
						{query && (
							<button
								onClick={() => setQuery("")}
								className="ml-2 cursor-pointer text-gray-400 hover:text-gray-600"
							>
								<svg
									width="18"
									height="18"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									strokeWidth="2"
								>
									<path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						)}
					</div>

					{query.trim() && query.length > 2 && (
						<ul className="absolute top-full left-0 z-10 mt-1 max-h-60 w-full overflow-y-auto rounded-md border border-gray-200 bg-white shadow-md">
							{filtered.length > 0 ? (
								filtered.map((ingredient) => (
									<li key={ingredient.id}>
										<button
											type="button"
											className="w-full cursor-pointer px-3 py-2 text-left text-sm text-gray-700 capitalize hover:bg-gray-100"
											onClick={() => {
												setQuery("");

												if (
													pantryIngredients.some(
														(pantryIngredient) => pantryIngredient.id === ingredient.id
													)
												) {
													(window as any).showSnackbar(
														"Ingredient already in pantry. Please edit the existing item.",
														"error"
													);
													return;
												}

												setSelectedIngredient(ingredient);
												setQuantity("");
												setExpirationDate("");
											}}
										>
											{ingredient.name}
										</button>
									</li>
								))
							) : (
								<li className="px-3 py-2 text-sm text-gray-400">No ingredients found</li>
							)}
						</ul>
					)}
				</div>

				{selectedIngredient && (
					<form
						className="flex flex-col gap-4 rounded-lg border border-gray-200 bg-gray-50 p-4"
						onSubmit={handleSubmit}
					>
						<h2 className="text-base font-semibold text-gray-800 capitalize">{selectedIngredient.name}</h2>

						<div className="grid grid-cols-2 gap-3">
							<div className="flex flex-col gap-1">
								<label htmlFor="quantity" className="text-xs font-medium text-gray-500">
									Quantity (g)
								</label>
								<input
									id="quantity"
									type="number"
									min="0"
									placeholder="e.g 500"
									value={quantity}
									onChange={(e) => setQuantity(e.target.value)}
									required
									className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
								/>
							</div>
							<div className="flex flex-col gap-1">
								<label htmlFor="expiration-date" className="text-xs font-medium text-gray-500">
									Expiration Date
								</label>
								<input
									id="expiration-date"
									type="date"
									value={expirationDate}
									onChange={(e) => setExpirationDate(e.target.value)}
									required
									className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
								/>
							</div>
						</div>

						<div className="flex flex-col gap-2">
							<h3 className="text-xs font-semibold tracking-wide text-gray-500 uppercase">
								Nutritional Information <span className="font-normal normal-case">(per 100g)</span>
							</h3>

							<NutritionalInformationCard
								nutritional_information={selectedIngredient.nutritionalInformation}
							/>

							<div className="flex flex-wrap gap-2 pt-1">
								{selectedIngredient.nutritionalInformation.is_gluten_free && (
									<DietaryTagBadge dietaryTag={DietaryTag.GlutenFree} />
								)}
								{selectedIngredient.nutritionalInformation.is_lactose_free && (
									<DietaryTagBadge dietaryTag={DietaryTag.LactoseFree} />
								)}
								{selectedIngredient.nutritionalInformation.is_vegetarian && (
									<DietaryTagBadge dietaryTag={DietaryTag.Vegetarian} />
								)}
								{selectedIngredient.nutritionalInformation.is_vegan && (
									<DietaryTagBadge dietaryTag={DietaryTag.Vegan} />
								)}
							</div>
						</div>

						<button
							type="submit"
							className="cursor-pointer rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
						>
							Add to Pantry
						</button>
					</form>
				)}
			</div>
		</Modal>
	);
}
