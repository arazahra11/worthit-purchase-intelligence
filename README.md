# WorthIt — Personal Purchase Intelligence

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Backend-3ECF8E?logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)
[![Live Demo](https://img.shields.io/badge/Live-Demo-705CFF)](https://worthit-purchase-intelligence.streamlit.app)

**WorthIt** is a personal purchase intelligence app that helps users answer a simple question:

> **Was my money actually well spent?**

Instead of acting as a basic expense tracker, WorthIt evaluates purchases using satisfaction, repurchase intention, usage behavior, longevity, and value-for-money signals.

It is designed as a multi-user web application with private user data, interactive purchase tracking, usage logging, and behavioral analytics.

## Live Demo

**App:** https://worthit-purchase-intelligence.streamlit.app

**Repository:** https://github.com/arazahra11/worthit-purchase-intelligence

## Features

- User registration, login, and logout
- Multi-user data isolation with Supabase Row Level Security
- Add, edit, finish, reopen, and delete purchases
- Support for:
  - Consumable purchases
  - Durable purchases
  - One-time purchases and experiences
- Usage Calendar for logging actual product usage by date
- Direct month and year navigation
- WorthIt scoring engine
- Evidence Confidence indicator
- Search and filtering for purchase history
- Analytics dashboard with:
  - Highest-value purchase
  - Lowest-value purchase
  - Average WorthIt score
  - Rebuy rate
  - Strongest category
  - Weakest category
  - Top 5 purchases
  - Bottom 5 / regret-watch purchases
  - Usage evidence
- Responsive, colorful, accessibility-aware UI
- Streamlit Cloud deployment
- Supabase backend

## Why WorthIt?

Most finance apps answer:

> **How much did I spend?**

WorthIt focuses on a different question:

> **Did the purchase create enough value to justify the money I spent?**

A product can be expensive but still be highly worth it if it is consistently used and loved.

A cheaper product can still be poor value if it is rarely used, disliked, or never repurchased.

This makes WorthIt closer to a **personal decision intelligence tool** than a traditional budgeting app.

## Purchase Types

### Consumable

Examples:

- Skincare
- Makeup
- Shampoo
- Bodycare
- Fragrance

Evaluated using:

- Satisfaction
- Repurchase intention
- Usage frequency

### Durable

Examples:

- Shoes
- Chargers
- Electronics
- Hair dryers

Evaluated using:

- Satisfaction
- Repurchase intention
- Usage frequency
- Longevity

### One-time

Examples:

- Restaurant meals
- Food orders
- Treatments
- Tickets
- Experiences

Evaluated using:

- Satisfaction
- Repurchase intention
- Value for money

One-time purchases are intentionally excluded from the Usage Calendar.

## WorthIt Score

WorthIt uses a transparent heuristic scoring model rather than a black-box model.

### Satisfaction normalization

| Rating | Normalized value |
| --- | ---: |
| 1 | 0.00 |
| 2 | 0.25 |
| 3 | 0.50 |
| 4 | 0.75 |
| 5 | 1.00 |

### Repurchase normalization

| Response | Value |
| --- | ---: |
| Yes | 1.00 |
| Maybe | 0.50 |
| No | 0.00 |

### Usage normalization

| Usage frequency | Value |
| --- | ---: |
| Almost daily | 1.00 |
| Frequent | 0.85 |
| Frequent / rotating | 0.70 |
| Weekly | 0.50 |
| Occasional | 0.25 |
| Rare | 0.10 |

### Consumable score

```text
WorthIt Score =
100 × (
    0.40 × Satisfaction
  + 0.35 × Repurchase
  + 0.25 × Usage
)
```

If a component is unavailable, the remaining weights are dynamically normalized.

### Durable score

```text
Longevity = min(ownership_days / 365, 1)

WorthIt Score =
100 × (
    0.35 × Satisfaction
  + 0.30 × Repurchase
  + 0.25 × Usage
  + 0.10 × Longevity
)
```

### One-time score

```text
WorthIt Score =
100 × (
    0.40 × Satisfaction
  + 0.35 × Repurchase
  + 0.25 × Value for Money
)
```

### Score labels

| Score | Label |
| --- | --- |
| 85–100 | Highly Worth It |
| 70–84.9 | Worth It |
| 55–69.9 | Mixed Value |
| 40–54.9 | Questionable |
| < 40 | Not Worth It |

## Evidence Confidence

WorthIt separates the **score itself** from the **quality of the evidence behind the score**.

Evidence Confidence is not a probability that the score is correct.

It represents how complete and reliable the supporting purchase data is.

Examples of stronger evidence include:

- Verified satisfaction
- Verified repurchase intention
- Actual purchase dates
- Real historical usage information

## Usage Calendar

Usage is logged only through the Usage Calendar.

The user:

1. Selects a product
2. Selects a year
3. Selects a month
4. Clicks a date to mark it as **Used**
5. Clicks the same date again to undo the log

The system prevents:

- Logging usage before the purchase date
- Logging usage in the future
- Duplicate usage logs for the same product on the same calendar day

## Architecture

```text
User
  │
  ▼
Streamlit UI
  │
  ├── Authentication
  ├── Purchase Management
  ├── Usage Calendar
  ├── Analytics
  │
  ▼
Python Application Logic
  │
  ├── WorthIt Scoring Engine
  ├── Evidence Confidence
  └── Validation
  │
  ▼
Supabase
  │
  ├── Auth
  ├── PostgreSQL
  └── Row Level Security
```

## Database Structure

### `purchases`

Stores:

- User ID
- Product name
- Purchase type
- Category
- Price
- Purchase date
- Date precision
- Status
- Usage estimate
- Satisfaction
- Repurchase intention
- Value for money
- Notes

### `usage_logs`

Stores:

- User ID
- Purchase ID
- Usage date

Each product can only be logged once per calendar day.

## Privacy & Security

WorthIt is designed as a multi-user application.

Each purchase and usage log is associated with a Supabase Auth user.

Supabase Row Level Security ensures users can only access their own data.

The public GitHub repository does **not** contain:

- `.env`
- Supabase credentials
- Private seed data
- Personal purchase import scripts

Production configuration is stored using Streamlit Secrets.

## Tech Stack

### Frontend
- Streamlit
- Custom HTML
- Custom CSS

### Backend
- Python
- Supabase Python client

### Database & Authentication
- Supabase Auth
- PostgreSQL
- Row Level Security

### Testing
- pytest

### Deployment
- GitHub
- Streamlit Community Cloud

## Project Structure

```text
worthit-purchase-intelligence/
│
├── app.py
├── database.py
├── scoring.py
├── test_scoring.py
├── requirements.txt
└── .gitignore
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/arazahra11/worthit-purchase-intelligence.git
cd worthit-purchase-intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_publishable_key
```

Run the application:

```bash
python -m streamlit run app.py
```

## Testing

Run:

```bash
pytest -v
```

The scoring engine includes tests for:

- Satisfaction normalization
- Repurchase normalization
- Usage normalization
- Dynamic weight normalization
- Durable longevity
- Invalid values
- Future purchase dates
- Score labels
- Evidence Confidence

## Design Principles

WorthIt was designed around:

- **Usability** — obvious navigation and clear next actions
- **Responsive layout** — usable on desktop, tablet, and smaller screens
- **Consistency** — shared visual system for colors, cards, typography, and spacing
- **Accessibility** — contrast, focus states, and reduced-motion support
- **Feedback** — toast notifications, validation messages, and hover interactions
- **Readability** — clear hierarchy and comfortable line spacing
- **Brand identity** — colorful category-aware visuals rather than a generic dashboard template

## Current Dataset

The development version was tested with a personal historical purchase dataset containing 40 purchases across categories such as:

- Makeup
- Skincare
- Haircare
- Bodycare
- Fragrance
- Electronics
- Shoes

The personal source dataset is intentionally excluded from this public repository.

## Future Improvements

- Cost-per-use analytics
- Observed usage frequency from calendar logs
- Spending composition by category
- Category trend visualization
- Regret-risk prediction
- Personalized purchase recommendations
- CSV import
- Exportable reports
- More advanced behavioral insights

## Author

**Halimah Zahra**

Built as a Data / Analytics / Product portfolio project combining behavioral data, scoring logic, database design, authentication, analytics, and product-oriented UI design.
