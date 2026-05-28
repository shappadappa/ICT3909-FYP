import os

import faiss
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


class Embedding:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        The `Embedding` class is responsible for creating an embedding, allowing for similarity search based on the
        embedding, and providing functionality to retrieve nutritional information for specific food items.

        In particular, this class is used by `FoodEmbedding` to create an embedding for food descriptions, and by `FoodDensityEmbedding` to create an embedding for foods that incorporates density information. The embedding allows for efficient similarity search without making API calls, enabling fast retrieval of similar food items based on their descriptions and/or density information, as well as access to their nutritional information without hitting API rate limits
        """

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.model = SentenceTransformer(model_name_or_path=model_name, token=os.getenv("HF_TOKEN"))

        self.search_cache = {}

    def initialise(self, descriptions: list[str] | None = None):
        """
        Initialise the embeddings for the descriptions, incorporating any information.

        :param descriptions: the list of descriptions to create embeddings for (if None, the method will be implemented
            by the subclass to determine the descriptions based on the relevant information for the embedding)
        :type descriptions: list[str] | None
        """

        embeddings = self.model.encode(
            descriptions, show_progress_bar=True, convert_to_numpy=True, batch_size=64
        ).astype("float32")  # type: ignore

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)  # type: ignore

    def search(
        self,
        query: str,
        data: pd.DataFrame | None = None,
        top_n: int = 5,
        minimum_confidence: float = 0.0,
    ) -> pd.DataFrame:
        """
        Search for similar items based on a query that incorporates the relevant information for the embedding.

        :param query: the search query, which can include relevant information for the embedding (e.g., textual
            description, density information, etc.)
        :type query: str
        :param data: the DataFrame containing the items to search through (if None, the method will be implemented by
            the subclass to determine the DataFrame based on the relevant information for the embedding)
        :type data: pd.DataFrame | None
        :param top_n: the number of top similar items to return (default = 5)
        :type top_n: int
        :param minimum_confidence: the minimum confidence score for a search result to be considered valid (default =
            0.0)
        :type minimum_confidence: float
        :returns: a DataFrame containing the top similar items based on the query
        :rtype: pd.DataFrame
        """

        if self.search_cache.get(query) is not None:
            return self.search_cache[query]

        query_embedding = self.model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_n)  # type: ignore

        results = data.iloc[indices[0]].copy()  # type: ignore
        results["score"] = scores[0]
        results = results[results["score"] >= minimum_confidence]

        return results

    def save(self, index_path: str):
        """
        Save the FAISS index to a file for later use.

        :param index_path: the file path to save the FAISS index
        :type index_path: str
        """

        faiss.write_index(self.index, index_path)

    def load(self, index_path: str):
        """
        Load a FAISS index from a file.

        :param index_path: the file path to load the FAISS index from
        :type index_path: str
        """

        self.index = faiss.read_index(index_path)
