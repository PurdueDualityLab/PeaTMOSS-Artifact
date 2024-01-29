import ast
import re
import json
import petl as etl

# Visitor class to traverse the AST and extract relevant information
class HubLoadVisitor(ast.NodeVisitor):
    def __init__(self):
        self.pairs = {}
    
    def visit_Assign(self, node):
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Str)
        ):
            var_name = node.targets[0].id
            var_value = node.value.s
            self.pairs[var_name] = var_value
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Attribute):
            if (
                node.func.value.attr == 'hub'
                and node.func.value.value.id == 'torch'
                and node.func.attr == 'load'
            ):
                args = node.args
                keywords = node.keywords
                if args:
                    repo_or_dir = self.get_arg_value(args[0])
                    model = self.get_arg_value(args[1])
                    self.pairs['repo_or_dir'] = [repo_or_dir] if self.pairs.get('repo_or_dir') is None else self.pairs['repo_or_dir'] + [repo_or_dir]
                    self.pairs['model'] = [model] if self.pairs.get('model') is None else self.pairs['model'] + [model]
                for kwarg in keywords:
                    arg_name = kwarg.arg
                    arg_value = self.get_arg_value(kwarg.value)
                    if arg_name == 'repo_or_dir' or arg_name == 'model':
                        self.pairs[arg_name] = [arg_value] if self.pairs.get(arg_name) is None else self.pairs[arg_name] + [arg_value]
                    else:
                        self.pairs[arg_name] = arg_value
        self.generic_visit(node)
    
    def get_arg_value(self, arg_node):
        if isinstance(arg_node, ast.Str):
            return arg_node.s
        elif isinstance(arg_node, ast.Name):
            return self.pairs.get(arg_node.id, '')
        return ''

def get_repo_and_model_pairs_from_snippet(snippet):
    try:
        parsed_tree : ast.Module = ast.parse(snippet, type_comments=True)
    except SyntaxError:
        return [], []
    visitor = HubLoadVisitor()
    visitor.visit(parsed_tree)
    repos = visitor.pairs.get('repo_or_dir', [])
    models = visitor.pairs.get('model', [])
    commented_calls = re.findall(r"#.*torch\.hub\.load\(([^)]+)\)", snippet)

    for call in commented_calls:
        args = call.strip().split(',')
        for i in range(len(args)):
            try:
                arg = re.search(r'[\'\"](.+?)[\'\"]', args[i].strip(), re.DOTALL).group(0)
            except AttributeError:
                print(f"Error parsing arg: {args[i]}")
                continue
            if arg.startswith("'") or arg.startswith('"'):
                arg = arg[1:]
            if arg.endswith("'") or arg.endswith('"'):
                arg = arg[:-1]
            args[i] = arg
        
        repos.append(args[0])
        models.append(args[1])

    return repos, models

def get_code_snippets(readme_content):
    return re.findall(r'```(?:python)(.*?)```', readme_content, re.DOTALL)

import torch
import torchvision

if __name__ == "__main__":
    table = etl.fromcsv("pytorch_transformed_dedup_full.csv")
    table = etl.convert(table, 'context_id', lambda v: v.rsplit('/', 1)[1])
    table.tocsv("pytorch_transformed_dedup_full_model_context_id.csv")
    