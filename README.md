# SARCathon-2024---AI-Hackathon
Submission by Team Chanakya, Team Leader: Vaibhav Kumar, Team Members: Vaibhav Itauriya, Kalpak Agrawal and  Sanket Bansal

# FAQ Search Web Application

## Overview
This Flask-based web app allows users to search through an FAQ database using fuzzy matching and semantic search with Sentence Transformers and FAISS. It provides query suggestions, search history, and feedback collection.

## Features
- Fuzzy matching and semantic search for relevant FAQs.
- Real-time suggestions while typing queries.
- Search history to track recent queries.
- Feedback collection for answer quality.

## Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/your-repo/faq-search.git
   cd faq-search
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add FAQ data in `faqs.json`.

## Usage
Run the Flask server:
```bash
python app_v2.py
```
Access the app at `http://localhost:5000`.

## File Structure
- `app_v2.py`: Flask app logic.
- `faq_search_v2.py`: Search engine implementation.
- `index_v2.html`, `styles_v2.css`, `script_v2.js`: Frontend components.

## License
Licensed under the MIT License.