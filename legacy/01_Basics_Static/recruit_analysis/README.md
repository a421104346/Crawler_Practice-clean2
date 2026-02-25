### Job Data Scraping + Job Demand Analysis (Practice)

Data source: Remotive public API (no login required, returns JSON: job title, region, salary, publication date, skill tags, etc.).

### 1) Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2) Scrape Data (generate RAW JSON + CSV)

```powershell
python recruit_analysis\crawl_jobs.py
```

Optional parameters:
- `--category`: e.g. `software-dev` / `data` (leave empty for all)
- `--search`: e.g. `python` / `data analyst`
- `--out`: Custom output directory

Example:

```powershell
python recruit_analysis\crawl_jobs.py --search python
```

### 3) Analyze (City Top10 + Skill Top10 + Charts)

Simplest: no parameters, auto-analyzes the latest `jobs_*.csv` in `recruit_analysis/output`:

```powershell
python recruit_analysis\analyze_jobs.py
```

You can also pass the `jobs_*.csv` path output by `crawl_jobs.py` to the analysis script:

```powershell
python recruit_analysis\analyze_jobs.py recruit_analysis\output\jobs_YYYYMMDD_HHMMSS.csv
```

Or pass a directory directly (it will automatically pick the latest `jobs_*.csv` in the directory):

```powershell
python recruit_analysis\analyze_jobs.py recruit_analysis\output
```

Output files are generated in the same directory as the CSV:
- `city_top10.csv`
- `skills_top10.csv`
- `city_top10.png`
- `skills_top10.png`
