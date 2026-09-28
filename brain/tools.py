# from langchain_core.tools import  tool

# @tool
# def get_weather_or_time(location: str):
#     """
#     Retrieve current weather conditions and local time for a specified location.

#     Args:
#         location (str): The name of the city or place to fetch weather and time data for.

#     Returns:
#         dict: A dictionary containing the current weather description, local time,
#               and city name.
#               Example:
#                   {
#                       "city": "New York",
#                       "weather": "75°F, raining",
#                       "time": "12:34"
#                   }
#     """
#     return {"city": location, "weather": "75°F, raining", "time": "12:34"}

# @tool
# def camera():
#     """
#     Capture an image using the camera and identify the main object in view.

#     Returns:
#         dict: Contains a description of the detected object.
#               Example: {"object": "White Cat"}
#     """
#     return {"object": "White Cat"}


# @tool
# def rag_retriever(query: str):
#     """
#     Perform a retrieval-augmented generation (RAG) search on the vector database, when ever the question is personal.

#     Args:
#         query (str): The text query to search for relevant information.

#     Returns:
#         dict: Contains retrieved content relevant to the query.
#               Example: {"content": "Mohammed Ansari was born in 2005"}
#     """
#     print(query)
#     return {"content": "Mohammed Ansari was born in 2005, ", "query":query}

# @tool
# def rag_save(query: str):
#     """
#     Save or update information in the vector database for retrieval-augmented generation (RAG).

#     This function stores or indexes new data into the vector database so it can be retrieved
#     later during RAG queries.

#     Args:
#         query (str): The text or document content to be embedded and saved in the database.

#     Returns:
#         dict: Confirmation of the save operation.
#               Example: {"content": "done"}
#     """
#     return {"content": "done"}