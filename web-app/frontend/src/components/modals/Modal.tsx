import { useEffect, type ReactNode } from "react";
import { CloseIcon } from "../../assets";

interface ModalProps {
	title: string;
	isOpen: boolean;
	onClose: () => void;
	children: ReactNode;
}

export default function Modal({ title, isOpen, onClose, children }: ModalProps) {
	useEffect(() => {
		document.body.classList.toggle("overflow-hidden", isOpen);

		return () => document.body.classList.remove("overflow-hidden");
	}, [isOpen]);

	return (
		<div
			className={`fixed inset-0 z-[60] ${isOpen ? "flex" : "hidden"} items-center justify-center bg-black/50`}
			onClick={onClose}
		>
			<div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
				<div className="mb-4 flex items-center justify-between">
					<h2 className="text-xl font-semibold text-gray-800 capitalize">{title}</h2>
					<button
						className="text-gray-400 hover:text-gray-600"
						onClick={() => {
							onClose();
						}}
					>
						<CloseIcon />
					</button>
				</div>

				{children}
			</div>
		</div>
	);
}
