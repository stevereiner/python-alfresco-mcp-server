import ast
from pathlib import Path
import inspect
import unittest
from unittest.mock import patch
from alfresco_mcp_server import document_tools


class Registry:
    def __init__(self):
        self.tools = {}

    def tool(self, *, name, annotations):
        def register(fn):
            if name in self.tools:
                raise ValueError('duplicate tool')
            self.tools[name] = (fn, annotations)
            return fn
        return register


class RegistrationTests(unittest.TestCase):
    def test_available_features_register_without_legacy_imports(self):
        server = Registry()
        document_tools.register_document_tools(server)
        self.assertTrue(server.tools)
        for name, (fn, annotations) in server.tools.items():
            self.assertEqual(name, fn.__name__)
            self.assertIn('readOnlyHint', annotations)
            self.assertIn('destructiveHint', annotations)
            self.assertIn('idempotentHint', annotations)
            for parameter in inspect.signature(fn).parameters.values():
                self.assertNotIn(parameter.kind, (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD))

    def test_absent_feature_is_skipped(self):
        def absent(name):
            raise ModuleNotFoundError(name=name)
        server = Registry()
        with patch.object(document_tools, 'import_module', side_effect=absent):
            document_tools.register_document_tools(server)
        self.assertEqual(server.tools, {})

    def test_broken_dependency_is_not_silently_ignored(self):
        with patch.object(document_tools, 'import_module', side_effect=ModuleNotFoundError(name='required_dependency')):
            with self.assertRaises(ModuleNotFoundError):
                document_tools.register_document_tools(Registry())

    def test_server_registers_document_extensions_once(self):
        path = Path(__file__).resolve().parents[2] / "alfresco_mcp_server" / "fastmcp_server.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [node for node in tree.body if isinstance(node, ast.Expr)
                 and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Name)
                 and node.value.func.id == "register_document_tools"]
        self.assertEqual(len(calls), 1)
