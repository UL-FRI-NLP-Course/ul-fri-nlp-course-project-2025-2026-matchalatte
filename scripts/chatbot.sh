#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem-per-gpu=64G
#SBATCH --time=00:30:00
#SBATCH --output=logs/chat-%J.out
#SBATCH --error=errors/error-%J.err
#SBATCH --job-name="travel_chatbot"

module load Python/3.10.8-GCCcore-12.2.0

mkdir -p logs
mkdir -p errors

source my_env/bin/activate

srun python code/chatbot.py "$1"
