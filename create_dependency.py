"""Python コードを読みこみ、メソッドとフィールドの関係を解析する."""

from __future__ import annotations

import ast


# 型エイリアス
_FuncToAttrType = dict[str, list[str]]
ClassToFuncType = dict[str, _FuncToAttrType]


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
            if isinstance(node, ast.ClassDef):
                class_relations[node.name] = cls._analyze_class_node(node)

        return class_relations

    @classmethod
    def _analyze_class_node(cls, class_node: ast.ClassDef) -> _FuncToAttrType:
        """クラスのASTノードを解析して、関数とメンバー変数の関係を表す辞書を生成する。"""
        relations = {}

        # プロパティ一覧を取得
        properties = CodeAnalyzer._get_properties(class_node)
        functions = cls._get_functions(class_node)

        # 関数と属性の関係を解析
        for sub_node in ast.walk(class_node):
            if not isinstance(sub_node, ast.FunctionDef):
                # 関数以外は除外
                continue

            function_name = sub_node.name
            if function_name == '__init__':
                # init は除外（グラフが複雑になるため）
                continue

            relations[function_name] = []

            for attr_node in ast.walk(sub_node):
                if not isinstance(attr_node, ast.Attribute):
                    continue

                attribute_name = attr_node.attr
                if attribute_name in properties:
                    # プロパティは除外
                    continue
                if attribute_name in functions:
                    # 関数は除外
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
