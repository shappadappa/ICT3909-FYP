import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import faiss

"""
PLAN:
- Check the ingredient_densities.csv
- If there is no satisfactory result, consider density = 1
    - Fallback: use the ingredient_parser.convert_to("g") and then use FoodEmbedding
- Otherwise, use this embedding to find the closest ingredient and use its density to convert the volume to mass, and then use FoodEmbedding to find the nutritional information based on the mass
"""

DEFAULT_MINIMUM_CONFIDENCE = 0.7

class FoodDensityEmbedding():
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `FoodDensityEmbedding` class, similar to the `FoodEmbedding` class, is responsible for creating an embedding for foods, but with a specific focus on incorporating density information for the food items, thereby allowing similarity search based on both the textual descriptions and the density values of the food items

        :param model_name: the name of the sentence transformer model to use for creating embeddings (default = "all-MiniLM-L6-v2")
        :type model_name: str
        """

        self.food_densities = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingredient_densities.csv"))

        self.model = SentenceTransformer(model_name, token = "test") # todo pass token

        self.search_cache = {}

    def initialise(self):
        """
        Initialise the embeddings for the foods, incorporating density information
        """

        ingredients = self.food_densities ["ingredient"].tolist()

        embeddings = self.model.encode(ingredients, show_progress_bar = True, convert_to_numpy = True, batch_size = 64).astype("float32")

        self.index = faiss.IndexFlatIP(embeddings.shape [1])
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def search(self, query: str, top_n: int = 5, minimum_confidence: float = DEFAULT_MINIMUM_CONFIDENCE) -> pd.DataFrame:
        """
        Search for similar food items based on a query that incorporates both textual description and density information

        :param query: the search query, which can include both textual description and density information
        :type query: str
        :param top_n: the number of top similar food items to return (default = 5)
        :type top_n: int
        :param minimum_confidence: the minimum confidence score for a search result to be considered valid (default = DEFAULT_MINIMUM_CONFIDENCE)
        :type minimum_confidence: float

        :returns: a DataFrame containing the top similar food items based on the query
        :rtype: pd.DataFrame
        """

        if self.search_cache.get(query) is not None:
            return self.search_cache [query]
        
        query_embedding = self.model.encode([query], convert_to_numpy = True).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, k = top_n)

        results = self.food_densities.iloc [indices [0]].copy()

        results ["score"] = scores [0]

        results = results [results ["score"] >= minimum_confidence]

        return results
    
    def load(self, index_path: str):
        """
        Loads the FAISS index from disk
        """

        self.index = faiss.read_index(index_path)

    def save(self):
        """
        Saves the FAISS index to disk
        """

        faiss.write_index(self.index, "food_density_embedding.faiss")