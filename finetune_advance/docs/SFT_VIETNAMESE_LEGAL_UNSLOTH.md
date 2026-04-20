# SFT Vietnamese Legal Unsloth - Tài liệu Kỹ thuật

### 🎯 Mục tiêu
- Fine-tune model Llama-3.2-3B cho domain pháp luật giao thông Việt Nam
- Tối ưu hóa cho GPU Tesla T4 (16GB VRAM) trên Kaggle/Colab
- Tạo ra model có khả năng trả lời chính xác các câu hỏi pháp luật giao thông

### 🚀 Công nghệ sử dụng
- **Base Model**: `unsloth/Llama-3.2-3B-Instruct-bnb-4bit`

## 🔧 Cấu hình Kỹ thuật

### Model Configuration
```python
max_seq_length = 1536      # Phủ 95% samples
dtype = None               # Auto-detect (FP16 cho T4)
load_in_4bit = True        # Quantization để tiết kiệm VRAM
model_name = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"
```

### LoRA Parameters
```python
r = 32                     # LoRA rank (balance quality/speed)
lora_alpha = 32           # Scaling factor
target_modules = [         # Train all attention & MLP layers
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]
lora_dropout = 0          # Optimized by Unsloth
bias = "none"             # Optimized setting
```

### Training Arguments
```python
num_train_epochs = 2                    # Sufficient for legal domain
per_device_train_batch_size = 4         # Max for T4 16GB
gradient_accumulation_steps = 4         # Effective batch = 16
learning_rate = 2e-4                    # Standard for LoRA
optim = "adamw_8bit"                   # Memory efficient
lr_scheduler_type = "cosine"           # Cosine annealing
```

## 📊 Dữ liệu

### Data Split
- **Training**: 90% samples
- **Validation**: 5% samples  
- **Test**: 5% samples

### Chat Template
Sử dụng format chuẩn Llama 3.2 Instruct:
```xml
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{SYSTEM}<|eot_id|><|start_header_id|>user<|end_header_id|>
{INPUT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{OUTPUT}<|eot_id|>
```
