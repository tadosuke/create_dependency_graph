"""Python コードを読みこみ、メソッドとフィールドの関係を解析する."""

from __future__ import annotations

import ast


# [型エイリアス] 関数名と、関数内で使用しているメンバー変数
_FuncToAttrType = dict[str, list[str]]
# [型エイリアス] 未使用メンバー変数のセット
_UnreferencedVarSetType = set[str]
# [型エイリアス] クラス名、_FuncToAttrType、未使用メンバー変数のセット
ClassToFuncType = dict[str, tuple[_FuncToAttrType, _UnreferencedVarSetType]]


class _CodeReader:
    """Pythonコードをファイルから読み込むクラス。"""

    @staticmethod
    def read_from_file(file_path: str) -> str:
        """指定されたファイルパスからPythonコードを読み込む。"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class CodeAnalyzer:
    """Pythonコードを解析するクラス。"""

    @classmethod
    def analyze_code(cls, file_path: str) -> ClassToFuncType:
        """Pythonコードを解析して、各クラスの関数とメンバー変数の関係を表す辞書を生成する。"""
        code = _CodeReader.read_from_file(file_path)
        tree = ast.parse(code)

        class_relations = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            class_node = node
            class_name = class_node.name
            class_relations[class_name] = cls._analyze_class_node(class_node)

        return class_relations

    @classmethod
    def _analyze_class_node(cls, class_node: ast.ClassDef) -> tuple[_FuncToAttrType, set[str]]:
        """クラスのASTノードを解析して、関数とメンバー変数の関係を表す辞書を生成する。"""
        member_vars = cls._get_member_vars(class_node)

        # 関数とメンバー変数の関係
        relations = cls._analyze_function_to_var_relations(class_node, member_vars)
        # どの関数からも参照されていないメンバー変数
        unreferenced_vars = cls._find_unreferenced_vars(relations, member_vars)

        return relations, unreferenced_vars

    @classmethod
    def _analyze_function_to_var_relations(
            cls,
            class_node: ast.ClassDef,
            member_vars: set[str]) -> _FuncToAttrType:
        relations: _FuncToAttrType = {}

        properties = cls._get_properties(class_node)
        functions = cls._get_functions(class_node)

        for sub_node in ast.walk(class_node):
            if not isinstance(sub_node, ast.FunctionDef):
                continue

            function_name = sub_node.name
            if function_name == '__init__':
                continue

            relations[function_name] = []

            for attr_node in ast.walk(sub_node):
                if not isinstance(attr_node, ast.Attribute):
                    continue

                attribute_name = attr_node.attr
                if attribute_name in properties:
                    continue
                if attribute_name in functions:
                    continue
                if attribute_name not in member_vars:
                    continue

                relations[function_name].append(attribute_name)

        return relations

    @classmethod
    def _get_properties(cls, class_node: ast.ClassDef) -> set[str]:
        """プロパティ名の一覧を取得する."""
        properties = set()
        for sub_node in ast.walk(class_node):
            if isinstance(sub_node, ast.FunctionDef):
                for decorator in sub_node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "property":
                        properties.add(sub_node.name)
        return properties

    @classmethod
    def _get_functions(cls, class_node: ast.ClassDef) -> set[str]:
        """関数名の一覧を取得する。"""
        functions = set()
        for sub_node in ast.walk(class_node):
            if isinstance(sub_node, ast.FunctionDef):
                functions.add(sub_node.name)
        return functions

    @classmethod
    def _get_member_vars(cls, class_node: ast.ClassDef) -> set[str]:
        """メンバ変数の一覧を取得する。"""
        member_vars = set()
        for sub_node in ast.walk(class_node):
            if isinstance(sub_node, ast.Assign):
                for target in sub_node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        member_vars.add(target.attr)
        return member_vars

    @classmethod
    def _find_unreferenced_vars(cls, relations: _FuncToAttrType, member_vars: set[str]) -> _UnreferencedVarSetType:
        all_referenced_vars = set()
        for function, vars in relations.items():
            all_referenced_vars.update(vars)

        return member_vars - all_referenced_vars
