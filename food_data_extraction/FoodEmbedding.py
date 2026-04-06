import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

class FoodEmbedding():
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodEmbedding` class is responsible for creating embeddings for food descriptions and allowing for similarity search based on those embeddings. It also provides functionality to retrieve nutritional information for specific food items

        The usage of this embedding allows to bypass the API limitations of 1000 requests per hour by precomputing the embeddings for all food items and storing them in a FAISS index, which can be searched efficiently without making API calls. This allows for fast retrieval of similar food items based on their descriptions, as well as access to their nutritional information without hitting API rate limits

        :param model_name: the name of the sentence transformer model to use for creating embeddings (default = "all-MiniLM-L6-v2")
        :type model_name: str
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.food = pd.read_csv(f"{os.path.join(base_dir, 'FoodData_Central_csv_2025-12-18')}/food.csv")
        self.food_nutrient = pd.read_csv(f"{os.path.join(base_dir, 'FoodData_Central_csv_2025-12-18')}/food_nutrient.csv")
        self.nutrient = pd.read_csv(f"{os.path.join(base_dir, 'FoodData_Central_csv_2025-12-18')}/nutrient.csv").drop_duplicates(subset = ["id"])

        self.model = SentenceTransformer(model_name, token = "test") # todo pass token

        self.search_cache = {}

    # def _normalize_description(self, description: str) -> str:
    #     """
    #     Converts a comma-separated FDC description into natural word order so that it aligns better with the queries

    #     :param description: the original FDC description to normalize
    #     :type description: str

    #     :returns: the normalized description with words in natural order
    #     :rtype: str
    #     """

    #     try:
    #         return description.replace(",", " ")
    #     except Exception:
    #         return description

    def initialise(self):
        """
        Initialise the embeddings for the food descriptions
        """

        descriptions = self.food ["description"].tolist()
        # normalized_descriptions = [self._normalize_description(description) for description in self.descriptions]
        # self.embeddings = self.model.encode(normalized_descriptions, show_progress_bar = True, convert_to_numpy = True, batch_size = 64).astype("float32")
        embeddings = self.model.encode(descriptions, show_progress_bar = True, convert_to_numpy = True, batch_size = 64).astype("float32")

        self.index = faiss.IndexFlatIP(embeddings.shape [1])
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

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

        if self.search_cache.get(query) is not None:
            return self.search_cache [query]

        # normalized_query = self._normalize_description(query)
        # query_embedding = self.model.encode([normalized_query], convert_to_numpy = True).astype("float32")
        query_embedding = self.model.encode([query], convert_to_numpy = True).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, k = top_n)

        results = self.food.iloc [indices [0]].copy()

        results ["score"] = scores [0]

        self.search_cache [query] = results

        return results
    
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

    def load(self, index_path: str):
        """
        Loads the FAISS index from disk
        """

        self.index = faiss.read_index(index_path)

    def save(self):
        """
        Saves the FAISS index to disk
        """

        faiss.write_index(self.index, "food_embedding.faiss")