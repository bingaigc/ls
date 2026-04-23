# 论文优化与分析系统

## 项目结构

```text
project/
├── backend/
│   ├── app.py
│   ├── report.py
│   ├── pipeline/
│   ├── models/
│   └── utils/
├── frontend/
├── config.yaml
├── requirements.txt
└── README.md
```

## 功能

- 文本/论文改写（全量、红句、重度）
- embedding 双模式（local / OpenAI）
- 相似度计算与 heavy/medium/safe 分级
- 自动优化（heavy_ratio < 0.05 自动停止）
- 前端可视化（Diff、导航、评分、日志、版本）
- PDF/TXT/JSON 报告导出
- docx 上传与下载（保留段落）
- 多 docx 批量处理

## 后端运行

```bash
cd /path/to/project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

## 前端运行

```bash
cd /path/to/project/frontend
npm install
npm run dev
```

默认前端地址：`http://localhost:5173`
默认后端地址：`http://localhost:8000`

## 配置

编辑项目根目录 `config.yaml`：

- `embedding.mode`: `local` 或 `openai`
- `embedding.openai_api_key`: OpenAI Key（openai 模式必填）
- `optimization.stop_heavy_ratio`: 自动停止阈值
- `optimization.max_iterations`: 最大优化轮次

## 主要 API

- `POST /api/process` 上传 docx
- `POST /api/rewrite/all` 全量改写
- `POST /api/rewrite/red` 只改红句
- `POST /api/rewrite/heavy` 只改重度句
- `POST /api/optimize/step` 自动优化单步
- `POST /api/lock/all` 全锁/全解锁
- `POST /api/version/switch` 切换历史版本
- `GET /api/docx/download/{session_id}` 下载优化 docx
- `GET /api/report/pdf/{session_id}` 导出 PDF
- `GET /api/report/text/{session_id}` 导出文本报告
- `GET /api/report/json/{session_id}` 导出 JSON 报告
- `POST /api/batch/process` 批量处理 docx
