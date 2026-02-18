# Cafe Management with AI

A Streamlit-based cafe management system with menu, orders, inventory, sales analytics, and an AI assistant powered by LangChain. The AI assistant is designed to integrate with the GitHub Copilot API (configurable via environment variables).

## Features
- Menu management (add, edit, remove items)
- Order creation with totals
- Daily sales summary + top items
- Inventory tracker with low-stock alerts
- AI assistant for menu questions, upsell suggestions, and inventory guidance

## Quick Start

1. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

4. **Run the app**

```bash
streamlit run app.py
```

## GitHub Copilot API Configuration

Set the following environment variables:

- `COPILOT_API_URL` - API endpoint
- `COPILOT_API_TOKEN` - access token
- `COPILOT_API_MODEL` - optional model name

If these variables are missing, the assistant uses a safe local fallback response.

## Data Storage

Data is stored locally in the `data/` directory:
- `menu.json`
- `orders.json`
- `inventory.json`

> This project uses local JSON storage for portability. You can upgrade it to a database later if needed.

## Project Structure

```
.
├── app.py
├── services
│   ├── ai_assistant.py
│   ├── analytics.py
│   └── storage.py
├── data
│   ├── inventory.json
│   ├── menu.json
│   └── orders.json
├── requirements.txt
└── .env.example
```