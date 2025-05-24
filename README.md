# UndergraduateEND
Undergraduate Graduation Project in ECNU SEI

本项目探索通过语言模型与音频生成模型的联动，实现餐馆特定场景下的背景音乐自动生成。项目内容涵盖数据抓取、清洗处理、prompt构建、实验流程、模型部署等多个模块。

实验环境： 本研究在Google Colab 云端平台进行实验，其中免费版GPU在亚太地区的配置为：
机器类型：n1-standard-4（4 个vCPU和15 GB内存） 
加速器：1个NVIDIA_TESLA_T4加速器 
数据磁盘：100 GB pd-standard

---

## 文件结构与说明

### 一、代码文件（位于 `代码/` 文件夹内）

| 文件名 | 功能说明 |
|--------|-----------|
| `getdata.py` | 用于抓取 Spotify 上的音乐数据，包括歌手、描述和类型（genre）等信息。 |
| `qwen_MusicgenSmall_gradio_1.py` | 通过部署 MusicGen-small 与 Qwen 模型生成音乐。 |
| `qwen_MusicgenMedium_gradio_2.py` | Qwen + 使用 Hugging Face API 远程调用 MusicGen-medium 模型，生成音乐片段。 |
| `experiments.ipynb` | 实验流程，包括prompt构建、模型调用、评估等步骤。 |

### 二、数据集文件（位于 `数据集/` 文件夹内）

| 文件名 | 数据说明 |
|--------|----------|
| `data1_有genre.csv` / `data2_480+_有genre去除无genre.csv` | 初始抓取的数据，包含基础元数据与 genre 标签。 |
| `data2_筛选.csv` | 筛选出缺失 genre 和描述的样本，为后续处理做准备。 |
| `data3_加入音乐描述和场景描述.xlsx` | 在已有数据中补充音乐描述与场景信息。 |
| `data3_z_add.csv` | 增加中文关键词，丰富文本语义。 |
| `data4_ending_please_去除冗余信息_清洗.csv` | 清洗后可用于生成 prompt 的最终数据版本。 |
| `data4_ending_please.jsonl` | 包含 205 条记录的主数据集（带音乐描述与场景）。 |
| `data4_ending_please_train.jsonl` / `data4_ending_please_test.jsonl` | 训练集与测试集划分。 |
| `sampled_85.jsonl` | 包含 85 条记录的数据集 |
| `sampled_train.jsonl` / `sampled_test.jsonl` | 训练集与测试集划分。 |

- `clean.py`：清洗数据
---

### 三、实验数据与记录

- `实验数据.docx`：记录实验结果
---
