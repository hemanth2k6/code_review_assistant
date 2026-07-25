from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
llm= ChatGoogleGenerativeAI(
    model = "gemini-1.5-flash",
    temperature = 0,
    api_key = settings.google_api_key
)

async def generate_code_review(diff: str, context: str) -> str:
    basic_prompt = f"""
    You are a Senior Software Engineer reviewing a Pull Request.

    Here is the exact code diff (changes):
    {diff}

    Here is the full file context for reference:
    {context}

    Give a very brief, 1-sentence review of these changes.
    """
    print("Sending code to Gemini for review...")
    response = await llm.ainvoke(basic_prompt)
    return response.content