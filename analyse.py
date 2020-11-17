# analyse.py
#!/usr/bin/env python3
# encoding: utf-8

import re, os, sys, types, linecache

class PyFile:
    def __init__(self, f):
        f = open(f, 'rb')
        code_str = f.read()
        f.close()
        self.code = compile(code_str, '', 'exec')
        self.lines = 1
        self.line_no = []

    def count_lines(self):
        self.lines, self.line_no = count_lines(self.code, self.lines, self.line_no)

def count_lines(code, lines, line_no):
    lines += len(code.co_lnotab) / 2
    first_lineno = code.co_firstlineno
    lb_ranges = [code.co_lnotab[b * 2 + 1] for b in range(len(code.co_lnotab) // 2)]
    line_no.append(first_lineno)
    for lb in lb_ranges:
        first_lineno += lb
        line_no.append(first_lineno)

    for const in code.co_consts:
        if type(const) == types.CodeType:
            lines, line_no = count_lines(const, lines, line_no)
    return lines, line_no

def analyse(file_name):
    result = ''
    pf = PyFile(file_name)
    pf.count_lines()
    executable_len = pf.lines

    f = open('coverage.txt', 'r')
    f.readline()

    # function coverage
    funcs = f.readline()[:-1]
    func_call_tuple = f.readline()[:-1]

    call_tree = {}
    func_called_set = []
    func_ncalled = []
    func_coverage = 0

    if len(funcs) and len(func_call_tuple):
        func_called = []
        func_called_tuple = []

        funcs = funcs.split(',')
        func_call_tuple = func_call_tuple.split(';')

        for i in func_call_tuple:
            tup = re.sub(r'\(|\)|\s|\'', '', i)
            tup = tuple(tup.split(','))

            func_called_tuple.append(tup)
            func_called.append(tup[1])

        func_called_set = list(set(func_called)) # De-duplication

        for i in funcs:
            if i not in func_called_set:
                func_ncalled.append(i)

        for i in func_called_tuple:
            if i[0] not in call_tree:
                call_tree[i[0]] = []
            call_tree[i[0]].append(i[1])

        func_coverage = len(func_called_set) / len(funcs) * 100

    result += 'call: {}\n'.format(func_called_set)
    result += 'call tree: {}\n'.format(call_tree)
    result += 'not called: {}\n'.format(func_ncalled)
    result += 'call number: {}\n'.format(len(func_called_set))
    result += 'not called number: {}\n'.format(len(func_ncalled))
    result += 'func coverage: {}%\n'.format(func_coverage)
    result += '\n'

    # statement coverage
    executed_lines = f.readline()[:-1]
    statement_coverage = 0

    if len(executed_lines):
        executed_len = len(set(executed_lines.split(',')))
        statement_coverage = executed_len / executable_len * 100

    result += 'executable lines: {}\n'.format(int(executable_len))
    result += 'executed lines: {}\n'.format(executed_len)
    result += 'missed lines: {}\n'.format(int(executable_len - executed_len))
    result += 'statement coverage: {}%\n'.format(statement_coverage)
    result += '\n'

    # branch coverage
    executed_tuple_list = []
    executed_tuple = f.readline()[:-1]
    f.close()
    missed_branch = 0
    branch_count = 0
    branch_coverage = 0

    if len(executed_tuple):
        executed_tuple = executed_tuple.split(';')

        for i in executed_tuple:
            tup = re.sub(r'\(|\)|\s|\'', '', i)
            executed_tuple_list.append(tuple(tup.split(',')))

        executed_tuple_set = list(set(executed_tuple_list))

        for i in executed_tuple_set:
            target = i[0]
            target_count = 0
            for j in executed_tuple_set:
                if target == j[0]:
                    target_count += 1
            if target_count < 2:
                missed_branch += 1

        keyword_count = 0
        for i in pf.line_no:
            pre_statement = linecache.getline(file_name, i)
            pre_statement_parts = re.split(r'\s|\(|\,|\)|\:', pre_statement)
            for word in pre_statement_parts:
                if word == 'if' or word == 'elif' or word == 'while' or word == 'for':
                    keyword_count += 1
                    break

        branch_count = keyword_count * 2
        branch_coverage = (branch_count - missed_branch) / branch_count * 100

    result += 'branch: {}\n'.format(branch_count)
    result += 'missed branch: {}\n'.format(missed_branch)
    result += 'branch coverage: {}%\n'.format(branch_coverage)

    f = open('analyse_result.txt', 'w+')
    f.write(result)
    f.close()

    print(result)

try:
    f = open('coverage.txt', 'r')
except IOError:
    print('coverage.txt is not found.')
else:
    file_name = f.readline()[:-1]
    f.close()

    if not os.path.exists(file_name):
        print(file_name + ' is not found.')
        sys.exit(1)

    analyse(file_name)
