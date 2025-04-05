import inspect
import re
from typing import Any, Dict, Optional, Type, get_origin

import langchain_community.chat_models as chat_models
from langchain_community.chat_models import __all__ as available_models
from langchain_core.language_models.chat_models import BaseChatModel


def _get_class_member_doc(cls, param_name: str) -> Optional[str]:
    lines, _ = inspect.getsourcelines(cls)
    state = 0  # 0=waiting, 1=ready, 2=reading mutliline
    doc_lines = []
    for line in lines:
        if state == 0:
            if re.match(f"\\s*({param_name}):", line):
                state = 1
                doc_lines = []
        elif state == 1:
            m = re.match('^\\s*("{1,3})(.*?)("{1,3})?$', line)
            if m:
                m_groups = m.groups()
                if m_groups[2] == m_groups[0]:
                    doc_lines.append(m_groups[1])
                    return list(doc_lines)
                elif m_groups[0] == '"""':
                    doc_lines.append(m_groups[1])
                    state = 2
                else:
                    state = 0
        elif state == 2:
            m = re.match('(.*?)"""$', line)
            if m:
                doc_lines.append(m.group(1))
                return list(doc_lines)
            else:
                doc_lines.append(line)
    return


def camel_to_snake(name):
    "Convert camelCase to snake_case"
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


EXCLUDED_CHAT_MODELS = [
    "FakeListChatModel",
    "ChatDatabricks",
    "ChatMlflow",
    "HumanInputChatModel",
]

CHAT_MODEL_EXCLUDED_PARAMS = [
    "name",
    "verbose",
    "cache",
    "streaming",
    "tiktoken_model_name",
]


class ChatModelParams:
    def __init__(self, typ: Any, default: Any, description: str):
        self.typ = typ
        self.default = default
        self.description = description

    def __str__(self):
        return f"ChatModelParams(typ={self.typ.__name__}, default='{self.default}'{', description=' + chr(39) + self.description + chr(39) if self.description else ''}"


class ChatModelInfo:
    def __init__(self, model_cls: Type[BaseChatModel], doc: str, params: Dict[str, Any]):
        self.model_cls = model_cls
        self.doc = doc
        self.params = params

    def __str__(self):
        s = f"ChatModelInfo(model_cls={self.model_cls}:\n"
        for param_name, param in self.params.items():
            if param_name == "doc":
                continue
            s += f"    {param_name}: {param}\n"
        return s

    @property
    def short_doc(self):
        return self.doc[: self.doc.find("\n")]


def get_langchain_chat_models_info() -> Dict[str, Dict[str, Any]]:
    """
    Inspects the langchain library, extracting information about supported chat models
    and their required/optional parameters.
    """
    models: Dict[str, ChatModelInfo] = {}

    # Iterate over available models dynamically using __all__ from langchain.chat_models
    for model_cls_name in available_models:
        # Skip excluded chat models
        if model_cls_name in EXCLUDED_CHAT_MODELS:
            continue

        # Try to get the model class from langchain.chat_models
        model_cls = getattr(chat_models, model_cls_name, None)

        # Ensure it's a class and a subclass of BaseChatModel
        if model_cls and isinstance(model_cls, type) and issubclass(model_cls, BaseChatModel):
            model_short_name = camel_to_snake(model_cls.__name__).replace("_chat", "").replace("chat_", "")

            # Introspect supported model parameters - for newer langchain versions
            params: Dict[str, ChatModelParams] = {}

            # Check if the class has __annotations__ for newer versions of langchain
            if hasattr(model_cls, "__annotations__"):
                for param_name, typ in model_cls.__annotations__.items():
                    if param_name in CHAT_MODEL_EXCLUDED_PARAMS:
                        continue

                    # Try to get default value
                    default = getattr(model_cls, param_name, None) if hasattr(model_cls, param_name) else None

                    # Try to get documentation
                    doc_lines = _get_class_member_doc(model_cls, param_name)
                    description = "".join(doc_lines) if doc_lines else None

                    params[param_name] = ChatModelParams(typ=typ, default=default, description=description)

            # For older versions with __fields__
            elif hasattr(model_cls, "__fields__"):
                for param_name, field in model_cls.__fields__.items():
                    if param_name in CHAT_MODEL_EXCLUDED_PARAMS:
                        continue
                    typ = field.outer_type_
                    if typ not in [str, float, int, bool] and get_origin(typ) not in [str, float, int, bool]:
                        continue
                    doc_lines = _get_class_member_doc(model_cls, param_name)
                    description = "".join(doc_lines) if doc_lines else None
                    params[param_name] = ChatModelParams(typ=typ, default=field.default, description=description)

            models[model_short_name] = ChatModelInfo(model_cls=model_cls, doc=model_cls.__doc__ or "", params=params)

    return models


def print_chat_models_info(detailed: bool = False) -> None:
    """
    Print information about LangChain chat models in a well-formatted way.

    Args:
        detailed: Whether to print detailed information including parameter descriptions
    """
    # Get models information
    models = get_langchain_chat_models_info()

    print(f"{'=' * 80}")
    print(f"AVAILABLE LANGCHAIN CHAT MODELS: {len(models)} models")
    print(f"{'=' * 80}")

    for model_name, model_info in sorted(models.items()):
        # Print model name and class
        print(f"\n{model_name} ({model_info.model_cls.__name__})")
        print(f"{'-' * 60}")

        # Print short documentation
        if model_info.doc:
            doc = model_info.doc.strip()
            print(f"Description: {model_info.short_doc}")

        # Print parameters
        if model_info.params:
            print("\nParameters:")
            for param_name, param in sorted(model_info.params.items()):
                type_name = getattr(param.typ, "__name__", str(param.typ))
                default_value = (
                    "None"
                    if param.default is None
                    else f"'{param.default}'"
                    if isinstance(param.default, str)
                    else str(param.default)
                )

                print(f"  • {param_name} ({type_name}, default={default_value})")

                # Print parameter description if detailed mode is enabled
                if detailed and param.description:
                    description = param.description.strip()
                    # Format the description with proper indentation for multiline descriptions
                    formatted_desc = "\n    ".join(description.split("\n"))
                    print(f"    {formatted_desc}")
        else:
            print("\nNo specific parameters documented.")

        # Add a visual separator between models
        if detailed:
            print("\n" + "-" * 60)
