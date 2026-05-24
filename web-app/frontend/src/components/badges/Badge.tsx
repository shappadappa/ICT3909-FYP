export default function Badge({ label, additionalClasses }: { label: string; additionalClasses?: string }) {
	return (
		<span
			className={`rounded-full border px-2 py-0.5 text-xs font-medium ${additionalClasses ?? "border-gray-200 bg-gray-100 text-gray-600"}`}
		>
			{label}
		</span>
	);
}
