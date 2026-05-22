import { useState } from "react";
import UserPreferencesModal from "./UserPreferencesModal";
import DisclaimerModal from "./DisclaimerModal";

export default function NavMenu() {
	const [isDrawerOpen, setIsDrawerOpen] = useState(false);
	const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
	const [isDisclaimerOpen, setIsDisclaimerOpen] = useState(false);

	const openMenu = () => setIsDrawerOpen(true);
	const closeMenu = () => setIsDrawerOpen(false);

	return (
		<>
			<button className="bg-sage-400 flex h-8 w-8 items-center justify-center rounded-full" onClick={openMenu}>
				<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth="2">
					<path strokeLinecap="round" strokeLinejoin="round" d="M3 3h18M3 9h18M3 15h18M3 21h18" />
				</svg>
			</button>
			<button
				type="button"
				aria-label="Close menu"
				className={`fixed inset-0 z-40 w-full bg-black/30 transition-opacity duration-300 ${
					isDrawerOpen ? "opacity-100" : "pointer-events-none opacity-0"
				}`}
				onClick={closeMenu}
			/>
			<aside
				className={`fixed top-0 left-0 z-50 flex h-full w-64 flex-col bg-white shadow-xl transition-transform duration-300 ${
					isDrawerOpen ? "translate-x-0" : "-translate-x-full"
				}`}
			>
				<div className="flex items-center justify-between border-b border-gray-100 px-5 py-4">
					<span className="font-semibold text-gray-800">Menu</span>
					<button className="text-gray-400 hover:text-gray-600" onClick={closeMenu}>
						<svg
							width="18"
							height="18"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							strokeWidth="2"
						>
							<path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				<nav className="flex flex-col px-3 py-3">
					<button
						className="nav-menu-btn"
						onClick={() => {
							closeMenu();
							setIsPreferencesOpen(true);
						}}
					>
						Your Preferences
					</button>
					<button
						className="nav-menu-btn"
						onClick={() => {
							closeMenu();
							setIsDisclaimerOpen(true);
						}}
					>
						Disclaimer
					</button>
				</nav>
			</aside>

			<UserPreferencesModal isOpen={isPreferencesOpen} onClose={() => setIsPreferencesOpen(false)} />
			<DisclaimerModal isOpen={isDisclaimerOpen} onClose={() => setIsDisclaimerOpen(false)} />
		</>
	);
}
