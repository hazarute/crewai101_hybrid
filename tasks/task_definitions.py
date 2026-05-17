"""
tasks/task_definitions.py — Re-exports all task factory functions.

Split into focused modules:
  tasks/architecture.py   — create_architecture_task
  tasks/backend.py        — create_backend_task, create_backend_revision_task
  tasks/frontend.py       — create_frontend_task, create_frontend_revision_task
  tasks/testing.py        — create_testing_task, create_retest_task
  tasks/devops.py         — create_devops_task
  tasks/documentation.py  — create_documentation_task
  tasks/review.py         — create_code_review_task, create_backend_review_task,
                             create_frontend_review_task
  tasks/gates.py          — create_dev_gate_task, create_backend_gate_task,
                             create_frontend_gate_task, create_test_gate_task,
                             create_approval_task

Importing from this module continues to work as before — no other files need to change.
"""

from tasks.architecture import create_architecture_task
from tasks.backend import create_backend_task, create_backend_revision_task
from tasks.frontend import create_frontend_task, create_frontend_revision_task
from tasks.testing import create_testing_task, create_retest_task
from tasks.devops import create_devops_task
from tasks.documentation import create_documentation_task
from tasks.review import (
    create_code_review_task,
    create_backend_review_task,
    create_frontend_review_task,
)
from tasks.gates import (
    create_dev_gate_task,
    create_backend_gate_task,
    create_frontend_gate_task,
    create_test_gate_task,
    create_approval_task,
)

__all__ = [
    "create_architecture_task",
    "create_backend_task",
    "create_backend_revision_task",
    "create_frontend_task",
    "create_frontend_revision_task",
    "create_testing_task",
    "create_retest_task",
    "create_devops_task",
    "create_documentation_task",
    "create_code_review_task",
    "create_backend_review_task",
    "create_frontend_review_task",
    "create_dev_gate_task",
    "create_backend_gate_task",
    "create_frontend_gate_task",
    "create_test_gate_task",
    "create_approval_task",
]
