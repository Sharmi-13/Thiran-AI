# Thiran AI

English mock interview coach for Tamil-medium, first-generation students.
Interview in English, feedback in Tamil.

Built for the AWS Builder Center "Strands SDK: Workshop to Ship" hackathon
(Education focus, Build for Madurai & Tamil).

## Problem
Many talented students freeze in English interviews. Paid coaching is costly,
and most practice tools give feedback only in English.

## What it does
1. Choose a role (Software/IT, Data Analyst, Customer Support, Business/Marketing)
2. Get an English interview question
3. Answer in English, Tamil or Tanglish
4. Get scores (content, structure, English, overall)
5. Get short Tamil tips on improving that answer
6. See your answer rewritten as natural spoken interview English
7. Track your progress across attempts

## Built with Strands Agents
- Interviewer agent: a Strands Agent with an @tool that picks the next unused
  question from a vetted question bank (saves free-tier requests)
- Reviewer agent: a Strands Agent using structured output (Pydantic) for the
  scores, Tamil tips and English rewrite
- Model: Gemini via Strands GeminiModel; a custom Strands Model (mock) is used
  for offline testing only
- UI: Streamlit

## Setup
1. Python 3.10 or newer
2. pip install -r requirements.txt
3. Copy .env.example to .env, then set AI_PROVIDER=gemini and add your
   GEMINI_API_KEY (never commit .env)
4. streamlit run app/app.py

## Results and limits (honest)
- One real Gemini example run scored 5/5/8/5 on a sample answer.
- No structured study with students yet.
- The free Gemini tier allows about 20 requests per day, which limited testing.
- Tamil output should be reviewed by a fluent reader before real use.
- Runs on Gemini. The model is chosen in ai/factory.py.

## Demo
https://youtu.be/hnO-pyWeifw

## License
MIT

