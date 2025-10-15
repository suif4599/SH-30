from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import API_KEY # pyright: ignore[reportAttributeAccessIssue]


def call_chat_api(prompt):
    """
    Call the chat API with a given prompt.
    
    @param prompt: The input prompt to send to the chat API
    @return: The content of the API response
    """
    llm = ChatOpenAI(
        base_url="https://api.siliconflow.cn/v1",
        api_key=API_KEY,
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        temperature=0,
    )
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    print("Response:", call_chat_api(user_input))