import { DietaryTag } from "../../types";
import Badge from "./Badge";

interface DietaryTagBadgeProps {
	dietaryTag: DietaryTag;
}

const DIETARY_TAG_STYLES: Record<DietaryTag, string> = {
	[DietaryTag.GlutenFree]: "bg-amber-50 text-amber-700 border-amber-200",
	[DietaryTag.LactoseFree]: "bg-blue-50 text-blue-700 border-blue-200",
	[DietaryTag.Vegetarian]: "bg-green-50 text-green-700 border-green-200",
	[DietaryTag.Vegan]: "bg-purple-50 text-purple-700 border-purple-200",
};

const DIETARY_TAG_LABELS: Record<DietaryTag, string> = {
	[DietaryTag.GlutenFree]: "Gluten Free",
	[DietaryTag.LactoseFree]: "Lactose Free",
	[DietaryTag.Vegetarian]: "Vegetarian",
	[DietaryTag.Vegan]: "Vegan",
};

export default function DietaryTagBadge({ dietaryTag }: DietaryTagBadgeProps) {
	return <Badge label={DIETARY_TAG_LABELS[dietaryTag]} additionalClasses={DIETARY_TAG_STYLES[dietaryTag]} />;
}
