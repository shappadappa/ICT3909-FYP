import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

folders = ["FoodData_Central_foundation_food_csv_2025-12-18", "FoodData_Central_sr_legacy_food_csv_2018-04", "FoodData_Central_survey_food_csv_2024-10-31"]

class FoodEmbedding():
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodEmbedding` class is responsible for creating embeddings for food descriptions and allowing for similarity search based on those embeddings. It also provides functionality to retrieve nutritional information for specific food items

        The usage of this embedding allows to bypass the API limitations of 1000 requests per hour by precomputing the embeddings for all food items and storing them in a FAISS index, which can be searched efficiently without making API calls. This allows for fast retrieval of similar food items based on their descriptions, as well as access to their nutritional information without hitting API rate limits
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.food = pd.concat([pd.read_csv(f"{os.path.join(base_dir, folder)}/food.csv") for folder in folders], ignore_index = True)
        self.food_nutrient = pd.concat([pd.read_csv(f"{os.path.join(base_dir, folder)}/food_nutrient.csv") for folder in folders], ignore_index = True)
        self.nutrient = pd.concat([pd.read_csv(f"{os.path.join(base_dir, folder)}/nutrient.csv") for folder in folders], ignore_index = True).drop_duplicates(subset = ["id"])

        self.model = SentenceTransformer(model_name, token = "test")

    def initialise(self):
        """
        Initialise the embeddings for the food descriptions
        """

        self.descriptions = self.food ["description"].tolist()
        self.embeddings = self.model.encode(self.descriptions, show_progress_bar = True, convert_to_numpy = True, batch_size = 64).astype("float32")

        self.index = faiss.IndexFlatIP(self.embeddings.shape [1])
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

    def search(self, query: str, top_n: int = 5) -> pd.DataFrame:
        """
        Search for similar food items based on a query string

        :param query: the query string to search for
        :type query: str
        :param top_n: the number of top results to return (default = 5)
        :type top_n: int

        :returns: a DataFrame containing the top N most similar food items, along with their similarity scores
        :rtype: pd.DataFrame
        """

        query_embedding = self.model.encode([query], convert_to_numpy = True).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, k = top_n)

        results = self.food.iloc [indices [0]].copy()

        results ["score"] = scores [0]

        return results
    
    def get_nutritional_info(self, fdc_id: int) -> pd.DataFrame:
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

    def load(self, index_path: str, food_path: str):
        """
        Loads the FAISS index and the food data from disk
        """

        self.index = faiss.read_index(index_path)
        self.food = pd.read_parquet(food_path)

    def save(self):
        """
        Saves the FAISS index and the food data to disk
        """

        faiss.write_index(self.index, "fdc_index.faiss")
        self.food.to_parquet("foods.parquet")