# 仅首次运行
!pip install gradio
!pip install transformers torchaudio audiocraft accelerate bitsandbytes

#2 qwen-musicgen-meduim API 
import json
import random
import requests
import gradio as gr

# Qwen API 配置
QWEN_API_KEY = "sk-"  # 阿里云 Key
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# Hugging Face MusicGen API
HF_API_TOKEN = ""  # Hugging Face Token
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-medium"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# 使用配额设置
DAILY_LIMIT = 10
call_counter = {"count": 0}

# 读取数据 {"scene": ..., "music": ...}
scene_music_data = []
with open("musicgen_scene_music_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        scene_music_data.append(json.loads(line.strip()))

# ==========================few-shot===================================
# Step 1: few-shot messages构建
def build_few_shot_messages(k=2):
    examples = random.sample(scene_music_data, k)
    messages = [{"role": "system", "content": "You are a music cognition expert converting restaurant scene descriptions into music prompts suitable for MusicGen."}]
    for ex in examples:
        messages.append({"role": "user", "content": f"Scene: {ex['scene']}"})
        messages.append({"role": "assistant", "content": ex['music']})
    return messages

# Step 2: Qwen生成音乐描述
def generate_music_description(scene_desc):
    messages = build_few_shot_messages(k=2)
    messages.append({"role": "user", "content": f"Scene: {scene_desc}"})

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen2.5-14b-instruct",
        "input": {"messages": messages},
        "parameters": {"temperature": 0.5, "max_tokens": 150}
    }
    response = requests.post(QWEN_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result.get("output", {}).get("text", "No output")
    else:
        return f"Error: {response.text}"

# ==========================音乐生成===================================
# Step 3: 调用MusicGen API
def generate_music_from_text(music_desc):
    if call_counter["count"] >= DAILY_LIMIT:
        return "已达到今日调用上限，请明日再试或升级配额", None
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json={"inputs": music_desc})
    if response.status_code == 200:
        audio_path = "musicgen_output.wav"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        call_counter["count"] += 1
        return audio_path
    else:
        return f"API Error: {response.status_code} - {response.text}", None

# Gradio 接口
def gradio_generate(scene_description):
    music_desc = generate_music_description(scene_description)
    if "Error" in music_desc or "调用上限" in music_desc:
        return music_desc, None
    result = generate_music_from_text(music_desc)
    if isinstance(result, tuple):
        return result[0], None
    return music_desc, result

# Gradio 页面构建
with gr.Blocks() as demo:
    gr.Markdown("## 背景音乐生成器")
    scene_input = gr.Textbox(label="餐馆环境描述", placeholder="如：温馨的意大利餐厅，适合情侣约会")
    generate_button = gr.Button("生成音乐")
    music_output = gr.Textbox(label="Qwen 生成的音乐描述")
    audio_output = gr.Audio(label="🎧 播放音乐", type="filepath")
    generate_button.click(gradio_generate, inputs=[scene_input], outputs=[music_output, audio_output])
demo.launch(share=True)
