from crews.integration_crew.integration_crew import FinalMissionReport
# Render the generated final json into a markdown file
def to_markdown(report: FinalMissionReport) -> str:
    toc = "\n".join(f"- {item}" for item in report.table_of_contents)

    return f"""# {report.title}

## Table of Contents
{toc}

---

{report.rover_section}

---

{report.drone_section}

---

{report.satellite_section}

---

## Conclusion
{report.conclusion}
"""
