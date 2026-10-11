---
name: voice-separation-discipline
description: Enforces strict TTS voice separation across TokyoFlow video pipelines. Prohibits English and Chinese explainer TTS from pronouncing Japanese words, kana, or romaji, reserving Japanese pronunciation exclusively for Tokyo native TTS.
---

# Voice Separation Discipline

## 1. When to Use
Use this skill whenever:
- Generating audio scripts, `script.json`, or `production_spec.json`.
- Configuring Edge TTS voice synthesis for breakdown cues, teamwork cards, follow-along drills, or Shorts.
- Reviewing or modifying multi-language educational video pipelines.

## 2. Core Separation Matrix

| Channel | Explainer Voice | Native Voice | Explainer Role | Native Role |
| :--- | :--- | :--- | :--- | :--- |
| **English Edition** | `en-US-AndrewNeural` | `ja-JP-NanamiNeural` | English definitions, grammar structure, nuance (Zero Japanese/Romaji) | All Japanese kana, kanji, words, sentences, shadowing drills |
| **Chinese Edition** | `zh-CN-YunxiNeural` | `ja-JP-NanamiNeural` | Chinese definitions, parts of speech, grammar rules (Zero Japanese/Romaji) | All Japanese kana, kanji, words, sentences, shadowing drills |

## 3. Formatting Guidelines

### Breakdown / Teamwork Cues
```json
[
  {
    "speaker": "ja",
    "text": "AI",
    "card_idx": 0
  },
  {
    "speaker": "explainer",
    "text": "名词，人工智能。",
    "card_idx": 0
  },
  {
    "speaker": "ja",
    "text": "自由",
    "card_idx": 1
  },
  {
    "speaker": "explainer",
    "text": "形容动词，自由、随心所欲。",
    "card_idx": 1
  }
]
```

### Explainer Sentence Cue Template
- Chinese: `f"例句的意思是：{sentence_meaning_zh}。"` (Do NOT include romaji)
- English: `f"The sentence means: {sentence_meaning_en}."` (Do NOT include romaji)

### Shorts Hook & Pro-Tip Audio
- Chinese: `"智能体竟然无视开发者指令？今天带你掌握东京热议核心表达！"`
- English: `"Discover how artificial intelligence agents are causing a stir in Tokyo!"`
