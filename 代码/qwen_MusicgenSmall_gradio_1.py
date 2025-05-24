# 仅首次运行
!pip install gradio
!pip install transformers torchaudio audiocraft accelerate bitsandbytes

#1 qwen-部署musicgen-small(colab)
import json
import random
import torch
import requests
import torchaudio
import gradio as gr
from transformers import MusicgenProcessor, MusicgenForConditionalGeneration

# Qwen API 配置
QWEN_API_KEY = "sk-"  # 阿里云DashScope Key (qwen2.5)
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 加载数据（JSONL），格式为 {"scene": "...", "music": "..."}
scene_music_data = []
with open("musicgen_scene_music_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        scene_music_data.append(json.loads(line.strip()))

# 加载 MusicGen 模型
MODEL_NAME = "facebook/musicgen-small" # 算力充足可替换为medium/large
processor = MusicgenProcessor.from_pretrained(MODEL_NAME)
model = MusicgenForConditionalGeneration.from_pretrained(MODEL_NAME)
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

# ==========================few-shot===================================
# Step 1: 构造多轮对话格式的示例 k为每轮对话使用的示例数量，默认=2
def build_few_shot_messages(k=2):
    examples = random.sample(scene_music_data, k)
    messages = [{"role": "system", "content": "You are a music cognition expert converting restaurant scene descriptions into music prompts suitable for MusicGen."}]
    for ex in examples:
        messages.append({"role": "user", "content": f"Scene: {ex['scene']}"})
        messages.append({"role": "assistant", "content": ex['music']})
    return messages

# Step 2: 训练后测试
def generate_music_description(scene_desc):
    messages = build_few_shot_messages(k=2)
    messages.append({"role": "user", "content": f"Scene: {scene_desc}"})

    # 请求头构建
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen2.5-14b-instruct",
        "input": {"messages": messages},
        "parameters": {"temperature": 0.5, "max_tokens": 200}
    }
    response = requests.post(QWEN_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result.get("output", {}).get("text", "No output")
    else:
        return f"Error: {response.text}"

# ==========================音乐生成===================================
# Step 3: 生成音乐+释放显存
def generate_music_from_text(music_desc, duration=12):
    inputs = processor(text=[music_desc], padding=True, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=600, do_sample=False)
    waveform = torch.tensor(outputs[0].cpu())
    sample_rate = 32000
    audio_path = "generated_music.wav"
    torchaudio.save(audio_path, waveform, sample_rate)

    del inputs, outputs, waveform
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return audio_path

# Step 4: Gradio页面创建
# 前端
def gradio_generate(scene_description):
    music_desc = generate_music_description(scene_description)
    if "Error" in music_desc:
        return music_desc, None
    audio_path = generate_music_from_text(music_desc)
    return music_desc, audio_path
# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 背景音乐生成器")
    scene_input = gr.Textbox(label="餐馆环境描述", placeholder="如：温馨的意大利餐厅，适合情侣约会")
    generate_button = gr.Button("生成音乐")
    music_output = gr.Textbox(label="生成的音乐描述")
    audio_output = gr.Audio(label="🎧 播放音乐", type="filepath")
    generate_button.click(gradio_generate, inputs=[scene_input], outputs=[music_output, audio_output])
demo.launch(share=True)
