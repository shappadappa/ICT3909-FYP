export default function PencilIcon({ width = 13, height = 13 }: { width?: number; height?: number }) {
	return (
		<svg width={width} height={height} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
			<path
				strokeLinecap="round"
				strokeLinejoin="round"
				d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a2 2 0 01-1.414.586H9v-2a2 2 0 01.586-1.414z"
			/>
		</svg>
	);
}
