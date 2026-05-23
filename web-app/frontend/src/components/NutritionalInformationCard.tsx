import type { NutritionalInformation } from "../types";

interface NutritionalInformationCardProps {
	nutritionalInformation: NutritionalInformation;
}

const ROWS: { label: string; key: keyof NutritionalInformation; unit: string; format: (v: number) => string }[][] = [
	[
		{ label: "Calories", key: "calories", unit: "kcal", format: (value) => String(Math.round(value)) },
		{ label: "Carbohydrates", key: "carbohydrates", unit: "g", format: (value) => value.toFixed(1) },
		{ label: "Sugar", key: "sugar", unit: "g", format: (value) => value.toFixed(1) },
		{ label: "Protein", key: "protein", unit: "g", format: (value) => value.toFixed(1) },
	],
	[
		{ label: "Fat", key: "fat", unit: "g", format: (value) => value.toFixed(1) },
		{ label: "Saturated Fat", key: "saturated_fat", unit: "g", format: (value) => value.toFixed(1) },
		{ label: "Fiber", key: "fiber", unit: "g", format: (value) => value.toFixed(1) },
		{ label: "Sodium", key: "sodium", unit: "mg", format: (value) => value.toFixed(0) },
	],
];

export default function NutritionalInformationCard({ nutritionalInformation }: NutritionalInformationCardProps) {
	return (
		<div className="space-y-2">
			{ROWS.map((row) => (
				<div key={row[0].key} className="grid grid-cols-4 gap-2 rounded-lg bg-gray-50 p-3 text-center text-xs">
					{row.map(({ label, key, unit, format }) => (
						<div key={label}>
							<p className="font-semibold text-gray-800">
								{format((nutritionalInformation[key] as number) ?? 0)}
								<span className="font-normal text-gray-400">{unit}</span>
							</p>
							<p className="mt-0.5 text-gray-500">{label}</p>
						</div>
					))}
				</div>
			))}
		</div>
	);
}
