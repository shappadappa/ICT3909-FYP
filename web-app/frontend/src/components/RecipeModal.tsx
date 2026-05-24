import type { Recipe } from "../types";
import DietaryTagBadge from "./DietaryTagBadge";
import Modal from "./Modal";
import NutritionalInformationCard from "./NutritionalInformationCard";

interface RecipeModalProps {
	recipe: Recipe | null;
	isError: boolean;
	isOpen: boolean;
	onClose: () => void;
}

export default function RecipeModal({ recipe, isError, isOpen, onClose }: RecipeModalProps) {
	if (!isOpen || !recipe) return null;

	return (
		<Modal title="Recipe Details" isOpen={isOpen} onClose={onClose}>
			{isError ? (
				<div className="py-4 text-center text-sm text-red-500">Failed to load recipe details.</div>
			) : (
				<div className="max-h-[65vh] space-y-4 overflow-y-auto pr-4">
					<div>
						<h3 className="text-base font-semibold text-gray-800">{recipe.name}</h3>
						<div className="mt-1.5 flex flex-wrap gap-1">
							{recipe.dietaryTags?.map((tag) => (
								<DietaryTagBadge key={tag} dietaryTag={tag} />
							))}
						</div>
					</div>

					<div>
						<h4 className="mb-1.5 text-xs font-semibold tracking-wide text-gray-400 uppercase">
							Nutritional Information
						</h4>

						<NutritionalInformationCard nutritionalInformation={recipe.nutritionalInformation} />
					</div>

					<div>
						<h4 className="mb-1.5 text-xs font-semibold tracking-wide text-gray-400 uppercase">
							Estimated Cost
						</h4>
						<p className="text-sm text-gray-700">
							{recipe.estimated_cost ? `€${recipe.estimated_cost.toFixed(2)}` : "N/A"}
						</p>
					</div>

					<div>
						<h4 className="mb-1.5 text-xs font-semibold tracking-wide text-gray-400 uppercase">
							Ingredients
						</h4>
						<ul className="space-y-1 text-sm text-gray-700">
							{recipe.ingredients.map(({ ingredient, quantity }, index) => (
								<li key={ingredient + index} className="flex justify-between gap-4">
									<span className="capitalize">{ingredient}</span>
									<span className="shrink-0 text-gray-400">
										{quantity % 1 === 0 ? quantity : quantity.toFixed(1)}g
									</span>
								</li>
							))}
						</ul>
					</div>

					<div>
						<h4 className="mb-1.5 text-xs font-semibold tracking-wide text-gray-400 uppercase">
							Instructions
						</h4>
						<div className="divide-y divide-gray-100 text-sm leading-relaxed text-gray-700">
							{recipe.instructions.map((instruction, index) => (
								<p key={instruction + index} className="py-2">
									{instruction}
								</p>
							))}
						</div>
					</div>
				</div>
			)}
		</Modal>
	);
}
