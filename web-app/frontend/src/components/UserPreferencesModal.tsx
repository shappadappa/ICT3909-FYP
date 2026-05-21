import { useEffect, useState } from "react";
import Modal from "./Modal";

const STORAGE_KEY = "user-preferences";

interface UserPreferencesProps {
	isOpen: boolean;
	onClose: () => void;
}

interface Preferences {
	calories: string;
	protein: string;
	glutenIntolerant: boolean;
	lactoseIntolerant: boolean;
}

const DEFAULT_PREFERENCES: Preferences = {
	calories: "",
	protein: "",
	glutenIntolerant: false,
	lactoseIntolerant: false,
};

function validate(calories: string, protein: string): string | null {
	if (!calories) return "Caloric intake is required.";
	if (!protein) return "Protein intake is required.";
	if (Number.isNaN(Number(calories)) || Number(calories) < 0) return "Caloric intake must be a non-negative number.";
	if (Number.isNaN(Number(protein)) || Number(protein) < 0) return "Protein intake must be a non-negative number.";
	return null;
}

export default function UserPreferencesModal({ isOpen, onClose }: UserPreferencesProps) {
	const [prefs, setPrefs] = useState<Preferences>(DEFAULT_PREFERENCES);

	useEffect(() => {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			const parsed = JSON.parse(saved);
			setPrefs({
				calories: parsed.calories ?? "",
				protein: parsed.protein ?? "",
				glutenIntolerant: parsed.glutenIntolerant ?? false,
				lactoseIntolerant: parsed.lactoseIntolerant ?? false,
			});
		}
	}, []);

	const handleSubmit = (e: React.SyntheticEvent<HTMLFormElement>) => {
		e.preventDefault();
		const error = validate(prefs.calories, prefs.protein);
		if (error) {
			(globalThis as any).showSnackbar(error, "error");
			return;
		}
		localStorage.setItem(
			STORAGE_KEY,
			JSON.stringify({
				calories: Number(prefs.calories),
				protein: Number(prefs.protein),
				glutenIntolerant: prefs.glutenIntolerant,
				lactoseIntolerant: prefs.lactoseIntolerant,
			})
		);
		onClose();
		(globalThis as any).showSnackbar("Preferences saved successfully!", "success");
	};

	return (
		<Modal title="User Preferences" isOpen={isOpen} onClose={onClose}>
			<form className="flex flex-col gap-5" onSubmit={handleSubmit}>
				<fieldset className="flex flex-col gap-2">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Dietary Restrictions
					</legend>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="gluten-intolerant"
							checked={prefs.glutenIntolerant}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPrefs((p) => ({ ...p, glutenIntolerant: e.target.checked }))}
						/>
						<span className="text-sm text-gray-700">Gluten-intolerant / Celiac</span>
					</label>

					<label className="hover:bg-sage-50 flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 px-3 py-2.5">
						<input
							type="checkbox"
							name="lactose-intolerant"
							checked={prefs.lactoseIntolerant}
							className="accent-sage-600 h-4 w-4 cursor-pointer rounded"
							onChange={(e) => setPrefs((p) => ({ ...p, lactoseIntolerant: e.target.checked }))}
						/>
						<span className="text-sm text-gray-700">Lactose-intolerant</span>
					</label>
				</fieldset>

				<fieldset className="flex flex-col gap-3">
					<legend className="mb-1 text-xs font-semibold tracking-wide text-gray-400 uppercase">
						Daily targets
					</legend>

					<div className="flex flex-col gap-1">
						<label htmlFor="calories" className="text-sm font-medium text-gray-600">
							Caloric intake
						</label>
						<div className="relative">
							<input
								type="number"
								id="calories"
								name="calories"
								min="0"
								placeholder="2000"
								value={prefs.calories}
								className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-12 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
								onChange={(e) => setPrefs((p) => ({ ...p, calories: e.target.value }))}
							/>
							<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
								kcal
							</span>
						</div>
					</div>

					<div className="flex flex-col gap-1">
						<label htmlFor="protein" className="text-sm font-medium text-gray-600">
							Protein intake
						</label>
						<div className="relative">
							<input
								type="number"
								id="protein"
								name="protein"
								min="0"
								placeholder="50"
								value={prefs.protein}
								className="focus:border-sage-400 w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pr-12 pl-3 text-sm text-gray-800 outline-none focus:bg-white"
								onChange={(e) => setPrefs((p) => ({ ...p, protein: e.target.value }))}
							/>
							<span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-xs text-gray-400">
								g
							</span>
						</div>
					</div>
				</fieldset>

				<button
					type="submit"
					className="bg-sage-600 hover:bg-sage-800 mt-1 w-full rounded-lg py-2 text-sm font-medium text-white transition-colors"
				>
					Save preferences
				</button>
			</form>
		</Modal>
	);
}
