"""Summarizes papers (PDFs) into structured format and visualize them.

See this example: https://curator.bespokelabs.ai/datasets/26d4adb10ab6445687b085bd28f5aec0?appId=3fb0753708f042718c36775d92b9fa71

See README.md for more details.

Usage:
```
# Use default PDFs
python summarize.py

# Summarize a single PDF
python summarize.py --pdf https://arxiv.org/pdf/2501.12948

# Summarize multiple PDFs using multiple flags
python summarize.py --pdf https://arxiv.org/pdf/2501.12948 --pdf https://arxiv.org/pdf/2403.04642

# Summarize multiple PDFs using comma-separated list
python summarize.py --pdf https://arxiv.org/pdf/2501.12948,https://arxiv.org/pdf/2403.04642
```

"""
from typing import Dict, List

import argparse
import textwrap
from pydantic import BaseModel, Field

from bespokelabs import curator
from bespokelabs.curator.utils import push_to_viewer

from get_content import get_pdf_markdown

# Default PDFs to process if none are specified
_DEFAULT_PDFS = [
    "https://arxiv.org/pdf/2501.12948",  # DeepSeek-R1
    "https://arxiv.org/pdf/2403.04642",  # RLHF
    "https://arxiv.org/pdf/2501.04519",  # rStar-Math
    "https://arxiv.org/pdf/2502.11886",  # LIMR
    "https://arxiv.org/pdf/2505.24864",  # ProRL
    "https://arxiv.org/pdf/2505.03335",  # Absolute-Zero
    "https://arxiv.org/pdf/2503.14476",  # DAPO
    "https://arxiv.org/pdf/2506.04178",  # OpenThoughts
    "https://arxiv.org/pdf/2410.01679",  # VinePPO
]


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
        return textwrap.dedent(f"""
            Extract information from the text of a paper.

            Text of the paper is:
            {input['markdown']}
        """).strip()
    
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
    parser = argparse.ArgumentParser(description="Summarize academic papers from PDFs.")
    parser.add_argument(
        "--pdf",
        type=str,
        default=",".join(_DEFAULT_PDFS),
        help=("URL(s) of the PDF(s) to summarize. Can be specified multiple times or as comma-separated list. "
              "If not specified, uses default set of papers.")
    )
    args = parser.parse_args()

    # Split the comma-separated URLs and strip whitespace
    pdf_urls = [url.strip() for url in args.pdf.split(",")]
    texts = get_pdf_markdown(pdf_urls)
    summarizer = PaperSummarizer(
        model_name="claude-sonnet-4-20250514", backend="litellm")
    summaries_response = summarizer(texts)

    viewer_url = push_to_viewer(summaries_response.dataset)
    print(f"Nicely formatted site, assuming you didn't change the format above: {viewer_url}?appId=3fb0753708f042718c36775d92b9fa71")