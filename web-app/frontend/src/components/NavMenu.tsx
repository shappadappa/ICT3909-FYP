import { useState } from "react";
import { BurgerMenuIcon, CloseIcon } from "../assets";
import DisclaimerModal from "./modals/DisclaimerModal";
import UserPreferencesModal from "./modals/UserPreferencesModal";

export default function NavMenu() {
	const [isDrawerOpen, setIsDrawerOpen] = useState(false);
	const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
	const [isDisclaimerOpen, setIsDisclaimerOpen] = useState(false);

	const openMenu = () => setIsDrawerOpen(true);
	const closeMenu = () => setIsDrawerOpen(false);

	return (
		<>
			<button className="bg-sage-600 flex h-8 w-8 items-center justify-center rounded-full" onClick={openMenu}>
				<BurgerMenuIcon />
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
				className={`fixed top-0 left-0 z-50 flex h-full w-56 flex-col bg-white shadow-xl transition-transform duration-300 sm:w-64 ${
					isDrawerOpen ? "translate-x-0" : "-translate-x-full"
				}`}
			>
				<div className="border-walnut-100 flex items-center justify-between border-b px-5 py-4">
					<span className="text-walnut-800 font-semibold">Menu</span>
					<button className="text-walnut-400 hover:text-walnut-600" onClick={closeMenu}>
						<CloseIcon />
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
