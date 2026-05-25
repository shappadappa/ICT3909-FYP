export default function BurgerMenuIcon({
	width = 16,
	height = 16,
	colour = "white",
}: {
	width?: number;
	height?: number;
	colour?: string;
}) {
	return (
		<svg width={width} height={height} fill="none" viewBox="0 0 24 24" stroke={colour} strokeWidth="2">
			<path strokeLinecap="round" strokeLinejoin="round" d="M3 3h18M3 9h18M3 15h18M3 21h18" />
		</svg>
	);
}
