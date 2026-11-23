#!/usr/bin/env bash
# Stav stahování a startu modelů Open Notebooku na arcmspark01.
# Autor: Hynek Cihlář (Bc. Hynek Cihlář)
#
# Použití (jako root, aby fungoval docker):
#   sudo watch -n 10 /home/spark/open-notebook/deploy/arcmspark01/stav-stahovani.sh
# Ukončení: Ctrl+C

HF="${HF_CACHE_DIR:-/home/spark/.cache/huggingface}"
QWEN="$HF/hub/models--Qwen--Qwen3.8-27B-FP8"
BGE="$HF/hub/models--BAAI--bge-m3"
WSP="$HF/hub/models--openai--whisper-large-v3"

echo "Čas: $(date '+%d.%m.%Y %H:%M:%S')"
echo
echo "=== Stažené váhy (cíl: Qwen ~31G, bge-m3 ~2,3G, Whisper ~3G) ==="
du -sh "$QWEN" "$BGE" "$WSP" 2>/dev/null

mapfile -t INC < <(find "$QWEN/blobs" "$BGE/blobs" "$WSP/blobs" -name '*.incomplete' 2>/dev/null)
if [ "${#INC[@]}" -gt 0 ]; then
    echo "Rozpracované soubory: ${#INC[@]}, dohromady $(du -ch "${INC[@]}" | tail -1 | cut -f1)"
else
    echo "Rozpracované soubory: 0"
fi
echo "Mezipaměť xet: $(du -sh "$HF/xet" 2>/dev/null | cut -f1)"

echo
echo "=== Kontejnery (cíl: running healthy restartů:0) ==="
docker inspect --format '{{.Name}} {{.State.Status}} {{.State.Health.Status}} restartů:{{.RestartCount}}' \
    on-vllm-qwen on-vllm-embed on-vllm-whisper 2>&1

echo
echo "=== Paměť (GB) ==="
free -g | head -2

echo
echo "=== Poslední řádky logu Qwenu ==="
docker logs --tail 4 on-vllm-qwen 2>&1 | cut -c1-170
