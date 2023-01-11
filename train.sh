#!/bin/sh

#SBATCH --partition=cpu-opteron
#SBATCH --job-name=RL-AI
#SBATCH --output=%x.out
#SBATCH --error=%x.err
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --mem=85G
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tancheelam2@gmail.com
#SBATCH --hint=nomultithread

source /home/user/lobbeytan/zelda-ai-game/venv/bin/activate

python main.py
