# Hướng dẫn chi tiết về Reward Functions cho Vietnamese Legal GRPO Training

## Tổng quan

Trong quá trình huấn luyện GRPO (Generalized Reward Preference Optimization) cho model Vietnamese Legal Llama3.2-3B, chúng ta sử dụng **5 reward functions chính** được tối ưu hóa để đánh giá chất lượng các response của model:

### **Functions cho Format và Response Structure:**
1. **match_format_exactly** - Kiểm tra format reasoning hoàn hảo (regex matching)
2. **match_format_approximately** - Đánh giá từng thành phần format riêng biệt  
3. **check_response_length_only** - Kiểm tra độ dài response phù hợp

### **Functions cho Content Quality:**
4. **check_vietnamese_language_consistency** - Kiểm tra tính nhất quán ngôn ngữ tiếng Việt  
5. **check_vietnamese_legal_reasoning** - Đánh giá suy luận pháp lý tiếng Việt

> **🎯 Cải tiến chính:** Tách rời việc đánh giá format structure thành 2 functions riêng biệt để có độ chính xác cao hơn và thêm function chuyên biệt cho độ dài response.


## 2. `match_format_exactly`

### Mục tiêu
Kiểm tra response có tuân thủ **hoàn hảo** cấu trúc reasoning format theo regex pattern. Function này có độ chính xác cao nhất và chỉ thưởng nếu format đúng 100%.

### Giải thích code chi tiết

```python
def match_format_exactly(completions, **kwargs):
    scores = []
    for completion in completions:
        score = 0
        response = completion[0]["content"]
        # Match if format is seen exactly!
        if match_format.search(response) is not None: score += 3.0
        scores.append(score)
    return scores
```

**Logic đánh giá:**
1. **Regex matching hoàn hảo**: Sử dụng `match_format` regex pattern để kiểm tra cấu trúc:
   - `<start_working_out>` + nội dung + `<end_working_out>` + `<SOLUTION>` + nội dung + `</SOLUTION>`
   - **+3.0 điểm** nếu format hoàn hảo theo đúng thứ tự
   - **0 điểm** nếu không match hoàn hảo

**Điểm số:** 0 hoặc 3.0 (binary scoring)

---

## 3. `match_format_approximately`

### Mục tiêu
Đánh giá từng thành phần format riêng biệt và cho điểm partial, giúp model học dần từng bước một thay vì chỉ học "all-or-nothing".

### Giải thích code chi tiết

```python
def match_format_approximately(completions, **kwargs):
    scores = []
    for completion in completions:
        score = 0
        response = completion[0]["content"]
        # Count how many keywords are seen - we penalize if too many!
        # If we see 1, then plus some points!
        score += 0.5 if response.count(reasoning_start) == 1 else -1.0
        score += 0.5 if response.count(reasoning_end)   == 1 else -1.0
        score += 0.5 if response.count(solution_start)  == 1 else -1.0
        score += 0.5 if response.count(solution_end)    == 1 else -1.0
        scores.append(score)
    return scores
```

**Logic đánh giá:**

1. **Đếm chính xác từng tag**:
   - `<start_working_out>`: +0.5 nếu có đúng 1 lần, -1.0 nếu 0 hoặc >1 lần
   - `<end_working_out>`: +0.5 nếu có đúng 1 lần, -1.0 nếu 0 hoặc >1 lần  
   - `<SOLUTION>`: +0.5 nếu có đúng 1 lần, -1.0 nếu 0 hoặc >1 lần
   - `</SOLUTION>`: +0.5 nếu có đúng 1 lần, -1.0 nếu 0 hoặc >1 lần

2. **Ưu điểm**: 
   - Cho phép model học từng bước (gradual learning)
   - Phạt nặng việc lặp lại tags
   - Không quan tâm đến thứ tự (khác với `match_format_exactly`)

**Điểm số:** -4.0 đến +2.0

### Chi tiết Reward Function: `reward_solution_length`

#### 🎯 **Mục tiêu:**
Function này được thiết kế để khuyến khích model tạo ra phần `<SOLUTION>...</SOLUTION>` với độ dài **tối ưu** cho câu trả lời pháp luật tiếng Việt:

1. **Tránh câu trả lời quá ngắn**: Đảm bảo cung cấp đủ thông tin pháp lý chi tiết
2. **Khuyến khích độ dài vừa phải**: Không quá dài làm mất tập trung, không quá ngắn thiếu thông tin
3. **Tối ưu cho luật giao thông VN**: Phù hợp với độ phức tạp của câu hỏi pháp luật Việt Nam

#### 📊 **Logic Range Scoring:**

**Target Range (Optimal):**
- **200-400 từ**: `+3.0 điểm` - Độ dài lý tưởng cho câu trả lời pháp luật chi tiết

**Bonus Range (Acceptable):**
- **100-199 từ**: `+1.0 điểm` - Có thể chấp nhận cho câu hỏi đơn giản

**Penalty Ranges:**
- **< 100 từ**: `-2.0 điểm` - Quá ngắn, thiếu thông tin pháp lý cần thiết
- **> 400 từ**: `4.0 - (excess/200)` - Penalty giảm dần theo độ dài vượt quá
  - 500 từ: ~3.5 điểm
  - 600 từ: ~3.0 điểm
  - 800 từ: ~2.0 điểm

**Special Cases:**
- **Không có section `<SOLUTION>`**: `-3.0 điểm` - Penalty nặng nhất

#### 🔍 **Cách tính toán:**
1. Sử dụng regex để extract nội dung trong `<SOLUTION>...</SOLUTION>`
2. Đếm từ Vietnamese bằng pattern `\b\w+\b` (phù hợp với tiếng Việt)
3. Apply scoring logic dựa trên ranges trên
4. Return score cho mỗi completion

#### ⚖️ **Tại sao thiết kế như vậy:**
- **200-400 từ**: Đủ để giải thích điều luật + ví dụ + hướng dẫn thực tế
- **Penalty gradual**: Không cắt cứng mà giảm dần để model học được balance
- **Bonus 100-199**: Khuyến khích model không sợ viết ngắn nếu câu hỏi đơn giản
- **Heavy penalty < 100**: Đảm bảo luôn có thông tin cơ bản về pháp luật


