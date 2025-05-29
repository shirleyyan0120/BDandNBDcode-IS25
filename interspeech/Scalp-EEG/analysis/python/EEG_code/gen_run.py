datasets = ['B_EEG','NB_EEG']
decision_windows = [1, 2, 5, 10]
# models = ['CNN_baseline','STANet','DenseNet_37-I3D']
models = ['DenseNet_37-I3D']

cnt = 0
for i in range(len(datasets)):
    dataset = datasets[i]
    for j in range(len(decision_windows)):
        decision_window = decision_windows[j]
        for k in range(len(models)):
            model = models[k]
            run_file = "run{}.slurm".format(cnt)
            with open(run_file, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("#SBATCH -o ./log/%j.out\n")
                f.write("#SBATCH -e ./log/%j.err\n")
                f.write("#SBATCH --ntasks-per-node=8\n")
                f.write("#SBATCH --partition=GPUA800\n")
                f.write("#SBATCH -J {}_{}_{}\n".format(dataset, decision_window, model))
                f.write("#SBATCH --gres=gpu:1\n\n")
                f.write("python main.py --dataset {} --decision_window {} --model {}\n".format(dataset, decision_window, model))
            cnt += 1