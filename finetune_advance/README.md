# 🚀 Vietnamese Legal AI - Fine-tuning Project

Fine-tuning Llama 3.2 3B model for Vietnamese legal question answering, specifically focusing on traffic law domain.

## 📋 Project Structure

```
Finetune_advance/
├── data_pipeline/          # Data processing and preparation
│   ├── data/              # Training datasets
│   │   ├── finetune_data/
│   │   ├── finetune_data2/
│   │   ├── finetune_data3/
│   │   └── finetune_llm/  # Main training data
│   └── utils/             # Data processing notebooks
├── downloaded_model/       # Pre-downloaded model files
├── finetune/              # Fine-tuning scripts
│   ├── sft_vietnamese_legal_unsloth.ipynb  # Main training notebook
│   └── REINFORCEMENT_LEARNING_GUIDE.md
└── download_and_upload_model.py
```

## 🎯 Features

- **Model**: Llama 3.2 3B Instruct (optimized with Unsloth)
- **Task**: Vietnamese Legal Question Answering
- **Domain**: Traffic Law
- **Technique**: Supervised Fine-Tuning (SFT) with LoRA
- **Optimization**: 4-bit quantization, memory-efficient training

## 🛠️ Tech Stack

- **Framework**: Unsloth (2x faster training)
- **Model**: Meta Llama 3.2 3B Instruct
- **Training**: LoRA (Low-Rank Adaptation)
- **Monitoring**: Weights & Biases (WandB)
- **Hardware**: Optimized for Kaggle T4 GPU (16GB VRAM)

## 📊 Dataset

- **Format**: JSONL with instruction-input-output structure
- **Language**: Vietnamese
- **Domain**: Traffic law questions and answers
- **Split**: 90% train, 5% validation, 5% test

## 🚀 Quick Start

### 1. Installation

```bash
pip install unsloth transformers datasets trl wandb
```

### 2. Training

Open and run `finetune/sft_vietnamese_legal_unsloth.ipynb` in Kaggle or local Jupyter environment.

### 3. Key Configuration

```python
model_name = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"
max_seq_length = 1536
lora_r = 32
learning_rate = 2e-4
num_epochs = 3
```

## 📈 Training Details

- **Max Sequence Length**: 1536 tokens
- **Batch Size**: 8 per device
- **Gradient Accumulation**: 4 steps (effective batch size: 32)
- **Learning Rate**: 2e-4 with cosine annealing
- **Optimizer**: AdamW 8-bit
- **Training Time**: ~3-4 hours on T4 GPU

## 🎓 LoRA Configuration

```python
r = 32                    # LoRA rank
lora_alpha = 32          # Scaling factor
target_modules = [       # Train all attention & MLP layers
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]
```

## 💾 Outputs

- **LoRA Adapters**: ~100-200MB (lightweight)
- **GGUF Models**: For Ollama/llama.cpp deployment
- **Checkpoints**: Saved every 50 steps

## 📊 Monitoring

Training metrics are logged to Weights & Biases:
- Training/Validation loss
- Learning rate schedule
- GPU memory usage
- Training time per epoch

## 🧪 Inference

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="vietnamese_legal_lora",
    max_seq_length=1536,
)

FastLanguageModel.for_inference(model)

# Generate response
response = model.generate(prompt, max_new_tokens=512)
```

## 📝 Data Format

```json
{
  "instruction": "Hãy trả lời câu hỏi về luật giao thông sau:",
  "input": "Phạt bao nhiêu khi không đội mũ bảo hiểm?",
  "output": "Theo Nghị định 100/2019/NĐ-CP..."
}
```

## 🎯 Use Cases

- Legal consultation chatbot
- Traffic law Q&A system
- Legal document assistant
- Educational tool for traffic regulations

## 🔧 Requirements

- Python 3.8+
- CUDA-capable GPU (16GB+ VRAM recommended)
- 20GB+ disk space

## 📚 Resources

- [Unsloth Documentation](https://docs.unsloth.ai)
- [Llama 3.2 Model](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [Training Notebook](finetune/sft_vietnamese_legal_unsloth.ipynb)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Meta AI for Llama 3.2
- Unsloth team for optimization framework
- Vietnamese legal dataset contributors

---

**Note**: This project is optimized for Kaggle T4 GPUs with 30h/week limit. Adjust batch sizes and gradient accumulation for different hardware configurations.
