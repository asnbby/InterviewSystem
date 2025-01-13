# Interview Process and Q&A System

Program Editor CHENYAN WU

## Setup
- Clone repository 
```
git clone https://github.com/asnbby/InterviewSystem.git
```
- Setup conda environment
```
conda create -n struct_llm python=3.9
conda activate struct_llm
```
- Install packages with a setup file
```
bash setup.sh
```
- Install pytorch module
```
if you are linux or windows:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
```
if you are macos :
pip3 install torch torchvision torchaudio
```
- Download Embedding Model From Hugging-Face(We use stella_en_400M_v5 as our embedding and retrieve model)
```
git lfs clone https://hf-mirror.com/dunzhang/stella_en_400M_v5
```

## Run System
```
bash run.sh
```

## Acknowledgement
```
This project is intended for non-commercial use
If you want to use it for commercial use, please contact wuchenyan0823@gmail.com
```
