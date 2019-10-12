import signac
import locale

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

project = signac.get_project()

def format_version(version):
    sv = "";
    for v in version[:-1]:
        sv = sv + str(v) + '.'

    sv = sv + str(version[-1]);
    return sv;

def make_table():
    table =  "| Benchmark | Compiler  | CUDA | HOOMD | Precision | N | GPU | Ranks | MPS|\n";
    table += "|-----------|-----------|------|-------|-----------|---|-----|-------|---------|\n";
    
    from collections import Counter

    for job in project.find_jobs():
        for key in job.doc:
            row = job.doc[key]
            gpu = row['gpu']

            gpus = Counter(gpu).keys()
            counts = Counter(gpu).values()

            gpu_str = ''
            for k,c in zip(gpus,counts):
                gpu_str += '['+k+']'

                if c > 1:
                    gpu_str += '*'+str(c)

            # mark the cpu or gpu bold depending on the mode
            table += "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8:4.2f} |\n".format(job.statepoint()['benchmark'],
                                                                                       row['compiler_version'],
                                                                                       format_version(row['cuda_version']),
                                                                                       format_version(row['hoomd_version']),
                                                                                       row['precision'],
                                                                                       locale.format_string("%d", row['N'], grouping=True),
                                                                                       gpu_str,
                                                                                       row['num_ranks'],
                                                                                       row['mps'])

    return table;

if __name__ == '__main__':
    table = make_table()
    print(table)

