# trace.py
#!/usr/bin/env python3
# encoding: utf-8

import linecache, os, re, sys

trace_file = sys.argv[1]

if os.path.exists(trace_file):
    pass
else:
    print('File not found: {}'.format(trace_file))
    sys.exit(1)

file_abspath = os.path.abspath(trace_file)
pyc_file = file_abspath + 'c'

if os.path.exists(pyc_file):
    os.remove(pyc_file)

calls = []
call_lines = []
exe_lines = []
exe_pairs = []

pre_lineno = 0
result = ''

def trace_func(frame, event, arg):
    global trace_file
    global calls
    global call_lines
    global exe_lines
    global exe_pairs
    global pre_lineno
    global result

    co = frame.f_code
    file_name = co.co_filename

    if not file_name.endswith(trace_file):
        # Ignore calls not in trace_file module
        return

    func_name = co.co_name
    line_no = frame.f_lineno

    if event == 'call':
        caller_frame = frame.f_back
        caller_frame_func_name = caller_frame.f_code.co_name
        caller_frame_line_no = caller_frame.f_lineno

        call_lines.append((caller_frame_func_name, func_name))

    elif event == 'line':
        statement = linecache.getline(trace_file, line_no)
        pre_statement = linecache.getline(trace_file, pre_lineno)
        statement_parts = re.split(r'\s|\(|\,|\)|\:', statement)
        pre_statement_parts = re.split(r'\s|\(|\,|\)|\:', pre_statement)

        if 'def' in statement_parts:
            calls.append(re.sub(r'def\s*(.*)\(.*\):\s*\n', r'\1', statement))

        for word in pre_statement_parts:
            if word == 'if' or word == 'elif' or word == 'while' or word == 'for':
                if pre_lineno != -1:
                    exe_pairs.append((pre_lineno, line_no))
                break

        exe_lines.append(line_no)
        pre_lineno = line_no
        result += 'line {}: {}\n'.format(line_no, statement.rstrip())

    elif event == 'return':
        statement = linecache.getline(file_name, line_no)
        statement_parts = re.split(r'\s|\(|\,|\)|\:', statement)
        for word in statement_parts:
            if word == 'if' or word == 'elif' or word == 'while' or word == 'for':
                exe_pairs.append((line_no, -1))
                pre_lineno = -1
                break

    return trace_func

sys.settrace(trace_func)

__import__(trace_file.replace('.py', ''))

print('\n' + result)

f = open("trace_result.txt", "w+")
f.write(result)
f.close()

f = open('coverage.txt', 'w+')

f.writelines(file_abspath)
f.writelines('\n')
f.writelines(','.join(i for i in calls))
f.writelines('\n')
f.writelines(';'.join(str(i) for i in call_lines[1:]))
f.writelines('\n')
f.writelines(','.join(str(i) for i in exe_lines))
f.writelines('\n')
f.writelines(';'.join(str(i) for i in exe_pairs))

f.close()
