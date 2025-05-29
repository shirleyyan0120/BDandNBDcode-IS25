datasets = ['B_EEG', 'NB_EEG', 'pNB_EEG']
# models = ['CNN_baseline', 'STANet']
models = ['STANet']
decision_windows = [0.5,1,2]
cnt = 3
for dataset in datasets:
    run_file = "run_{}.slurm".format(cnt)
    with open(run_file, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH -o ./log/%j.out\n")
        f.write("#SBATCH -e ./log/%j.err\n")
        f.write("#SBATCH --ntasks-per-node=8\n")
        f.write("#SBATCH --partition=GPUA800\n")
        f.write("#SBATCH -J {}_batch_job\n".format(dataset))
        f.write("#SBATCH --gres=gpu:1\n\n")

        for decision_window in decision_windows:
            for model in models:
                f.write("python main.py --dataset {} --decision_window {} --model {}\n".format(dataset, decision_window, model))
    cnt += 1
    print("Batch script generated: {}".format(run_file))
