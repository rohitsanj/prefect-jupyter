"""Module containing tasks for interacting with Jupyter."""

from enum import Enum
from typing import Any, Dict, Optional

import nbconvert
import nbformat
import papermill as pm
from prefect import task


class OutputFormat(Enum):
    """
    Valid output formats of a notebook.
    """

    ASCIIDOC = "asciidoc"
    CUSTOM = "custom"
    HTML = "html"
    LATEX = "latext"
    MARKDOWN = "markdown"
    NOTEBOOK = "notebook"
    JSON = "notebook"
    PDF = "pdf"
    PYTHON = "python"
    RST = "rst"
    SCRIPT = "script"
    WEBPDF = "webpdf"


@task
def execute_notebook(
    path: str,
    parameters: Optional[Dict[str, Any]] = None,
    log_output: bool = False,
    output_format: OutputFormat = OutputFormat.NOTEBOOK,
    kernel_name: Optional[str] = None,
    **export_kwargs: Dict[str, Any],
) -> str:
    """
    Task for running Jupyter Notebooks.

    In order to parametrize the notebook, you need to mark the parameters
    cell as described in the [papermill documentation](
    https://papermill.readthedocs.io/en/latest/usage-parameterize.html).

    Args:
        path: Where to fetch the notebook from; can be a cloud storage path.
        parameters: Parameters to use for the notebook.
        log_output: Whether or not to log notebook cell output to the papermill logger.
        output_format: The notebook output format.
        kernel_name: Name of kernel to execute the notebook against.
        **export_kwargs: Additional keyword arguments to pass to `nbconvert.export`.

    Returns:
        The body of the output.

    Examples:
        Run a parameterized notebook.
        ```python
        from prefect import flow
        from prefect_jupyter import notebook

        @flow
        def example_execute_notebook():
            body = notebook.execute_notebook(
                "test_notebook.ipynb",
                parameters={"num": 5}
            )
            output_path = "executed_notebook.ipynb"
            with open(output_path, "w") as f:
                f.write(body)
            return output_path

        example_execute_notebook()
        ```
    """
    nb: nbformat.NotebookNode = pm.execute_notebook(
        path,
        "-",
        parameters=parameters,
        kernel_name=kernel_name,
        log_output=log_output,
    )

    exporter = nbconvert.get_exporter(output_format.value)
    body, _ = nbconvert.export(exporter, nb, **export_kwargs)
    return body
