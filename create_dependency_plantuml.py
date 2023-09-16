"""Python コードを読みこみ、メソッドとフィールドとの関係を PlantUML 形式で出力するツール.

複数クラス分の PlantUML コードが生成されます。
複数クラス間で同名のメソッド・フィールドが含まれていると、表示がおかしくなります。
その場合はクラスごとに表示するようにしてください。
"""

from __future__ import annotations

import argparse

import create_dependency


class PlantUMLGenerator:
    @classmethod
    def generate(cls, class_relations: create_dependency.ClassToFuncType) -> str:
        plantuml_code = "@startuml\n"
        for class_name, (relations, unused_vars) in class_relations.items():
            plantuml_code += f"rectangle {class_name} {{\n"
            plantuml_code += _AttributeSectionGenerator.generate(relations, unused_vars)
            plantuml_code += _FunctionSectionGenerator.generate(relations)
            plantuml_code += _RelationsSectionGenerator.generate(relations)
            plantuml_code += _UnusedVarsSectionGenerator.generate(unused_vars)
            plantuml_code += "}\n"
        plantuml_code += "@enduml\n"
        return plantuml_code


class _AttributeSectionGenerator:
    @classmethod
    def generate(cls, relations: dict[str, list[str]], unused_vars: set[str]) -> str:
        attributes = set()
        for _, attribute_list in relations.items():
            attributes.update(attribute_list)
        attributes.update(unused_vars)
        attribute_section = ""
        for attribute in attributes:
            attribute_section += f"() {attribute}\n"
        return attribute_section


class _FunctionSectionGenerator:
    @classmethod
    def generate(cls, relations: dict[str, list[str]]) -> str:
        function_section = ""
        for function_name, _ in relations.items():
            function_section += f"() f_{function_name}\n"
        return function_section


class _RelationsSectionGenerator:
    @classmethod
    def generate(cls, relations: dict[str, list[str]]) -> str:
        relations_section = ""
        for function_name, attribute_list in relations.items():
            for attribute in attribute_list:
                relations_section += f"f_{function_name} --> {attribute}\n"
        return relations_section


class _UnusedVarsSectionGenerator:
    @classmethod
    def generate(cls, unused_vars: set[str]) -> str:
        unused_vars_section = ""
        for unused_var in unused_vars:
            unused_vars_section += f"() {unused_var} <<unused>>\n"
        return unused_vars_section


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and generate PlantUML code for function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    class_relations = create_dependency.CodeAnalyzer.analyze_code(file_path)

    plantuml_code = PlantUMLGenerator.generate(class_relations)

    print(plantuml_code)
