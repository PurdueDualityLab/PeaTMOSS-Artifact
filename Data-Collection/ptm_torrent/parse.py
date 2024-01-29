import ast
import re
import json

# Create a visitor class to traverse the AST and extract required information
# class HubLoadVisitor(ast.NodeVisitor):
#     def __init__(self):
#         self.pairs = []
    
#     def visit_Call(self, node):
#         if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Attribute):
#             if (
#                 node.func.value.attr == 'hub'
#                 and node.func.value.value.id == 'torch'
#                 and node.func.attr == 'load'
#             ):
#                 args = node.args
#                 if len(args) >= 2:
#                     repo_or_dir = args[0]
#                     model = args[1]
#                     self.pairs.append((repo_or_dir, model))
        
#         self.generic_visit(node)

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
                    self.pairs['repo_or_dir'] = repo_or_dir
                    self.pairs['model'] = model
                for kwarg in keywords:
                    arg_name = kwarg.arg
                    arg_value = self.get_arg_value(kwarg.value)
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
        parsed_tree = ast.parse(snippet)
    except SyntaxError:
        return []
    visitor = HubLoadVisitor()
    visitor.visit(parsed_tree)
    pairs = []
    print(visitor.pairs)
    # for repo_or_dir, model in visitor.pairs:
    #     pairs.append((repo_or_dir.id if isinstance(repo_or_dir, ast.Name) else repo_or_dir.value, 
    #                   model.id if isinstance(model, ast.Name) else model.value))

    # commented_calls = re.findall(r"#.*torch\.hub\.load\(([^)]+)\)", snippet)

    # for call in commented_calls:
    #     args = call.strip().split(',')
    #     for i in range(len(args)):
    #         try:
    #             arg = re.search(r'\'(.+?)\'', args[i].strip(), re.DOTALL).group(1)
    #         except AttributeError:
    #             print(args[i])
    #             continue
    #         if arg.startswith("'") or arg.startswith('"'):
    #             arg = arg[1:]
    #         if arg.endswith("'") or arg.endswith('"'):
    #             arg = arg[:-1]
    #         args[i] = arg
        
    #     pairs.append((args[0], args[1]))

    return pairs

def get_code_snippets(readme_content):
    return re.findall(r'```(?:python)([^`]*)```', readme_content, re.DOTALL)


if __name__ == "__main__":
    with open("/scratch/bell/jone2078/PTMTorrent/ptm_torrent/pytorchhub/data/pytorch_files.json", "r") as f:
        markdown_files = json.load(f)
    
    for markdown_file in markdown_files:
        print(markdown_file["name"])
        code_snippets = get_code_snippets(markdown_file["text"])
        print(f"Number of code snippets {len(code_snippets)}")
        i = 1
        for snippet in code_snippets:
            print(f"Snippet {i}:")
            i += 1
            print(get_repo_and_model_pairs_from_snippet(snippet))
        print()
