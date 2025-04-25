# TradeSentry Business Data Analyzer

The TradeSentry Business Data Analyzer is a plug-and-play solution that allows users to upload business data files (CSV, Excel, JSON) directly through a website interface and receive automatic insights, trend analysis, and downloadable reports.

## 🚀 What It Does

- Users visit a website (built on Wix or any platform)
- Upload business data files in common formats
- The bot processes the data and:
  - Detects trends
  - Highlights KPIs
  - Generates charts and summaries
  - Creates downloadable PDF reports

All results are delivered **automatically and instantly** — no technical setup required.

## 🔒 Secure & Client-Facing

- Runs on a hosted server (Render)
- Integrated into a secured, members-only area on the website
- Built to deliver insights without exposing raw data or source code

## 🧠 Who It's For

- Business owners
- Freelancers
- Agencies
- E-commerce shops
- SaaS startups

No technical knowledge required. Just upload your file — get the results.

## 🔧 Developer Info (for internal use)

This repository contains:
- Core logic for file handling and data analysis
- Auto-report generation (charts + PDFs)
- API endpoint for file upload

### Environment Variables (`.env`)

You may copy `.env.example` and rename it to `.env` if running locally.

Example:
```env
PORT=8000
SECRET_KEY=your_secret_key_here
