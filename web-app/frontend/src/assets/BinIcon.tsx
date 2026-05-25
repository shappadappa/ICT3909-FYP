export default function BinIcon({ width = 13, height = 13 }: { width?: number; height?: number }) {
	return (
		<svg width={width} height={height} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
			<path strokeLinecap="round" strokeLinejoin="round" d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
		</svg>
	);
}
