from packages.workflows.paper_scanner.v0 import run_paper_scanner_v0

# VERSIONING EXPORTS HERE
# -----------------------

# Alias the latest process to point to the most recent version
paper_scanner_latest = run_paper_scanner_v0


paper_scanner = {
    "v0": run_paper_scanner_v0,
    "latest": "v0",  # Remember to update respective latest also
}
paper_scanner["available_versions"] = list(paper_scanner.keys())


# Export everything
__all__ = [
    "paper_scanner",
]
