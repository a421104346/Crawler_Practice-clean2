### 招聘信息抓取 + 职位需求分析（练习）

数据源：Remotive 公开接口（无需登录，返回 JSON：职位、地区、薪资、发布日期、技能标签等）。

### 1) 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 2) 抓取数据（生成 RAW JSON + CSV）

```powershell
python recruit_analysis\crawl_jobs.py
```

可选参数：
- `--category`：例如 `software-dev` / `data`（留空表示全部）
- `--search`：例如 `python` / `data analyst`
- `--out`：自定义输出目录

示例：

```powershell
python recruit_analysis\crawl_jobs.py --search python
```

### 3) 分析（城市 Top10 + 技能 Top10 + 图表）

最简单：不传参数，自动分析 `recruit_analysis/output` 下最新的 `jobs_*.csv`：

```powershell
python recruit_analysis\analyze_jobs.py
```

也可以把 `crawl_jobs.py` 输出的 `jobs_*.csv` 路径传给分析脚本：

```powershell
python recruit_analysis\analyze_jobs.py recruit_analysis\output\jobs_YYYYMMDD_HHMMSS.csv
```

或者直接传目录（会自动选目录里最新的 `jobs_*.csv`）：

```powershell
python recruit_analysis\analyze_jobs.py recruit_analysis\output
```

输出文件会生成在 CSV 同目录：
- `city_top10.csv`
- `skills_top10.csv`
- `city_top10.png`
- `skills_top10.png`


