# Advanced Llama3.2 (3B) GRPO LoRA - Tài liệu Kỹ thuật

## 📋 Tổng quan

File `Advanced_Llama3_2_(3B)_GRPO_LoRA.ipynb` thực hiện **Group Relative Policy Optimization (GRPO)** cho model Vietnamese Legal Llama3.2-3B đã qua SFT, nhằm cải thiện chất lượng câu trả lời thông qua reward-based learning.

### 🎯 Mục tiêu 
- **Reinforcement Learning**: Sử dụng GRPO để tối ưu chất lượng response
- **Structured Reasoning**: Training model output format `<start_working_out>` và `<SOLUTION>`

## 🧠 GRPO Framework

### Khái niệm GRPO
**Group Relative Policy Optimization** là một variant của PPO được thiết kế để:
- **Group-based Comparison**: So sánh responses trong cùng một group
- **Relative Scoring**: Đánh giá tương đối thay vì absolute scoring  
- **Stability**: Ổn định hơn PPO truyền thống cho conversational AI
- **Efficiency**: Ít computational overhead hơn

### Structured Response Format
Model được train để output theo format:
```
<start_working_out>
[Phần phân tích và suy nghĩ của AI]
<end_working_out>

<SOLUTION>
[Câu trả lời cuối cùng]
</SOLUTION>
```

## 🔧 Cấu hình Kỹ thuật

### Model Configuration
```python
max_seq_length = 1536         # Optimized cho T4 15GB
lora_rank = 32               # Balance quality/memory
load_in_4bit = False         # Disable cho GRPO training
fast_inference = True        # Enable vLLM backend
gpu_memory_utilization = 0.85 # Conservative cho T4
```

### GRPO Specific Settings  
```python
reasoning_start = "<start_working_out>"
reasoning_end = "<end_working_out>"
solution_start = "<SOLUTION>"
solution_end = "</SOLUTION>"

system_prompt = """Bạn là một trợ lý AI chuyên về luật giao thông Việt Nam. 
Khi trả lời câu hỏi, hãy:
1. Suy nghĩ và phân tích câu hỏi trong phần <start_working_out> <end_working_out>
2. Đưa ra câu trả lời chính xác trong phần <SOLUTION></SOLUTION>"""
```

### LoRA Configuration
```python
r = 32                       # LoRA rank cho GRPO
target_modules = [           # Full attention + MLP
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]
lora_alpha = 32             # Scaling factor
use_gradient_checkpointing = "unsloth"  # Memory optimization
```

