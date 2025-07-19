﻿# ðŸ—ï¸ India Startup Grant Oracle

**One source-of-truth for every non-dilutive rupee the Indian government offers startups (â‚¹10k â†’ â‚¹25 Cr)**

A comprehensive multi-agent system that discovers, tracks, and notifies about government grants, subsidies, and funding schemes for Indian startups.

## ðŸŽ¯ Features

- **Comprehensive Coverage**: Tracks grants from 40+ government agencies, PSUs, and incubators
- **Multi-Agent Discovery**: Uses Magentic-One AI agents for intelligent web scraping and data extraction
- **Real-time Notifications**: Slack and WhatsApp alerts for new grants and deadlines
- **REST API**: GraphQL-ready API for integration with other systems
- **Smart Filtering**: Filter by amount, sector, stage, state, and eligibility criteria
- **Deadline Tracking**: Automated reminders for upcoming application deadlines

## ðŸ—ï¸ Architecture

### Multi-Agent System (Magentic-One)
- **LeadPlanner**: Orchestrates daily discovery missions
- **GovPortalAgent**: Browses government websites and portals
- **PDFExtractorAgent**: Extracts information from PDF documents
- **SchemaCoder**: Validates and normalizes grant data
- **NotifierBot**: Sends alerts via Slack/WhatsApp

### Data Pipeline
- **Scrapy Spiders**: For static HTML table extraction
- **Playwright**: For JavaScript-heavy portals
- **PDF Processing**: Camelot + PyPDF2 for document parsing
- **Change Detection**: ETag + SHA-256 based incremental updates

### Storage & API
- **PostgreSQL**: Primary data store with JSONB support
- **Redis**: Caching layer for API responses
- **Flask API**: RESTful endpoints with CORS support
- **Hasura**: Auto-generated GraphQL API (optional)

## ðŸ“Š Data Schema

```json
{
  "id": "sisfs_seed_grant",
  "title": "Startup India Seed Fund Scheme",
  "bucket": "Early Stage",
  "instrument": ["grant", "convertible_debenture"],
  "min_ticket_lakh": 20,
  "max_ticket_lakh": 70,
  "typical_ticket_lakh": 60,
  "deadline_type": "rolling",
  "next_deadline_iso": "2025-12-31",
  "eligibility_flags": ["dpiit_recognised", "<2_years", "indian_promoters"],
  "sector_tags": ["tech_agnostic"],
  "state_scope": "national",
  "agency": "DPIIT, GoI",
  "source_urls": ["https://seedfund.startupindia.gov.in"],
  "confidence": 0.95,
  "status": "live"
}
```

## ðŸš€ Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key

### Installation

1. **Clone and Setup**
```bash
git clone https://github.com/Jayluci4/india-grants-oracle.git
cd india-grants-oracle
cp .env.example .env
# Edit .env with your API keys
```

2. **Start Services**
```bash
docker-compose up --build
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
playwright install --with-deps chromium
```

4. **Run the Application**
```bash
# Full mode (API + Scheduler)
python main.py --mode full

# API only
python main.py --mode api

# Discovery only (one-time)
python main.py --mode discovery
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...                    # Required for Magentic-One
DATABASE_URL=postgresql://grants:grants@db:5432/grantsdb
REDIS_URL=redis://redis:6379
SLACK_WEBHOOK=https://hooks.slack.com/services/...
TWILIO_SID=AC...                         # For WhatsApp notifications
TWILIO_TOKEN=...
```

## ðŸ“¡ API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check and database status
- `GET /grants` - List grants with filtering options
- `GET /grants/<id>` - Get specific grant details
- `GET /stats` - Database statistics and metrics
- `GET /search?q=<query>` - Text search in grants

### Query Parameters for `/grants`
- `bucket` - Filter by stage (Ideation, Early Stage, Growth, etc.)
- `status` - Filter by status (live, expired, draft)
- `min_amount` - Minimum funding amount in lakhs
- `max_amount` - Maximum funding amount in lakhs
- `agency` - Filter by agency name
- `sector` - Filter by sector tags
- `limit` - Number of results (default: 50)

### Example API Calls

```bash
# Get all live grants
curl "http://localhost:5000/grants?status=live"

# Get early stage grants above â‚¹50 lakh
curl "http://localhost:5000/grants?bucket=Early%20Stage&min_amount=50"

# Search for biotechnology grants
curl "http://localhost:5000/search?q=biotechnology"

# Get database statistics
curl "http://localhost:5000/stats"
```

## ðŸ•·ï¸ Data Sources

### Central Government
- **DPIIT**: Startup India Seed Fund, various schemes
- **BIRAC**: Biotechnology grants and fellowships
- **TDB**: Technology Development Board funding
- **MeitY**: IT and electronics sector schemes
- **DSIR**: Scientific research grants
- **IN-SPACe**: Space technology funding

### State Governments
- Karnataka, Kerala, Tamil Nadu, Telangana
- Odisha, Bihar, Goa, Uttar Pradesh
- Madhya Pradesh, Jammu & Kashmir

### PSU & Corporate
- GAIL Pankh, BPCL Ankur, HPCL Udgam
- Oil India SNEH, NTPC, BHEL
- SIDBI, various CSR funds

### Incubators & PPP
- T-Hub, KIIT-TBI, Villgro
- C-CAMP, TIFAC SRIJAN

## ðŸ”” Notifications

### Slack Integration
- New grant alerts in `#grants-feed`
- Daily discovery summaries
- Deadline reminders
- Error alerts in `#alerts`

### WhatsApp Integration
- Broadcast lists for founders
- Instant grant notifications
- Deep links to grant details

### Email Digest
- Weekly summary reports
- Personalized recommendations
- Deadline calendars

## ðŸ› ï¸ Development

### Project Structure
```
india-grants-oracle/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ agents/           # Magentic-One orchestrator
â”‚   â”œâ”€â”€ scrapers/         # Scrapy spiders
â”‚   â”œâ”€â”€ database/         # PostgreSQL models
â”‚   â”œâ”€â”€ api/             # Flask API
â”‚   â””â”€â”€ notifications/   # Slack/WhatsApp
â”œâ”€â”€ data/                # Downloaded files
â”œâ”€â”€ logs/                # Application logs
```

## ðŸ¤ Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ðŸ“„ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ðŸ™ Acknowledgments

- Built with [Magentic-One](https://github.com/magentic-ai/magentic) for AI orchestration
- Uses [Scrapy](https://scrapy.org/) for web scraping
- Powered by [Flask](https://flask.palletsprojects.com/) for the API
- Database powered by [PostgreSQL](https://www.postgresql.org/)

## ðŸ“ž Support

For support, email support@indiagrantsoracle.com or join our Slack channel.

---

**Made with â¤ï¸ for Indian Startups**


