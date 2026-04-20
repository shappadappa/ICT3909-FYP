export const enum IngredientGroupEnum {
	PRODUCE = "Produce",
	DAIRY = "Dairy",
	PROTEINS = "Proteins",
	GRAINS = "Grains",
	CONDIMENTS = "Condiments",
}

export type IngredientGroup = `${IngredientGroupEnum}`;
