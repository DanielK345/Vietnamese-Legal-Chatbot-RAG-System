# Data Pipeline - Vietnamese Legal Traffic Chatbot

Tài liệu mô tả chi tiết quá trình thu thập, xử lý và chuẩn bị dữ liệu cho hệ thống chatbot tư vấn pháp luật giao thông Việt Nam.

### 🎯 Mục tiêu chính
- Thu thập và tổng hợp dữ liệu pháp luật từ 3 nguồn HuggingFace uy tín
- Lọc và trích xuất nội dung liên quan đến giao thông đường bộ
- Tạo synthetic data (806 mẫu) chuyên biệt về giao thông

## 📊 Nguồn dữ liệu chính

### 1. Dataset phuocsang/hoidap-tvpl-20k (finetune_data)
- **Nguồn**: Hugging Face Dataset
- **Mô tả**: Bộ dữ liệu hỏi đáp pháp luật Việt Nam với 20,000+ câu hỏi
- **Số lượng**: 21,529 mẫu ban đầu → 19,536 mẫu training + 1,993 mẫu test  

### 2. Dataset huyhuy123/ViLQA (finetune_data2)
- **Nguồn**: Hugging Face Dataset  
- **Mô tả**: Vietnamese Legal Q&A Dataset chuyên sâu
- **Số lượng**: 43,420 mẫu training (từ 43,588 mẫu gốc)

### 3. Dataset chillies/vn-legal-conversation (finetune_data3)
- **Nguồn**: Hugging Face Dataset
- **Mô tả**: Vietnamese Legal Conversation Dataset với định dạng hội thoại
- **Số lượng**: 34,566 mẫu (gộp từ train/validation/test splits)

### 4. Synthetic Legal Q&A Data
- **Nguồn**: Tự tạo bằng LlamaIndex + OpenAI GPT từ corpus pháp luật giao thông
- **Số lượng**: 806 mẫu 
- **Phương pháp**:
  - Sử dụng corpus pháp luật giao thông làm knowledge base
  - Generate câu hỏi tự động dựa trên nội dung luật
  - Tạo câu trả lời có citation từ văn bản gốc
- **Mục đích**: Bổ sung dữ liệu chuyên biệt về giao thông đường bộ

## 🔄 Quy trình xử lý dữ liệu

### Bước 1: Thu thập dữ liệu từ HuggingFace
```python
# Load datasets từ Hugging Face
from datasets import load_dataset

# Dataset 1: Hỏi đáp pháp luật cơ bản (finetune_data)
dataset1 = load_dataset("phuocsang/hoidap-tvpl-20k")

# Dataset 2: ViLQA mở rộng (finetune_data2)
dataset2 = load_dataset("huyhuy123/ViLQA")

# Dataset 3: Legal Conversation (finetune_data3)  
dataset3 = load_dataset("chillies/vn-legal-conversation")
```

### Bước 2: Lọc dữ liệu liên quan giao thông
Sử dụng từ khóa và pattern matching để lọc:
- **Từ khóa giao thông**: "giao thông", "đường bộ", "xe cộ", "lái xe", "bằng lái"
- **Luật liên quan**: Luật Giao thông đường bộ, Nghị định về xử phạt vi phạm giao thông
- **Chủ đề**: Vi phạm giao thông, an toàn đường bộ, quy tắc lưu thông
=> 8000 rows về luật giao thông đường bộ



### Bước 3: Tạo Synthetic Data (860 mẫu) - Quy trình chi tiết

![Synthetic Data Architecture](asset/synthetic_architecture.png)

### Chất lượng đạt được:
- ✅ **Coverage toàn diện**: 3 nguồn dữ liệu khác nhau cho độ đa dạng cao
- ✅ **Specialized traffic data**: 806 mẫu synthetic chuyên về giao thông với citations chính xác
- ✅ **Automated pipeline**: Quy trình tự động từ crawl → embed → generate → validate
- ✅ **High quality**: Sử dụng GPT-4o-mini với prompt engineering chuyên nghiệp

 ### Bước4: Lọc ra những câu hỏi liên quan đến luật giao thông 
 

