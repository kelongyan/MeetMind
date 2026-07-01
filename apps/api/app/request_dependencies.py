from collections.abc import Callable

from fastapi import Request


def resolve_request_dependency[T](request: Request, dependency: Callable[[], T]) -> T:
    override = request.app.dependency_overrides.get(dependency)
    if override is not None:
        return override()
    return dependency()
