import { useState } from "react";
import DisclaimerModal from "./DisclaimerModal";

export default function OnboardingModal() {
	const [isOpen, setIsOpen] = useState(true);

	const handleClose = () => {
		fetch("/api/onboarding", { method: "POST" }).finally(() => setIsOpen(false));
	};

	return <DisclaimerModal isOpen={isOpen} onClose={handleClose} />;
}
