# Multi-Agent Insurance Claim Intake System 🤖📄

Automating insurance document processing using AI agents

---

## 🚀 Overview

This is a multi-agent system designed to simulate how AI Teammates can automate end-to-end insurance claim intake — from unstructured PDF uploads to structured, validated outputs.

This system is inspired by real-world document workflows in regulated industries like insurance and healthcare.

---

## 🧠 Agent Architecture

| Agent             | Responsibility                                |
|------------------|------------------------------------------------|
| 📨 Intake Agent    | OCR + LLM extract fields from PDFs            |
| 🔍 Validation Agent| Ensures correctness, format, and logic        |
| 🧾 Filler Agent    | Saves into form, JSON or DB                   |

---

## 🛠️ Tech Stack

- **Backend**: Flask
- **OCR**: PyMuPDF, pytesseract
- **LLMs**: Groq (LLama)
- **Agents**: CrewAI
- **Output**: JSON
- **Frontend** : React
