import shutil
from pathlib import Path

BACKEND_DIR = Path(__file__).parent
ROOT_DIR = BACKEND_DIR.parent.parent

FILES = {
    ROOT_DIR / "engines" / "best_ga_meal_planner_hyperparameters.json": BACKEND_DIR
    / "best_ga_meal_planner_hyperparameters.json",
    ROOT_DIR / "recipe_extraction" / "supplemented_structured_ingredients.json": BACKEND_DIR
    / "supplemented_structured_ingredients.json",
    ROOT_DIR / "recipe_extraction" / "supplemented_structured_recipes.json": BACKEND_DIR
    / "supplemented_structured_recipes.json",
}

ENGINE_FILES = [
    "GAMealPlanner.py",
    "MealPlanner.py",
    "fitness_score.py",
    "utils.py",
]

ENGINES_INIT = """\
from engines.fitness_score import fitness_score, get_waste_penalty
from engines.GAMealPlanner import GAMealPlanner
from engines.MealPlanner import MealPlanner
from engines.utils import (
    filter_and_add_recipes,
    get_consumed_stock,
    get_ingredient,
    get_pantry_ingredient,
    load_all_ingredients,
    make_pantry,
    make_preferences,
    make_recipe,
    parse_recipes,
)

__all__ = [
    "GAMealPlanner",
    "MealPlanner",
    "fitness_score",
    "get_waste_penalty",
    "filter_and_add_recipes",
    "get_consumed_stock",
    "get_ingredient",
    "get_pantry_ingredient",
    "load_all_ingredients",
    "make_pantry",
    "make_preferences",
    "make_recipe",
    "parse_recipes",
]
"""


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"[SKIP] Source not found: {src}")
        return

    shutil.copy2(src, dst)

    print(f"[OK]   {src.name} -> {dst}")


def copy_package(src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(exist_ok=True)

    for py_file in src_dir.glob("*.py"):
        copy_file(py_file, dst_dir / py_file.name)


def copy_engines(src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(exist_ok=True)
    for filename in ENGINE_FILES:
        copy_file(src_dir / filename, dst_dir / filename)
    (dst_dir / "__init__.py").write_text(ENGINES_INIT)

    print(f"[OK]   engines/__init__.py written")


for src, dst in FILES.items():
    copy_file(src, dst)

copy_package(ROOT_DIR / "models", BACKEND_DIR / "models")
copy_engines(ROOT_DIR / "engines", BACKEND_DIR / "engines")
