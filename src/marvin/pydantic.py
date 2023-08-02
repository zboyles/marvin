from pydantic.version import VERSION as PYDANTIC_VERSION

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if not PYDANTIC_V2:
    from pydantic import (
        BaseModel,
        BaseSettings,
        Extra,
        Field,
        PrivateAttr,
        PyObject,
        SecretStr,
        root_validator,
        validate_arguments,
        validator,
    )
    from pydantic.main import ModelMetaclass

    ModelMetaclass = ModelMetaclass
    BaseModel = BaseModel
    BaseSettings = BaseSettings
    Field = Field
    SecretStr = SecretStr
    Extra = Extra
    PrivateAttr = PrivateAttr
    validate_arguments = validate_arguments
    validator = validator
    root_validator = root_validator
    PyObject = PyObject
