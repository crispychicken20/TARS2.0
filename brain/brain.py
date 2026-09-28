# """
# brain.py
# --------
# TARS  Module — Processes user input and generates responses.
# """
# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
# from tools import get_weather_or_time,camera,rag_save,rag_retriever
# from typing import TypedDict, Annotated, Sequence
# from langgraph.graph import StateGraph, END,START
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode, tools_condition
# from langgraph.checkpoint.memory import MemorySaver


# #Setting up the LLM
# load_dotenv()
# os.environ["GOOGLE_API_KEY"] = os.getenv("LLM_API_KEY")



# # state
# class State(TypedDict):
#     messages: Annotated[list, add_messages]


# SYSTEM_PROMPT = (
#     "You are TARS, the witty, efficient, and loyal robotic assistant from Interstellar. "
#     "Maintain a balance between sarcasm and professionalism. Be mission-focused, with occasional dry humor. "
#     "Be clear and concise; add personality when appropriate."
#     "Use the rag rag_retriever tool when you do not have answers to personal questions, input a relevant query"
# )

# tools = [get_weather_or_time,camera,rag_save,rag_retriever,get_weather_or_time]



# memory = MemorySaver()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-lite",
#     temperature=0.7,
#     max_output_tokens=200,
# )

# llm_with_tools  = llm.bind_tools(tools)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM_PROMPT),
#     MessagesPlaceholder(variable_name="messages"),
# ])

# # Compose prompt -> model (with tools)
# chain = prompt | llm_with_tools

# def chatbot(state: State):
#     # chain expects a dict containing `messages`
#     return {"messages": [chain.invoke(state)]}



# def chatbot(state: State):
#     # chain expects a dict containing `messages`
#     return {"messages": [chain.invoke(state)]}




# builder = StateGraph(State)
# builder.add_node(chatbot)
# builder.add_node("tools", ToolNode(tools))
# builder.add_edge(START, "chatbot")
# builder.add_conditional_edges("chatbot", tools_condition)
# builder.add_edge("tools", "chatbot")
# graph = builder.compile(checkpointer=memory)




# def chat_loop():
#     config = {"configurable": {"thread_id": "1"}}
#     print("TARS is online. Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ").strip()
#         if user_input.lower() in ["exit", "quit"]:
#             print("TARS: Shutting down. See you.")
#             break
#         try:
#             state = graph.invoke(
#                 {"messages": [{"role": "user", "content": user_input}]},
#                 config=config
#             )

#             # extract latest assistant message
#             last_msg = state["messages"][-1]
#             if isinstance(last_msg, dict):
#                 reply = last_msg.get("content", "")
#             else:
#                 reply = getattr(last_msg, "content", "")
#             print(f"TARS: {reply}")

#         except Exception as e:
#             print(f"ERROR {e}")


# from typing import Optional, List, Dict, Any, Union

# def end_point_chat_tars(
#     question: str,
#     session_id: str,
#     user_id: str,
#     current_url: Optional[str] = None,
#     conversation_history: Optional[List[Dict[str, str]]] = None
# ) -> Dict[str, Any]:
#     """
#     Entry point for TARS (LangGraph) backed chat.
#     - Normalizes conversation_history into LangGraph's expected message dicts.
#     - Injects current_url as a system hint (optional).
#     - Invokes the compiled `graph` with MemorySaver using session_id as thread_id.
#     - Returns a structured response payload.
#     """
#     try:
#         # 1) Normalize history
#         if conversation_history is None:
#             conversation_history = []

#         normalized_messages: List[Dict[str, str]] = []
#         for msg in conversation_history:
#             role = msg.get("role")
#             content = msg.get("content", "")
#             if role in {"user", "assistant", "system"} and isinstance(content, str):
#                 normalized_messages.append({"role": role, "content": content})


#         # 3) Append the current user question
#         normalized_messages.append({"role": "user", "content": question})

#         # 4) Invoke LangGraph with per-session thread id for MemorySaver
#         config = {"configurable": {"thread_id": session_id}}
#         state = graph.invoke({"messages": normalized_messages}, config=config)

#         # 5) Extract last assistant message safely
#         reply = ""
#         msgs = state.get("messages", [])
#         if msgs:
#             last = msgs[-1]
#             if isinstance(last, dict):
#                 # Typical shape when using dict messages
#                 if last.get("role") == "assistant":
#                     reply = last.get("content", "") or ""
#                 else:
#                     # If the final node returned a model message object-like
#                     reply = last.get("content", "") or ""
#             else:
#                 # Fallback for object messages (e.g., BaseMessage)
#                 reply = getattr(last, "content", "") or ""

#         if reply.strip():
#             return {
#                 "response": reply,
#                 "status": "success",
#                 "session_id": session_id,
#                 "user_id": user_id,
#             }
#         else:
#             return {
#                 "response": "No response generated",
#                 "status": "no_response",
#                 "session_id": session_id,
#                 "user_id": user_id,
#             }

#     except Exception as e:
#         return {
#             "response": f"Error: {e}",
#             "status": "error",
#             "session_id": session_id,
#             "user_id": user_id,
#         }


# def test_end_point_chat_tars():
#     print("Running minimal test for end_point_chat_tars...\n")

#     # Sample conversation history
#     conversation_history = [
#         {"role": "user", "content": "Hello TARS."},
#         {"role": "assistant", "content": "Hello, pilot. How can I assist?"}
#     ]

#     # Call endpoint
#     result = end_point_chat_tars(
#         question="What's the weather like on Mars?",
#         session_id="test-session-001",
#         user_id="user-42",
#         conversation_history=conversation_history
#     )

#     # Print output
#     print("Test Output:")
#     for k, v in result.items():
#         print(f"{k}: {v}")

#     # Basic sanity assertions
#     assert isinstance(result, dict), "Result should be a dictionary"
#     assert "status" in result, "Missing status field"
#     assert "response" in result, "Missing response field"
#     print("\n Basic test completed successfully.")

# # Run it
# if __name__ == "__main__":
#     test_end_point_chat_tars()

