"""Schemas utils module."""

import inspect

from fastapi import Form
from pydantic import BaseModel
from pydantic.fields import ModelField


def as_form(cls: type[BaseModel]):
    """Create a decorator used to be able to use pydantic models as forms."""
    new_parameters = []

    for _, model_field in cls.__fields__.items():
        model_field: ModelField  # type: ignore

        new_parameters.append(
            inspect.Parameter(
                model_field.alias,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...)
                if model_field.required
                else Form(model_field.default),
                annotation=model_field.outer_type_,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore

    return as_form_func
