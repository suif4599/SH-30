from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



def call_chat_api(prompt):
    llm = ChatOpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-jryboknzeyogkbatbtuzxcvhojgdbcdxfdprmxfbixallsnw",
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            temperature=0,
        )
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    user_input = input("Your question: ")
    print("Response:", call_chat_api(user_input))