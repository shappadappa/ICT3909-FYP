import { useStore } from "@nanostores/react";
import { useState } from "react";
import { CloseIcon } from "../../assets";
import { API_BASE_URL } from "../../config";
import { addPantryItem, pantryStore, preferencesStore } from "../../stores";
import type { Ingredient, UserPreferences } from "../../types";
import { DietaryTag } from "../../types";
import DietaryTagBadge from "../badges/DietaryTagBadge";
import NutritionalInformationCard from "../NutritionalInformationCard";
import Modal from "./Modal";

interface AddIngredientModalProps {
	isOpen: boolean;
	onClose: () => void;
}

const fetchIngredients = async (savedPreferences: UserPreferences, name_query: string) => {
	const params = new URLSearchParams({
		gluten_free: savedPreferences?.glutenIntolerant ? "true" : "false",
		lactose_free: savedPreferences?.lactoseIntolerant ? "true" : "false",
		vegetarian: savedPreferences?.vegetarian ? "true" : "false",
		vegan: savedPreferences?.vegan ? "true" : "false",
		name_query: name_query || "",
	});

	const res = await fetch(`${API_BASE_URL}/api/ingredients?${params.toString()}`);
	if (!res.ok) throw new Error("Failed to fetch ingredients");

	const rawIngredients = await res.json();

	const ingredients: Ingredient[] = rawIngredients.map(
		(ingredient: any): Ingredient => ({
			id: ingredient.id,
			name: ingredient.name,
			nutritionalInformation: ingredient.nutritional_information,
			cost: ingredient.price_per_100g,
		})
	);

	return ingredients;
};

export default function AddIngredientModal({ isOpen, onClose }: AddIngredientModalProps) {
	const pantryIngredients = useStore(pantryStore);
	const savedPreferences = useStore(preferencesStore);

	const hasDietaryRestrictions =
		savedPreferences?.glutenIntolerant ||
		savedPreferences?.lactoseIntolerant ||
		savedPreferences?.vegetarian ||
		savedPreferences?.vegan;

	const [filteredIngredients, setFilteredIngredients] = useState<Ingredient[]>([]);
	const [isFetchingIngredients, setIsFetchingIngredients] = useState(false);
	const [selectedIngredient, setSelectedIngredient] = useState<Ingredient | null>(null);
	const [query, setQuery] = useState("");
	const [quantity, setQuantity] = useState("");
	const [expirationDate, setExpirationDate] = useState("");
	const [price, setPrice] = useState("");

	const today = new Date();
	today.setHours(0, 0, 0, 0);

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

		if (pantryIngredients.some((ingredient) => ingredient.id === selectedIngredient.id)) {
			(window as any).showSnackbar("Ingredient already in pantry. Please edit the existing item.", "error");
			return;
		}

		addPantryItem({
			...selectedIngredient,
			quantity: Number(quantity),
			expirationDate,
			cost: Math.trunc(Number(price) * 100) / 100,
		});

		setSelectedIngredient(null);
		setQuery("");
		setQuantity("");
		setExpirationDate("");
		setPrice("");
		onClose();
	};

	const handleQueryChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const newValue = e.target?.value || "";
		const oldValue = query;

		setQuery(newValue);

		// to avoid excesive API calls, if there was previously no results, and the user is still adding more characters, don't call the API again
		if (newValue.length > 3 && newValue?.length > oldValue?.length && filteredIngredients.length == 0) {
			return;
		}

		if (newValue.length > 2) {
			setIsFetchingIngredients(true);

			const newFilteredIngredients = await fetchIngredients(savedPreferences, newValue);

			setFilteredIngredients(newFilteredIngredients);
			setIsFetchingIngredients(false);
		} else {
			setFilteredIngredients([]);
		}
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
				setPrice("");
			}}
		>
			<div className="flex flex-col gap-3">
				<div className="relative">
					{hasDietaryRestrictions && (
						<div className="mb-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2.5 text-sm text-amber-800">
							⚠️ Please check your dietary preferences if you can't find the ingredient you are looking
							for.
						</div>
					)}

					<div className="flex w-full items-center rounded-md border border-gray-300 px-3 py-2 text-sm focus-within:ring-2 focus-within:ring-blue-500">
						<input
							type="text"
							placeholder="Start typing to search ingredients"
							value={query}
							onChange={handleQueryChange}
							className="flex-1 focus:outline-none"
						/>
						{query && (
							<button onClick={() => setQuery("")} className="ml-2 text-gray-400 hover:text-gray-600">
								<CloseIcon />
							</button>
						)}
					</div>

					{query.trim() && query.length > 2 && (
						<ul className="absolute top-full left-0 z-10 mt-1 max-h-60 w-full overflow-y-auto rounded-md border border-gray-200 bg-white shadow-md">
							{filteredIngredients.length > 0 &&
								filteredIngredients.map((ingredient) => (
									<li key={ingredient.id}>
										<button
											type="button"
											className="w-full px-3 py-2 text-left text-sm text-gray-700 capitalize hover:bg-gray-100"
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
												setPrice("");
											}}
										>
											{ingredient.name}
										</button>
									</li>
								))}{" "}
							{filteredIngredients.length === 0 && !isFetchingIngredients && (
								<li className="px-3 py-2 text-sm text-gray-400">
									No ingredients found
									{hasDietaryRestrictions &&
										". You may need to adjust your dietary preferences to find the ingredients you are looking for."}
								</li>
							)}
							{isFetchingIngredients && <li className="px-3 py-2 text-sm text-gray-400">Searching...</li>}
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
									onChange={(e) => {
										setQuantity(e.target.value);

										const numericValue = Number(e.target.value);

										if (!isNaN(numericValue) && selectedIngredient.cost !== undefined) {
											const calculatedPrice = (numericValue / 100) * selectedIngredient.cost;
											setPrice(calculatedPrice.toFixed(2));
										} else {
											setPrice("");
										}
									}}
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
							<div className="flex flex-col gap-1">
								<label htmlFor="price" className="text-xs font-medium text-gray-500">
									Price (EUR)
								</label>
								<input
									id="price"
									type="number"
									min="0"
									step="0.01"
									placeholder="e.g. 2.99"
									value={price}
									onChange={(e) => setPrice(e.target.value)}
									required
									className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
								/>
							</div>
							<div className="flex items-center self-end pb-2">
								<p className="text-xs text-gray-400 italic">
									Auto-estimated from quantity, but adjustable
								</p>
							</div>
						</div>

						<div className="flex flex-col gap-2">
							<h3 className="text-xs font-semibold tracking-wide text-gray-500 uppercase">
								Nutritional Information <span className="font-normal normal-case">(per 100g)</span>
							</h3>

							<NutritionalInformationCard
								nutritionalInformation={selectedIngredient.nutritionalInformation}
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
							className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
						>
							Add to Pantry
						</button>
					</form>
				)}
			</div>
		</Modal>
	);
}
