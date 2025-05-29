datasets = ['B_EEG', 'NB_EEG', 'pNB_EEG']
models = ['CNN_baseline', 'STANet']
decision_windows = [1, 2, 5, 10]


run_file = "run_all.slurm"
with open(run_file, "w") as f:
    f.write("#!/bin/bash\n")
    f.write("#SBATCH -o ./log/%j.out\n")
    f.write("#SBATCH -e ./log/%j.err\n")
    f.write("#SBATCH --ntasks-per-node=8\n")
    f.write("#SBATCH --partition=GPUA800\n")
    f.write("#SBATCH -J batch_job\n")
    f.write("#SBATCH --gres=gpu:1\n\n")

    cnt = 0
    for dataset in datasets:
        for decision_window in decision_windows:
            for model in models:
                f.write("echo 'Running task {}'\n".format(cnt))
                f.write("python main.py --dataset {} --decision_window {} --model {}\n".format(dataset, decision_window, model))
                f.write("\n")
                cnt += 1

print("Batch script generated: {}".format(run_file))
