from typing import Any, Callable


def create_with_partial(
    **params: Any,
) -> Callable[..., Any]:
    def wrapper(template, **extra_params):
        merged_params = {
            **{key: str(value) for key, value in params.items()},
            **{key: str(value) for key, value in extra_params.items()},
        }
        return template.partial(**merged_params)

    return wrapper
