import ast
from bisect import bisect_right
from scalpel.SSA.const import SSA
from scalpel.core.mnode import MNode    # This core file has some customization
import traceback
import logging

logging.basicConfig(filename='codeextraction_dep.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


'''
Usage example: 
    es = ExtractSource(source)   # source: python 3 source code
    es.set_blob(fileID)
    es.set_importname(importname)   # for example, "torch", "transformers"
    es.set_targets_info(targets)    # for example, targets = [{'class_to_check': '', 'method_to_check': "from_pretrained"}] 
    values = es.fetch_match_called()
'''


class ExtractSource():
    def __init__(self, source):
        self.mnode = MNode("local")
        self.mnode.source = source

        self.import_dict = {}
        self.func_defs = []
        self.func_calls = []
        self.importname = ""
        self.classname = ""
        self.method = ""
        self.function_with_startln = {}
        self.function_with_endln = {}
        self.all_options_import = []
        self.blob = ""   # id of a file
        self.params_info = {}
        self.targets_info = []

    def set_importname(self, importname):
        self.importname = importname

    def set_targets_info(self, targets):
        self.targets_info = targets

    def set_classname(self, classname):
        self.classname = classname

    def set_method(self, method):
        self.method = method

    def set_blob(self, blob):
        self.blob = blob

    def get_ast(self):
        try:
            self.mnode.gen_ast()
        except Exception as e:
            logging.error('exception in AST generation: ' + self.blob + str(e))

    def get_imports(self):
        try:
            self.import_dict = self.mnode.parse_import_stmts_extended()  # scalpel.core.mnode has been modified
            self._consider_import()
        except Exception as e:
            logging.error('exception in imports: ' + self.blob + str(e))

    def get_func_calls(self):
        try:
            self.func_calls = self.mnode.parse_func_calls()
        except Exception as e:
            print('exception in func_calls:' + self.blob  + str(e))

    def get_func_defs(self):
        try:
            self.func_defs = self.mnode.parse_func_defs_extended()  # scalpel.core.mnode has been modified
            self.extract_fun_defs()
        except Exception as e:
            logging.error('exception in func_defs: ' + self.blob + str(e))

    def _find_val(self, arr, x):
        i = bisect_right(arr, x)
        if i == 0:
            return arr[0]
        return arr[i - 1]

    def _consider_import(self):
        keys_list = list(self.import_dict.keys())
        for each_val in keys_list:
            dotted_keys = each_val.split('.')
            self.all_options_import.extend(dotted_keys)
        values_list = self.import_dict.values()
        for each_val in values_list:
            dotted_values = each_val.split('.')
            self.all_options_import.extend(dotted_values)
        self.all_options_import = list(set(self.all_options_import))

    def extract_fun_defs(self):
        for func_def in self.func_defs:
            func_name = func_def["name"]
            func_scope = func_def["scope"]
            lineno = func_def["lineno"]
            end_linno = func_def["end_linno"]
            if func_scope != 'mod':
                func_name = func_scope + "." + func_name

            self.function_with_startln[lineno] = {'name': func_name, 'scope': func_scope, 'end_linno': end_linno}
            self.function_with_endln[end_linno] = func_name

    # This method has been used to find the usage matched with the signature
    def fetch_match_called(self):
        matched_result = []

        self.get_ast()
        if self.mnode.ast is None:
            logging.error('exception in ast generation: ' + self.blob)

        if self.mnode.ast is not None:
            self.get_imports()
            self.get_func_calls()

            try:
                for call_info in self.func_calls:

                    call_data = {}
                    call_name = call_info["name"]
                    dotted_parts = call_name.split(".")

                    if dotted_parts[0] in self.import_dict:  # ....... nltk.data?
                        dotted_parts = [self.import_dict[dotted_parts[0]]] + dotted_parts[1:]
                        call_name = ".".join(dotted_parts)

                    dotted_parts_import = call_name.split(".")
                    # if this function calls is from a imported module
                    for target_info in self.targets_info:
                        model_usage_call = self.importname
                        method_to_check = target_info['method_to_check']
                        class_to_check = target_info['class_to_check']

                        if dotted_parts[0] in self.all_options_import:  # not from variable, coming from modules
                            model_usage_call = self.importname
                        # if self.importname == "transformers":
                        #     model_usage_call = method_to_check = target_info['method_to_check']

                        if model_usage_call == dotted_parts_import[0]:
                            if method_to_check == 'hub.load' and model_usage_call == 'torch':
                                if 'hub' in dotted_parts_import[1:]:
                                    ind = dotted_parts_import.index('hub')
                                    if ind:
                                        if dotted_parts_import[ind+1] == 'load':
                                            call_data['name'] = call_name
                                            call_data['lineno'] = call_info['lineno']
                                            call_data['params'] = call_info['params']
                                            matched_result.append(call_data)

                            else:
                                if method_to_check in dotted_parts_import[1:]:

                                    ind = dotted_parts_import.index(method_to_check)

                                    if class_to_check == method_to_check:
                                        if ind == len(dotted_parts_import) - 1:
                                            class_to_check = ""
                                        else:
                                            ind = 0
                                    if (class_to_check == '' and ind) or (len(class_to_check) and class_to_check == dotted_parts_import[ind - 1]):
                                        # todo: direct mapping is possible
                                        call_data['name'] = call_name
                                        call_data['lineno'] = call_info['lineno']
                                        call_data['params'] = call_info['params']
                                        if model_usage_call == 'spacy':
                                            if "spacy.load" in call_name:
                                                matched_result.append(call_data)
                                        else:
                                            matched_result.append(call_data)
            except Exception as e:
                logging.error('exception in fetch_match_called: ' + str(e))
                traceback.print_exc()

        return matched_result

    def fetch_caller(self, line):
        name_caller = ""
        try:
            defs_lineno_start = list(self.function_with_startln.keys())
            defs_lineno_end = list(self.function_with_endln.keys())

            if len(defs_lineno_end):
                defs_lineno_end.sort()
                defs_lineno_start.sort()

                if defs_lineno_start[0] < line <= defs_lineno_end[len(defs_lineno_end) - 1]:
                    # last_function_start = defs_lineno_start[len(defs_lineno_start) - 1]
                    start = self._find_val(defs_lineno_start, line)
                    name = self.function_with_startln[start]['name']
                    # make sure the endline
                    end_ln = self.function_with_startln[start]['end_linno']
                    if line <= end_ln:
                        name_caller = name

                    # if line > last_function_start:
                    #     name_caller = self.function_with_startln[last_function_start]
                    # else:
                    #     start = self._find_val(defs_lineno_start, line)
                    #     name_caller = self.function_with_startln[start]
        except Exception as e:
            logging.error('exception at fetch caller: ' + str(e))

        return name_caller

    def fetch_called_and_imports(self):
        matched_result = []

        self.get_ast()

        if self.mnode.ast is None:
            logging.error('exception during AST: ' + self.blob)
        if self.mnode.ast is not None:
            self.get_imports()
            self.get_func_calls()

            try:
                for call_info in self.func_calls:
                    call_data = {}
                    call_name = call_info["name"]
                    dotted_parts = call_name.split(".")

                    if dotted_parts[0] in self.import_dict:  # ....... nltk.data?
                        dotted_parts = [self.import_dict[dotted_parts[0]]] + dotted_parts[1:]
                        call_name = ".".join(dotted_parts)

                    call_data['name'] = call_name
                    call_data['lineno'] = call_info['lineno']
                    call_data['params'] = call_info['params']
                    matched_result.append(call_data)
            except Exception as e:
                logging.error('exception in fetch_match_called: ' + str(e))
                traceback.print_exc()

        return matched_result

