"""Summarizes papers (PDFs) into structured format.

See this example: https://curator.bespokelabs.ai/datasets/26d4adb10ab6445687b085bd28f5aec0?appId=3fb0753708f042718c36775d92b9fa71

Note that if you enable CURATOR_VIEWER (which is enabled by default -- see the .env file),
the outputs are streamed to the viewer, which improves the visualization of the outputs.

The URL of the viewer is displayed in the terminal.

The data can be transformed into a nicer view, by adding an appId to the URL (which is done below).
If you are interested more about creating custom visualizations or want to change the structured outputs here, 
please contact me (mahesh at bespokelabs.ai).

Other things to note:
* Caching is enabled by default. So if the prompt and/or the input doesn't change,
  the output is served from the cache.
* If you want to disable caching, you can set the environment variable
  CURATOR_DISABLE_CACHE=1.
  
Installation:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python summarize.py
```

"""
from typing import Dict, List
from pydantic import BaseModel, Field
from bespokelabs import curator

from get_content import get_pdf_markdown

# Add your PDFs here.
_PDFS = [
    "https://arxiv.org/pdf/2501.12948",  # DeepSeek-R1
    "https://arxiv.org/pdf/2403.04642",  # RLHF
    "https://arxiv.org/pdf/2501.04519",  # rStar-Math
    "https://arxiv.org/pdf/2502.11886",  # LIMR
    "https://arxiv.org/pdf/2505.24864",  # ProRL
    "https://arxiv.org/pdf/2505.03335",  # Absolute-Zero
    "https://arxiv.org/pdf/2503.14476",  # DAPO
]
# Sample output, via in the viewer:
# https://curator.bespokelabs.ai/datasets/26d4adb10ab6445687b085bd28f5aec0?appId=3fb0753708f042718c36775d92b9fa71


class ConceptExplanation(BaseModel):
    concept: str = Field(description="Technical term or concept from the paper")
    simple_explanation: str = Field(description="Plain language explanation")
    analogies: List[str] = Field(description="Real-world analogies to aid understanding")
    prerequisites: List[str] = Field(description="What you need to know first")


class KeyInsight(BaseModel):
    insight: str = Field(description="Main takeaway or breakthrough")
    significance: str = Field(description="Why this matters in the field")
    implications: List[str] = Field(description="What this enables or changes")

class Summary(BaseModel):
    """Summary of a paper."""
    eli5_summary: str = Field(description="A novice level summary of the text, in the style of ELI5.")
    basic_summary: str = Field(description="A basic level summary of the text.")
    advanced_summary: str = Field(description="An advanced level summary of the text.")
    
class CriticalAnalysis(BaseModel):
    strengths: List[str] = Field(description="What the paper does well")
    limitations: List[str] = Field(description="Potential weaknesses or gaps")
    assumptions: List[str] = Field(description="Unstated assumptions made")
    methodology_assessment: str = Field(description="Quality of research methods")

class ConnectionMapping(BaseModel):
    prior_work: List[str] = Field(description="How this builds on previous research")
    related_fields: List[str] = Field(description="Connections to other domains")
    future_directions: List[str] = Field(description="What research this enables")
    practical_applications: List[str] = Field(description="Real-world uses")

class ComprehensionAid(BaseModel):
    reading_roadmap: List[str] = Field(description="Optimal order to read sections")
    focus_areas: List[str] = Field(description="Most important parts to understand deeply")
    skip_suggestions: List[str] = Field(description="Sections that can be skimmed")
    

class PaperResponse(BaseModel):
    """Summaries and insights from a paper."""
    title: str = Field(description="The title of the paper.")
    authors: List[str] = Field(description="The authors of the paper.")
    summary: Summary = Field(description="Summary of the paper.")
    # visual_aids: List[VisualAid] = Field(
    #     description="Suggested visualizations to aid understanding"
    # )
    comprehension_aid: ComprehensionAid = Field(
        description="Guide for how to approach reading the paper"
    )
    connection_mapping: ConnectionMapping = Field(
        description="How this work fits in the broader landscape"
    )
    key_insights: List[KeyInsight] = Field(
        description="Major breakthroughs and findings"
    )
    concept_explanations: List[ConceptExplanation] = Field(description="Concept explanations for the paper.")
    critical_analysis: CriticalAnalysis = Field(description="Balanced assessment of the work")
    future_work: str = Field(description="Future work from the text.")


class PaperSummarizer(curator.LLM):
    """Generate structured summaries and insights from a paper."""
    
    response_format = PaperResponse

    def prompt(self, input: Dict) -> str:
        """Prompt for the LLM."""
        return f"""Extract information from the text of a paper.

Text of the paper is:
{input['markdown']}"""
    
    def parse(self, input: Dict, response: PaperResponse) -> List[Dict]:
        """Parse the model response into structured summaries.

        Args:
            input: Dictionary containing the original text.
            response: The structured response from the LLM.

        Returns:
            List of dictionaries containing the original text and summaries.
        """
        result = {}
        result["url"] = input["url"]
        result.update(response.model_dump())
        return [result]
        

if __name__ == "__main__":
    texts = get_pdf_markdown(_PDFS)
    summarizer = PaperSummarizer(
        model_name="claude-sonnet-4-20250514", backend="litellm")
    summaries_response = summarizer(texts)
    print(summaries_response.viewer_url)
    print(f"Nicely formatted site, assuming you didn't change the format above: {summaries_response.viewer_url}?appId=3fb0753708f042718c36775d92b9fa71")