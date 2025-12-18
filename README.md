# 🏓 tt_stats_app
Table Tennis analytics dashboard using Polars and Streamlit.
Data scraped from WTT and ITTF websites.
Refactored from earlier (obsolete) project at:
https://github.com/mannegarn/table_tennis_stats


## How to Run
1. Install [uv](https://docs.astral.sh/uv/)
2. Run `uv sync` to install dependencies
3. Run `uv run streamlit run app.py`



# Non-exhaustive list of resources used 

### Data Sources
- [WTT Website - via reverse engineering the internal API](https://www.worldtabletennis.com/)
- [ITTF Database (older http-based site containing additional data)](https://results.ittf.link/)

### Extra reading and resources

- [Data Engineering Cookbook](https://github.com/andkret/Cookbook) - Patterns for raw/processed data separation.
- [Polars Documentation](https://docs.pola.rs/) - High-performance data processing logic.
- [Streamlit Design Guide](https://docs.streamlit.io/library/get-started) - Best practices for dashboard UX.
