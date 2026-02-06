"""Tool registry with decorator-based schema generation for Claude tool_use."""

import inspect
from typing import get_type_hints, Any, Callable

# Global tool registry
_tools: dict[str, dict] = {}

# Python type → JSON Schema type mapping
_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def tool(name: str, description: str):
    """Decorator that registers a function as a Claude tool.

    Extracts parameter types from type hints and docstring to build
    the Claude tool_use JSON schema automatically.

    Usage:
        @tool(name="web_search", description="Search the web using DuckDuckGo")
        def web_search(query: str) -> str:
            '''
            Args:
                query: The search query string
            '''
            ...
    """
    def decorator(func: Callable) -> Callable:
        hints = get_type_hints(func)
        sig = inspect.signature(func)
        param_docs = _parse_param_docs(func.__doc__ or "")

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = hints.get(param_name, str)
            json_type = _TYPE_MAP.get(param_type, "string")

            prop: dict[str, Any] = {"type": json_type}
            if param_name in param_docs:
                prop["description"] = param_docs[param_name]

            properties[param_name] = prop

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "name": name,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

        _tools[name] = {
            "schema": schema,
            "func": func,
        }

        func._tool_name = name
        return func

    return decorator


def _parse_param_docs(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from Args section of docstring."""
    params = {}
    in_args = False
    current_param = None
    current_desc_lines = []

    for line in docstring.split("\n"):
        stripped = line.strip()

        if stripped.lower().startswith("args:"):
            in_args = True
            continue

        if in_args:
            if stripped and not stripped.startswith("-") and ":" in stripped and not stripped.startswith(" "):
                # Could be end of Args section (e.g. "Returns:")
                if current_param:
                    params[current_param] = " ".join(current_desc_lines).strip()
                break

            # Match "param_name: description" or "param_name (type): description"
            if ":" in stripped:
                parts = stripped.lstrip("- ").split(":", 1)
                param_candidate = parts[0].strip().split("(")[0].strip()
                if param_candidate.isidentifier():
                    if current_param:
                        params[current_param] = " ".join(current_desc_lines).strip()
                    current_param = param_candidate
                    current_desc_lines = [parts[1].strip()]
                    continue

            if current_param and stripped:
                current_desc_lines.append(stripped)

    if current_param:
        params[current_param] = " ".join(current_desc_lines).strip()

    return params


def get_all_tool_schemas() -> list[dict]:
    """Return all registered tool schemas for Claude API."""
    return [entry["schema"] for entry in _tools.values()]


def get_tool_func(name: str) -> Callable | None:
    """Get the function for a registered tool by name."""
    entry = _tools.get(name)
    return entry["func"] if entry else None


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a registered tool with the given arguments."""
    func = get_tool_func(name)
    if func is None:
        return f"Error: Unknown tool '{name}'"
    try:
        result = func(**arguments)
        return str(result) if result is not None else "Done."
    except Exception as e:
        return f"Error executing {name}: {e}"
