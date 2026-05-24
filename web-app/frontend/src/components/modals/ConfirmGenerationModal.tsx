import Modal from "./Modal";

interface ConfirmGenerationModalProps {
	isOpen: boolean;
	onClose: () => void;
	confirmWarnings: string[];
	generateMealPlan: () => void;
}

export default function ConfirmGenerationModal({
	isOpen,
	onClose,
	confirmWarnings,
	generateMealPlan,
}: ConfirmGenerationModalProps) {
	return (
		<Modal title="Before you Continue" isOpen={isOpen} onClose={onClose}>
			<div className="flex flex-col gap-4">
				<ul className="flex flex-col gap-2">
					{confirmWarnings.map((warning) => (
						<li
							key={warning}
							className="flex items-start gap-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2.5 text-sm text-amber-800"
						>
							<span className="mt-0.5 shrink-0">⚠️</span>
							{warning}
						</li>
					))}
				</ul>
				<p className="text-sm text-gray-500">
					You can still generate a meal plan, but the results may not match your needs.
				</p>
				<div className="flex justify-end gap-2">
					<button
						className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
						onClick={onClose}
					>
						Cancel
					</button>
					<button
						className="bg-sage-600 hover:bg-sage-800 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors"
						onClick={() => {
							onClose();
							generateMealPlan();
						}}
					>
						Generate Anyway
					</button>
				</div>
			</div>
		</Modal>
	);
}
