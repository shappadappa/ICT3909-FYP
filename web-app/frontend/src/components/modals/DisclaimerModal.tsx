import Modal from "./Modal";

export default function DisclaimerModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
	return (
		<Modal title="Disclaimer" isOpen={isOpen} onClose={onClose}>
			<p className="my-4 text-sm">
				This project was developed by Michael Farrugia at the University of Malta as part of the Final Year
				Project for the Bachelor of Science in Artificial Intelligence (study unit code ICT3909).
			</p>
			<p className="my-4 text-sm">
				The project is intended to be a prototype for the developed system. Ingredients, recipes, and dietary
				restrictions or allergens may not be fully accurate, therefore the system should not be relied solely
				upon for dietary or nutritional advice. Make sure to re-review the generated meal plans before taking
				any further action.
			</p>
			<p className="my-4 text-sm">
				To begin planning meals, you are encouraged to set your preferences and add pantry entries to improve
				the quality of suggestions. Given the current implementation, recipes suggested are designed for one
				serving only.
			</p>
			<a
				className="my-4 text-sm text-blue-500 underline"
				href="https://github.com/shappadappa/ICT3909-FYP"
				target="_blank"
			>
				The GitHub repository is available online.
			</a>
		</Modal>
	);
}
