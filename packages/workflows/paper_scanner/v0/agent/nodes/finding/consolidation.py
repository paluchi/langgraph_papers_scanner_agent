from uuid import uuid4
from packages.workflows.paper_scanner.v0.agent.schemas.format_instructions import (
    FindingsConsolidator,
)
from packages.workflows.paper_scanner.v0.utils.call_llm import call_llm

from packages.workflows.paper_scanner.v0.agent.schemas.states import (
    OverallState,
)

from packages.workflows.paper_scanner.v0.agent.prompt_templates import (
    findings_consolidator_prompt,
)


# This node executes at the very end of the process to consolidate all findings into a cleaner set of findings
def findings_consolidator(state: OverallState):
    findings = state["findings"]

    # If there are no findings, return the state as is
    if len(findings) == 0:
        return state

    findings_as_text = "".join(
        [
            f"Title: {finding['title']}\nSummary: {finding['summary']}\nMethodology: {finding['methodology']}\n\n"
            for finding in findings
        ]
    )

    # Consolidate findings
    consolidation_result = call_llm(
        prompt_template=findings_consolidator_prompt,
        input_parameters={
            "findings": findings_as_text,
        },
        pydantic_object=FindingsConsolidator,
    )

    # Append an id to each finding
    consolidated_findings = []
    for finding in consolidation_result["findings"]:
        finding["id"] = str(uuid4())
        consolidated_findings.append(finding)

    # Update state with consolidated findings
    state["consolidated_findings"] = consolidated_findings

    return state
