import os

import pandas as pd

from food_data_extraction.Embedding import Embedding

DEFAULT_MINIMUM_CONFIDENCE = 0.7


class FoodDensityEmbedding(Embedding):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodDensityEmbedding` class, similar to the `FoodEmbedding` class, is responsible for creating an embedding
        for foods, but with a specific focus on incorporating density information for the food items, thereby allowing
        similarity search based on both the textual descriptions and the density values of the food items.

        :param model_name: the name of the sentence transformer model to use for creating embeddings (default = "all-
            MiniLM-L6-v2")
        :type model_name: str
        """

        super().__init__(model_name)

        self.food_densities = pd.read_csv(os.path.join(self.base_dir, "ingredient_densities.csv"))

    def initialise(self, descriptions: list[str] | None = None):
        """
        Initialise the embeddings for the foods, incorporating density information.

        :param descriptions: the list of descriptions to create embeddings for (if None, the method will use the
            ingredient names from the food densities DataFrame)
        :type descriptions: list[str] | None
        """

        if descriptions is None:
            descriptions = self.food_densities["ingredient"].tolist()

        super().initialise(descriptions)

    def search(
        self,
        query: str,
        data: pd.DataFrame | None = None,
        top_n: int = 5,
        minimum_confidence: float = DEFAULT_MINIMUM_CONFIDENCE,
    ) -> pd.DataFrame:
        """
        Search for similar food items based on a query that incorporates both textual description and density
        information.

        :param query: the search query, which can include both textual description and density information
        :type query: str
        :param data: the DataFrame containing the food items to search through (if None, the method will use the food
            densities DataFrame)
        :type data: pd.DataFrame | None
        :param top_n: the number of top similar food items to return (default = 5)
        :type top_n: int
        :param minimum_confidence: the minimum confidence score for a search result to be considered valid (default =
            DEFAULT_MINIMUM_CONFIDENCE)
        :type minimum_confidence: float
        :returns: a DataFrame containing the top similar food items based on the query
        :rtype: pd.DataFrame
        """

        if data is None:
            data = self.food_densities

        return super().search(query, data, top_n, minimum_confidence)

    def save(self, index_path: str = "food_density_embedding.faiss"):
        """
        Saves the FAISS index to disk.

        :param index_path: the file path to save the FAISS index to (default = "food_density_embedding.faiss")
        :type index_path: str
        """

        super().save(index_path)
