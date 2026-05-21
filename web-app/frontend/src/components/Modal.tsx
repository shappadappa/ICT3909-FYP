import type { ReactNode } from "react";

interface ModalProps {
	title: string;
	isOpen: boolean;
	onClose: () => void;
	children: ReactNode;
}

export default function Modal({ title, isOpen, onClose, children }: ModalProps) {
	return (
		<div
			className={`fixed inset-0 z-[60] ${isOpen ? "flex" : "hidden"} items-center justify-center bg-black/50`}
			onClick={onClose}
		>
			<div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
				<div className="mb-4 flex items-center justify-between">
					<h2 className="text-xl font-semibold text-gray-800 capitalize">{title}</h2>
					<button
						className="cursor-pointer text-gray-400 hover:text-gray-600"
						onClick={() => {
							onClose();
						}}
					>
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

				{children}
			</div>
		</div>
	);
}
