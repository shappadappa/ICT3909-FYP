export default function ClipboardIcon({
	width = 14,
	height = 14,
	colour = "#4F7A47",
}: {
	width?: number;
	height?: number;
	colour?: string;
}) {
	return (
		<svg width={width} height={height} fill="none" viewBox="0 0 24 24" stroke={colour} strokeWidth="2">
			<path
				strokeLinecap="round"
				strokeLinejoin="round"
				d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
			></path>
		</svg>
	);
}
