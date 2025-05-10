#!/usr/bin/env bash
###############################################################################
# run_all_jobs.sh —— 一鍵啟動所有 PySpark Streaming Job（正確依賴順序）
###############################################################################
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
JOB_SUBMIT="$SCRIPT_DIR/job_submit.sh"

log() { echo -e "\033[1;32m[$(date '+%H:%M:%S')] $*\033[0m"; }

# ---------------------------------------------------------------------------#
log ">>> 啟動 Strategy A B C D ..."
"$JOB_SUBMIT" strategy_job.py --strategies A B C D &  PID_STRATEGY=$!

# ---------------------------------------------------------------------------#
log ">>> 啟動 C & D 合併 Job (merge_c_d.py) ..."
"$JOB_SUBMIT" merge_c_d.py &                 PID_MERGE=$!

# ---------------------------------------------------------------------------#
log "所有 Job 已提交！Driver PID："
printf "  STRATEGY=%s  MERGE=%s\n" \
       "$PID_STRATEGY" "$PID_MERGE"

# 如僅需確認提交成功即可結束腳本，可註解下行 wait
wait "$PID_STRATEGY" "$PID_MERGE" || true

log "✅ 全部 Spark Streaming Job 啟動完成！"