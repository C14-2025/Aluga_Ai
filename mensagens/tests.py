import inspect
import importlib
import pathlib
import pytest

PACKAGE = __package__ or "mensagens"
HERE = pathlib.Path(__file__).parent

def _module_paths():
    for p in HERE.glob("*.py"):
        if p.name.startswith("_"):
            continue
        if p.name == "test_tests.py":
            continue
        yield p.stem

def test_modules_importable():
    modules = list(_module_paths())
    if not modules:
        pytest.skip("Nenhum módulo em mensagens para testar")
    for name in modules:
        # relative import from the package
        mod = importlib.import_module(f".{name}", package=PACKAGE)
        assert mod is not None


def test_public_callables_have_valid_signatures():
    modules = list(_module_paths())
    if not modules:
        pytest.skip("Nenhum módulo em mensagens para testar")
    for name in modules:
        mod = importlib.import_module(f".{name}", package=PACKAGE)
        members = inspect.getmembers(mod, predicate=lambda o: (inspect.isfunction(o) or inspect.isclass(o)) and o.__module__ == mod.__name__)
        for member_name, member in members:
            if member_name.startswith("_"):
                continue
            if inspect.isfunction(member):
                sig = inspect.signature(member)
                assert isinstance(sig, inspect.Signature)
            elif inspect.isclass(member):
                # check constructor signature is retrievable
                try:
                    sig = inspect.signature(member)
                    assert isinstance(sig, inspect.Signature)
                except (ValueError, TypeError):
                    pytest.fail(f"Não foi possível obter assinatura de {mod.__name__}.{member_name}")

def test_admin_modules_importable():
    try:
        mod = importlib.import_module(f".admin", package=PACKAGE)
        assert mod is not None
    except ImportError as e:
        pytest.fail(f"Não foi possível importar o módulo admin: {e}")

def test_admin_has_registered_models():
    mod = importlib.import_module(f".admin", package=PACKAGE)
    admin_site = getattr(mod, 'admin', None)
    assert admin_site is not None, "O módulo admin não possui o atributo 'admin'"

    registered_models = admin_site.site._registry.keys()
    assert registered_models, "Nenhum modelo registrado no admin"

    from .models import Conversation, Message
    assert any(model.__name__ == 'Conversation' for model in registered_models), "Modelo Conversation não está registrado no admin"
    assert any(model.__name__ == 'Message' for model in registered_models), "Modelo Message não está registrado no admin"

def test_admin_model_admin_classes():
    mod = importlib.import_module(f".admin", package=PACKAGE)
    admin_site = getattr(mod, 'admin', None)
    assert admin_site is not None, "O módulo admin não possui o atributo 'admin'"

    registered_models = admin_site.site._registry
    from .models import Conversation, Message

    conversation_admin = registered_models.get(Conversation)
    assert conversation_admin is not None, "Conversation não está registrado no admin"
    assert hasattr(conversation_admin, 'list_display'), "ConversationAdmin deve ter list_display definido"
    assert conversation_admin.list_display == ('id', 'created_at'), "ConversationAdmin list_display incorreto"

    message_admin = registered_models.get(Message)
    assert message_admin is not None, "Message não está registrado no admin"
    assert hasattr(message_admin, 'list_display'), "MessageAdmin deve ter list_display definido"
    assert message_admin.list_display == ('id', 'conversation', 'sender', 'created_at'), "MessageAdmin list_display incorreto"
    assert hasattr(message_admin, 'search_fields'), "MessageAdmin deve ter search_fields definido"
    assert message_admin.search_fields == ('content',), "MessageAdmin search_fields incorreto"

