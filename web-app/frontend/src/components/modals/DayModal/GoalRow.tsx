interface GoalRowProps {
	readonly label: string;
	readonly actual: number;
	readonly target: number;
	readonly diff: number;
	readonly unit: string;
	readonly higherIsBetter: boolean;
}

const formatDiffValue = (absVal: number, unit: string): string => {
	return unit === "kcal" ? String(Math.round(absVal)) : absVal.toFixed(1);
};

export function GoalRow({ label, actual, target, diff, unit, higherIsBetter }: GoalRowProps) {
	const percentageReached = Math.min((actual / target) * 100, 100);
	const isOver = diff > 0;
	const isOnTarget = Math.abs(diff / target) <= 0.05; // within 5% of the target

	let barColor = "bg-amber-400";
	if (isOnTarget || (isOver && higherIsBetter)) {
		barColor = "bg-green-400";
	} else if (isOver && !higherIsBetter) {
		barColor = "bg-red-400";
	}

	let diffColor = "text-amber-500";
	if (isOnTarget || (isOver && higherIsBetter)) {
		diffColor = "text-green-600";
	} else if (isOver && !higherIsBetter) {
		diffColor = "text-red-500";
	}

	let diffLabel: string;
	if (isOnTarget) {
		diffLabel = "on target";
	} else if (isOver) {
		diffLabel = `+${formatDiffValue(Math.abs(diff), unit)}${unit} over`;
	} else {
		diffLabel = `${formatDiffValue(Math.abs(diff), unit)}${unit} under`;
	}

	const formatValue = (value: number) => (unit === "kcal" ? String(Math.round(value)) : value.toFixed(1));

	return (
		<div className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2.5">
			<div className="mb-1.5 flex items-baseline justify-between">
				<span className="text-xs font-medium text-gray-600">{label}</span>
				<span className="text-xs text-gray-400">
					{formatValue(actual)} / {formatValue(target)}
					{unit}
					<span className={`ml-2 font-semibold ${diffColor}`}>{diffLabel}</span>
				</span>
			</div>
			<div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
				<div
					className={`h-full rounded-full transition-all ${barColor}`}
					style={{ width: `${percentageReached}%` }}
				/>
			</div>
		</div>
	);
}
