import tiktoken
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.core.config import settings
from app.schemas.models import CodeReviewResult

primary_llm = ChatGoogleGenerativeAI(
    model = "gemini-1.5-pro",
    temperature = 0,
    api_key = settings.google_api_key,
    max_retries = 2
)

fallback_llm = ChatGoogleGenerativeAI(
    model = "gemini-1.5-flash",
    temperature = 0,
    api_key = settings.google_api_key
)

robust_llm = primary_llm.with_fallbacks([fallback_llm])

parser = PydanticOutputParser(pydantic_object=CodeReviewResult)

system_template = """
You are an elite Senior Security and Software Engineer reviewing a GitHub Pull Request.
Your goal is to find critical security vulnerabilities, performance bottlenecks, and architectural flaws.

STRICT RULES:
1. DO NOT nitpick. Ignore minor style issues, missing commas, or simple typos.
2. Focus ONLY on the code changes provided in the diff.
3. Use the file context to understand the surrounding logic, but your critique must only be about the diff.
4. Keep your review concise, professional, and actionable.
5. If the code looks perfectly fine and secure, return an empty list of comments.

{format_instructions}
"""
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template = """
File Context (For Reference)
{context}

Pull Request Diff (The changes to Review):
{diff}
"""
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

review_chain = chat_prompt | robust_llm | parser

def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

async def generate_code_review(diff: str, context: str) -> CodeReviewResult:
    total_text = diff + context
    token_count = count_tokens(total_text)
    print(f"Total tokens for this PR: {token_count}")
    if token_count > settings.max_tokens:
        print(f"BLOCKED: PR token count ({token_count}) exceeds budget limit ({settings.max_tokens})")
        return CodeReviewResult(comments=[])
    print("Budget approved. Sending code to gemini for structured review...")
    response = await review_chain.ainvoke({
        "diff": diff,
        "context": context,
        "format_instructions": parser.get_format_instructions()
    })
    return response