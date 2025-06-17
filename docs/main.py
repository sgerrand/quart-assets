from pathlib import Path
from typing import Any, Callable, Optional


def define_env(env: Any) -> None:
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro
    - filter: a function with one of more arguments, used to perform a
      transformation
    """

    @env.macro  # type: ignore[misc]
    def read_file(file_path: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
        """
        Read content from a file, optionally between start and end tokens.

        Args:
            file_path (str): Path to the file to read
            start (str, optional): Start token/line to begin reading from
            end (str, optional): End token/line to stop reading at

        Returns:
            str: File content, optionally filtered by start/end tokens

        Examples:
            {{ read_file('../README.md') }}
            {{ read_file('../README.md', start='## Installation') }}
            {{ read_file('../README.md', start='## Features', end='## Usage') }}
        """
        docs_dir = Path(env.conf['docs_dir'])
        full_path = docs_dir / file_path

        if not full_path.exists():
            return f"**Error: File not found: {file_path}**"

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except OSError as e:
            return f"**Error reading file {file_path}: {e}**"

        if start is None and end is None:
            return content

        lines = content.split('\n')
        start_idx = 0
        end_idx = len(lines)

        if start is not None:
            for i, line in enumerate(lines):
                if start in line:
                    start_idx = i
                    break
            else:
                return f"**Warning: Start token '{start}' not found in {file_path}**"

        if end is not None:
            for i, line in enumerate(lines[start_idx + 1:], start_idx + 1):
                if end in line:
                    end_idx = i
                    break
            else:
                pass

        extracted_lines = lines[start_idx:end_idx]
        return '\n'.join(extracted_lines)

    @env.macro  # type: ignore[misc]
    def include(file_path: str, start: Optional[str] = None, end: Optional[str] = None, skip_lines: int = 0) -> str:
        """
        Include content from a file with additional options.

        Args:
            file_path (str): Path to the file to include
            start (str, optional): Start token/line to begin reading from
            end (str, optional): End token/line to stop reading at
            skip_lines (int): Number of lines to skip from the start

        Returns:
            str: File content, processed according to parameters
        """
        content = read_file(file_path, start, end)

        if skip_lines > 0:
            lines = content.split('\n')
            content = '\n'.join(lines[skip_lines:])

        return content
