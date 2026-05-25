export default function CloseIcon({ width = 18, height = 18 }: { width?: number; height?: number }) {
	return (
		<svg width={width} height={height} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
			<path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
		</svg>
	);
}
