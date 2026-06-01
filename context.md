# Project Context: AI-Powered Restaurant Recommendation System (Zomato Use Case)

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system suggests restaurants from a real-world dataset by combining **structured filtering** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations with explanations.

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM for personalized, natural-language recommendations
4. Presents clear, useful results to the user

## Data Source

| Item | Detail |
|------|--------|
| **Dataset** | Zomato restaurant data on Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related attributes |

### Data Ingestion

- Load and preprocess the dataset from Hugging Face
- Extract fields needed for filtering and display (name, location, cuisine, cost, rating, etc.)

## User Input

Collect preferences including:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional** | family-friendly, quick service, etc. |

## System Architecture (Workflow)

```
User Input → Filter/Prepare Data → LLM Prompt → Rank & Explain → Display Results
```

### 1. Integration Layer

- Filter restaurant data based on user input
- Prepare structured candidate results for the LLM
- Design prompts so the LLM can **reason** and **rank** options

### 2. Recommendation Engine (LLM)

The LLM should:

- **Rank** restaurants against user preferences
- **Explain** why each recommendation fits
- **Optionally** summarize the overall choice set

### 3. Output Display

Present top recommendations in a user-friendly format. Each item should include:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation (why it was recommended)

## Success Criteria (Implicit)

- End-to-end flow: ingest data → collect preferences → filter → LLM → display
- Recommendations are grounded in dataset fields, not purely hallucinated
- Explanations are readable and tied to user-stated preferences
- UI or presentation layer makes results easy to scan and compare

## Out of Scope (Not Specified in Problem Statement)

- Specific tech stack (framework, LLM provider, hosting)
- Authentication, payments, or live Zomato API integration
- Exact number of recommendations to return

## Reference

Full problem statement: `Docs/problemstatement.txt`
