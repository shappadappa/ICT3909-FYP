import os

import faiss
import pandas as pd

from food_data_extraction.Embedding import Embedding


class FoodEmbedding(Embedding):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodEmbedding` class is responsible for creating embeddings for food
        descriptions and allowing for similarity search based on those embeddings.
        It also provides functionality to retrieve nutritional information for specific
        food items

        The usage of this embedding allows to bypass the API limitations of 1000
        requests per hour by precomputing the embeddings for all food items and storing
        them in a FAISS index, which can be searched efficiently without making API
        calls. This allows for fast retrieval of similar food items based on their
        descriptions, as well as access to their nutritional information without hitting
        API rate limits

        :param model_name: the name of the sentence transformer model to use for creating
        embeddings (default = "all-MiniLM-L6-v2")
        :type model_name: str
        """

        super().__init__(model_name)

        self.food = pd.read_csv(
            f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/food.csv"
        )
        self.food_nutrient = pd.read_csv(
            f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/food_nutrient.csv"
        )
        self.nutrient = pd.read_csv(
            f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/nutrient.csv"
        ).drop_duplicates(subset=["id"])
        self.food_portion = pd.read_csv(
            f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/food_portion.csv"
        )

    def initialise(self, descriptions: list[str] | None = None):
        """
        Initialise the embeddings for the food descriptions

        :param descriptions: the list of descriptions to create embeddings for (if None,
        the method will use the ingredient names from the food densities DataFrame)
        :type descriptions: list[str] | None
        """

        if descriptions is None:
            descriptions = self.food["description"].tolist()

        super().initialise(descriptions)

    def search(
        self,
        query: str,
        data: pd.DataFrame | None = None,
        top_n: int = 5,
        minimum_confidence: float = 0.0,
    ) -> pd.DataFrame:
        """
        Search for similar food items based on a query string

        :param query: the query string to search for
        :type query: str
        :param data: the DataFrame containing the food items to search through (if None, the method will use the food DataFrame)
        :type data: pd.DataFrame | None
        :param top_n: the number of top results to return (default = 5)
        :type top_n: int
        :param minimum_confidence: the minimum confidence score for a search result to
        be considered valid (default = 0.0)
        :type minimum_confidence: float

        :returns: a DataFrame containing the top N most similar food items, along with
        their similarity scores
        :rtype: pd.DataFrame
        """

        if data is None:
            data = self.food

        query_embedding = self.model.encode([query], convert_to_numpy=True).astype(
            "float32"
        )
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, 1000)  # type: ignore

        results = data.iloc[indices[0]].copy()
        results["score"] = scores[0]
        results = results[results["score"] >= minimum_confidence]

        foundation_results = results[results["data_type"] == "foundation_food"]
        sr_legacy_results = results[results["data_type"] == "sr_legacy_food"]

        foundation_results = foundation_results[foundation_results["score"] >= 0.7]
        sr_legacy_results = sr_legacy_results[sr_legacy_results["score"] >= 0.7]

        # if there are not top_n results from foundation food or SR legacy food, then add the top results from the other data types until we have top_n results
        priority_results = pd.concat(
            [foundation_results, sr_legacy_results]
        ).sort_values("score", ascending=False)

        if len(priority_results) >= top_n:
            return priority_results.head(top_n)

        # fill remaining slots with other data types, sorted by score
        remaining = top_n - len(priority_results)
        other_results = results[
            ~results["data_type"].isin(["foundation_food", "sr_legacy_food"])
        ]
        other_results = other_results.sort_values("score", ascending=False).head(
            remaining
        )

        return pd.concat([priority_results, other_results]).head(top_n)

    def get_nutritional_information(self, fdc_id: int) -> pd.DataFrame:
        """
        Get the nutritional information for a specific food item

        :param fdc_id: the ID of the food item
        :type fdc_id: int

        :returns: a DataFrame containing the nutritional information for the specified food item
        :rtype: pd.DataFrame
        """

        raw_nutrient_info = self.food_nutrient[self.food_nutrient["fdc_id"] == fdc_id]

        nutrient_info = raw_nutrient_info.merge(
            self.nutrient, left_on="nutrient_id", right_on="id", how="left"
        )

        return nutrient_info[["nutrient_id", "amount", "unit_name", "name"]]

    def get_portion_size(self, fdc_id: int) -> pd.DataFrame:
        """
        Get the portion size information for a specific food item

        :param fdc_id: the ID of the food item
        :type fdc_id: int

        :returns: a DataFrame containing the portion size information for the specified food item
        :rtype: pd.DataFrame
        """

        portion = self.food_portion[self.food_portion["fdc_id"] == fdc_id]

        return portion

    def save(self, index_path: str = "food_embedding.faiss"):
        """
        Saves the FAISS index to disk

        :param index_path: the file path to save the FAISS index to (default = "food_embedding.faiss")
        :type index_path: str
        """

        super().save(index_path)
