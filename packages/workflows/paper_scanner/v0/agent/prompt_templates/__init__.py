from langchain.prompts import PromptTemplate

# HERE LIES THE PROMPT TEMPLATES FOR ALL AGENT NODES
# --------------------------------------------------

discovery_prompt = PromptTemplate.from_template(
    """
You are an expert research analyzer. Analyze the text and extract meaningful research findings that represent significant academic contributions and discoveries.

Guidelines:
- Don't add or update more than 3 findings in total.
- Focus exclusively on research insights, theoretical developments, and empirical results.
- Exclude implementation details, institutional information, or other non-research specifics.
- Avoid adding umbrella findings that encompass multiple insights.
- Prioritize refining existing findings over creating new ones when possible.
- Each finding should represent a distinct academic contribution or theoretical advancement.
- Each finding must be supported by the given text - no inference or fabrication.
- Findings should focus on methodology, theoretical frameworks, and empirical evidence.

Text: 
```
{text}
```

Existing Findings: 
```
{existing_findings}
```

{format_instructions}
"""
)

finding_creation_prompt = PromptTemplate.from_template(
    """
You are an expert research analyzer. Create a new finding from the given text.

guidelines:
- Avoid returning latex or code snippets, istead, provide explanatory plain text.
- The finding summary and methodology should be clear, concise and tightly related to the title and subject of the finding.

Title of the new finding: 
```
{title}
```
Subject of the new finding: 
```
{description}
```

Create a finding from:
```
{text}
```

{format_instructions}
"""
)

finding_update_prompt = PromptTemplate.from_template(
    """
You are an expert research analyzer. Update an existing finding with new information in relation of what is the update about.

guidelines:
- Update this finding with new information only where suitable.
- Avoid returning latex or code snippets, istead, provide explanatory plain text.

Current finding: 
```
{finding}
```

New information: 
```
{text}
```

What to update:
```
{what_to_update}
```

{format_instructions}
"""
)

findings_consolidator_prompt = PromptTemplate.from_template(
    """
You are a highly skilled research assistant tasked with consolidating academic findings. The goal is to identify and synthesize the key research contributions and scholarly insights, focusing exclusively on novel academic discoveries, methodological advances, and theoretical developments.

Guidelines:
- Prioritize findings that represent original research contributions or theoretical advancements
- Focus on empirical results, methodological innovations, and theoretical frameworks
- Exclude implementation details, or non-research-specific data like instititutional information
- Merge related research findings while preserving their distinct academic contributions
- Ensure each finding addresses a specific research question or theoretical gap
- Maintain academic precision in terminology and concepts
- Preserve statistical significance and empirical evidence where present

When evaluating findings, consider:
- Does it present new knowledge or theoretical understanding?
- Is it supported by empirical evidence or rigorous theoretical analysis?
- Does it advance the field's methodology or theoretical framework?
- Does it challenge or refine existing academic understanding?

Input Findings:
{findings}

{format_instructions}
"""
)
