import pandas as pd
import os
from Embedding import Embedding

class FoodEmbedding(Embedding):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodEmbedding` class is responsible for creating embeddings for food descriptions and allowing for similarity search based on those embeddings. It also provides functionality to retrieve nutritional information for specific food items

        The usage of this embedding allows to bypass the API limitations of 1000 requests per hour by precomputing the embeddings for all food items and storing them in a FAISS index, which can be searched efficiently without making API calls. This allows for fast retrieval of similar food items based on their descriptions, as well as access to their nutritional information without hitting API rate limits

        :param model_name: the name of the sentence transformer model to use for creating embeddings (default = "all-MiniLM-L6-v2")
        :type model_name: str
        """

        super().__init__(model_name)

        self.food = pd.read_csv(f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/food.csv")
        self.food_nutrient = pd.read_csv(f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/food_nutrient.csv")
        self.nutrient = pd.read_csv(f"{os.path.join(self.base_dir, 'FoodData_Central_csv_2025-12-18')}/nutrient.csv").drop_duplicates(subset = ["id"])

    def initialise(self, descriptions: list[str] | None = None):
        """
        Initialise the embeddings for the food descriptions

        :param descriptions: the list of descriptions to create embeddings for (if None, the method will use the ingredient names from the food densities DataFrame)
        :type descriptions: list[str] | None
        """

        if descriptions is None:
            descriptions = self.food ["description"].tolist()

        super().initialise(descriptions)

    def search(self, query: str, data: pd.DataFrame | None = None, top_n: int = 5, minimum_confidence: float = 0.0) -> pd.DataFrame:
        """
        Search for similar food items based on a query string

        :param query: the query string to search for
        :type query: str
        :param data: the DataFrame containing the food items to search through (if None, the method will use the food DataFrame)
        :type data: pd.DataFrame | None
        :param top_n: the number of top results to return (default = 5)
        :type top_n: int
        :param minimum_confidence: the minimum confidence score for a search result to be considered valid (default = 0.0)
        :type minimum_confidence: float

        :returns: a DataFrame containing the top N most similar food items, along with their similarity scores
        :rtype: pd.DataFrame
        """

        if data is None:
            data = self.food

        return super().search(query, data, top_n, minimum_confidence)
    
    def get_nutritional_information(self, fdc_id: int) -> pd.DataFrame:
        """
        Get the nutritional information for a specific food item

        :param fdc_id: the ID of the food item
        :type fdc_id: int

        :returns: a DataFrame containing the nutritional information for the specified food item
        :rtype: pd.DataFrame
        """

        raw_nutrient_info = self.food_nutrient [self.food_nutrient ["fdc_id"] == fdc_id]

        nutrient_info = raw_nutrient_info.merge(self.nutrient, left_on = "nutrient_id", right_on = "id", how = "left")

        return nutrient_info [["nutrient_id", "amount", "unit_name", "name"]]

    def save(self, index_path: str = "food_embedding.faiss"):
        """
        Saves the FAISS index to disk

        :param index_path: the file path to save the FAISS index to (default = "food_embedding.faiss")
        :type index_path: str
        """

        super().save(index_path)