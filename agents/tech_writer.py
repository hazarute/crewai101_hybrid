"""
agents/tech_writer.py — Senior Technical Writer / Documentation Engineer.

Writes the final README.md and any supplementary docs, making sure a
developer can onboard and run the project in under 10 minutes.
"""

from crewai import Agent
from crewai_tools import FileWriterTool, FileReadTool, DirectoryReadTool

from models.llm_factory import reviewer_llm


tech_writer = Agent(
    role="Senior Technical Writer",
    goal=(
        "Write complete, developer-friendly documentation for the project. "
        "Use FileWriterTool to write the README.md, API reference, and development "
        "setup guide to the project directory."
    ),
    backstory=(
        "You are a senior technical writer who has documented APIs and developer tools "
        "at top-tier software companies. You understand code deeply and translate it "
        "into clear, accurate documentation that helps developers onboard in under "
        "10 minutes. "
        "Your README.md always covers: project overview, architecture diagram "
        "(ASCII or Mermaid), prerequisites, quickstart (`docker compose up`), "
        "API reference with curl examples, development setup (venv, npm install, "
        "hot reload), environment variables table, testing instructions, and "
        "contributing guidelines. "
        "You verify that every documented command corresponds to the real project files. "
        "CRITICAL RULE — you MUST use FileWriterTool to write README.md and all docs "
        "to disk under projects/<slug>/. "
        "Your Final Answer is a concise summary of what was documented."
    ),
    llm=reviewer_llm,
    tools=[FileWriterTool(), FileReadTool(), DirectoryReadTool()],
    allow_delegation=False,
    verbose=True,
)
