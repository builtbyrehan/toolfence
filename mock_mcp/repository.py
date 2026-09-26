from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import TypedDict

from app.policy.matcher import validate_resource


DEMO_REPOSITORY = "project"
TASK_BRANCH = "feature/BUG-17"

MAX_FILE_CONTENT_LENGTH = 200_000
MAX_PR_TITLE_LENGTH = 200
MAX_PR_BODY_LENGTH = 4_000


class FileRecord(TypedDict):
    repository: str
    branch: str
    path: str
    content: str


class WriteResult(TypedDict):
    repository: str
    branch: str
    path: str
    created: bool
    content: str


class PullRequestRecord(TypedDict):
    number: int
    repository: str
    branch: str
    title: str
    body: str
    changed_files: list[str]
    changes: dict[str, str]
    status: str


class RepositorySnapshot(TypedDict):
    repository: str
    branch: str
    files: dict[str, str]


_INITIAL_FILES: dict[str, str] = {
    "project/src/cart.py": (
        "def calculate_total(prices):\n"
        "    return sum(prices[1:])\n"
    ),
    "project/tests/test_cart.py": (
        "from src.cart import calculate_total\n"
        "\n"
        "\n"
        "def test_multiple_items():\n"
        "    assert calculate_total([10, 20, 30]) == 60\n"
        "\n"
        "\n"
        "def test_empty_cart():\n"
        "    assert calculate_total([]) == 0\n"
        "\n"
        "\n"
        "def test_single_item():\n"
        "    assert calculate_total([25]) == 25\n"
    ),
}


class RepositoryService:
    """
    Small in-memory repository backend for the ToolFence golden demo.

    The service models one repository and one task working branch:

        repository: project
        branch: feature/BUG-17

    Authorization is intentionally NOT performed here. ToolFence's protected
    execution layer will authorize requests before calling this service.
    """

    def __init__(self) -> None:
        self._lock = RLock()

        # Keep an immutable-by-convention baseline so that pull requests can
        # determine which files differ from the starting demo fixture.
        self._initial_files: dict[str, str] = deepcopy(_INITIAL_FILES)

        # This is the mutable working tree used by repo.read, repo.write,
        # future CI checks, and pull-request creation.
        self._files: dict[str, str] = deepcopy(_INITIAL_FILES)

        self._pull_requests: list[PullRequestRecord] = []

    def read(self, path: str) -> FileRecord:
        """
        Read a file from the current in-memory working tree.

        Raises:
            ValueError:
                If the logical repository resource is malformed.

            KeyError:
                If the repository or file does not exist.
        """
        self._validate_demo_path(path)

        with self._lock:
            if path not in self._files:
                raise KeyError(f"Repository file does not exist: {path}")

            return {
                "repository": DEMO_REPOSITORY,
                "branch": TASK_BRANCH,
                "path": path,
                "content": self._files[path],
            }

    def write(self, path: str, content: str) -> WriteResult:
        """
        Create or update a text file in the demo repository.

        The caller cannot choose the working branch. All writes belong to the
        single task branch used by the golden demo.

        Raises:
            ValueError:
                If the repository path or file content is invalid.

            KeyError:
                If the path targets a repository other than the demo repo.
        """
        self._validate_demo_path(path)
        self._validate_file_content(content)

        with self._lock:
            created = path not in self._files
            self._files[path] = content

            return {
                "repository": DEMO_REPOSITORY,
                "branch": TASK_BRANCH,
                "path": path,
                "created": created,
                "content": content,
            }

    def create_pull_request(
        self,
        branch: str,
        title: str,
        body: str = "",
    ) -> PullRequestRecord:
        """
        Create an in-memory pull request for the task branch.

        The PR records the files whose current contents differ from the
        repository's starting fixture.

        Raises:
            ValueError:
                If the branch/resource syntax or PR text is invalid, or if
                there are no repository changes to submit.

            KeyError:
                If the requested branch is not the task branch.
        """
        validate_resource("branch", branch)
        self._validate_pr_title(title)
        self._validate_pr_body(body)

        if branch != TASK_BRANCH:
            raise KeyError(f"Unknown repository branch: {branch}")

        with self._lock:
            changed_files = sorted(
                path
                for path, content in self._files.items()
                if self._initial_files.get(path) != content
            )

            if not changed_files:
                raise ValueError(
                    "Cannot create a pull request because the repository "
                    "contains no changes."
                )

            changes = {
                path: self._files[path]
                for path in changed_files
            }

            record: PullRequestRecord = {
                "number": len(self._pull_requests) + 1,
                "repository": DEMO_REPOSITORY,
                "branch": branch,
                "title": title,
                "body": body,
                "changed_files": changed_files,
                "changes": deepcopy(changes),
                "status": "open",
            }

            self._pull_requests.append(deepcopy(record))

            return deepcopy(record)

    def snapshot(self) -> RepositorySnapshot:
        """
        Return a safe copy of the current repository state.

        This is intended for trusted internal components such as the future
        mock CI service. Mutating the returned dictionary cannot modify the
        stored repository.
        """
        with self._lock:
            return {
                "repository": DEMO_REPOSITORY,
                "branch": TASK_BRANCH,
                "files": deepcopy(self._files),
            }

    def list_pull_requests(self) -> list[PullRequestRecord]:
        """
        Return safe copies of all pull requests created by this service.
        """
        with self._lock:
            return deepcopy(self._pull_requests)

    @staticmethod
    def _validate_demo_path(path: str) -> None:
        validate_resource("repo_path", path)

        repository, _, _relative_path = path.partition("/")

        if repository != DEMO_REPOSITORY:
            raise KeyError(f"Unknown repository: {repository}")

    @staticmethod
    def _validate_file_content(content: str) -> None:
        if not isinstance(content, str):
            raise ValueError("Repository file content must be a string.")

        if len(content) > MAX_FILE_CONTENT_LENGTH:
            raise ValueError(
                "Repository file content exceeds the maximum size of "
                f"{MAX_FILE_CONTENT_LENGTH} characters."
            )

        if "\x00" in content:
            raise ValueError(
                "Repository file content cannot contain null characters."
            )

    @staticmethod
    def _validate_pr_title(title: str) -> None:
        if not isinstance(title, str):
            raise ValueError("Pull request title must be a string.")

        if not title.strip():
            raise ValueError("Pull request title cannot be blank.")

        if title != title.strip():
            raise ValueError(
                "Pull request title cannot contain surrounding whitespace."
            )

        if len(title) > MAX_PR_TITLE_LENGTH:
            raise ValueError(
                "Pull request title exceeds the maximum length of "
                f"{MAX_PR_TITLE_LENGTH} characters."
            )

        if "\x00" in title:
            raise ValueError(
                "Pull request title cannot contain null characters."
            )

    @staticmethod
    def _validate_pr_body(body: str) -> None:
        if not isinstance(body, str):
            raise ValueError("Pull request body must be a string.")

        if len(body) > MAX_PR_BODY_LENGTH:
            raise ValueError(
                "Pull request body exceeds the maximum length of "
                f"{MAX_PR_BODY_LENGTH} characters."
            )

        if "\x00" in body:
            raise ValueError(
                "Pull request body cannot contain null characters."
            )