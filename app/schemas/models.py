from pydantic import BaseModel, Field
class ReviewComment(BaseModel):
    line_number: int = Field(description="The exact line number in the modified file where the issue was found.")
    comment: str = Field(description="The detailed code review comment explaining the issue and how to fix it.")
    severity: str = Field(description="The severity of the issue: 'LOW', 'MEDIUM', or 'HIGH'.")

class CodeReviewResult(BaseModel):
    comments: list[ReviewComment] = Field(description="A list of review comments for the provided code.")