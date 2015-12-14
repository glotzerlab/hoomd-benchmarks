import signac
import json
import os
import locale

locale.setlocale(locale.LC_ALL, 'en_US')

project = signac.contrib.get_project()

def format_version(version):
    sv = "";
    for v in version[:-1]:
        sv = sv + str(v) + '.'

    sv = sv + str(version[-1]);
    return sv;

def read_rows(benchmark):
    global project

    # Read in rows of performance data
    rows = []
    for job in project.find_jobs(dict(benchmark=benchmark)):
            row = job.statepoint();
            try:
                meta = json.load(open(os.path.join(job.workspace(), 'metadata.json')))[0]
            except IOError:
                # skip missing files
                continue

            row['mps'] = meta['user']['mps'];
            row['N'] = meta['data.system_data']['particles']['N'];
            row['num_ranks'] = meta['context']['num_ranks'];
            row['compiler_version'] = meta['hoomd']['compiler_version'];
            row['cuda_version'] = meta['hoomd']['cuda_version'];
            row['hoomd_version'] = meta['hoomd']['hoomd_version'];
            row['gpu'] = meta['context']['gpu'];
            row['mode'] = meta['context']['mode'];

            compile_flags = meta['hoomd']['hoomd_compile_flags'].split();
            row['precision'] = 'n/a'
            if 'SINGLE' in compile_flags:
                row['precision'] = 'single';
            if 'DOUBLE' in compile_flags:
                row['precision'] = 'double';

            rows.append(row)

    return rows

def make_table(rows):
    table =  "| Date | System | Compiler | CUDA | HOOMD | Precision | N | CPU | GPU | Ranks | MPS (millions) |\n";
    table += "|------|--------|----------|------|-------|-----------|---|-----|-----|-------|---------------:|\n";

    rows.sort(key=lambda v: (v['hoomd_version'], v['mps']), reverse=True);

    for row in rows:
        cpu = row['cpu'];
        gpu = row['gpu'];

        # mark the cpu or gpu bold depending on the mode
        if row['mode'] == 'cpu':
            cpu = '**' + cpu + '**';
        if row['mode'] == 'gpu':
            gpu = '**' + gpu + '**';

        table += "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} | {9} | {10:4.2f} |\n".format(row['date'],
                                                                                               row['system'],
                                                                                               row['compiler_version'],
                                                                                               format_version(row['cuda_version']),
                                                                                               format_version(row['hoomd_version']),
                                                                                               row['precision'],
                                                                                               locale.format("%d", row['N'], grouping=True),
                                                                                               cpu,
                                                                                               gpu,
                                                                                               row['num_ranks'],
                                                                                               row['mps'] / 1e6)

    return table;
