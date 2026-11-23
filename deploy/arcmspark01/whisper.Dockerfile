# vLLM pro přepis řeči (Whisper) na arcmspark01
# Autor: Hynek Cihlář (Bc. Hynek Cihlář)
#
# Image vllm/vllm-openai:qwen38 neobsahuje knihovny pro čtení zvuku, takže
# /v1/audio/transcriptions vrací „Invalid or unsupported audio file“.
# Doplníme je; verze numpy, numba, llvmlite a torch zůstanou zamčené, aby
# instalace nerozbila vLLM.

ARG VLLM_IMAGE=vllm/vllm-openai:qwen38
FROM ${VLLM_IMAGE}

RUN python3 -m pip freeze | grep -iE '^(numpy|numba|llvmlite|torch|torchaudio|scipy)==' > /tmp/zamceno.txt \
 && cat /tmp/zamceno.txt \
 && python3 -m pip install --no-cache-dir --break-system-packages -c /tmp/zamceno.txt \
        "librosa>=0.10" "soundfile>=0.12" "av" "audioread" \
 && python3 -c "import librosa, soundfile, av, numpy, torch; print('ZVUK_OK librosa', librosa.__version__, 'soundfile', soundfile.__version__, 'numpy', numpy.__version__, 'torch', torch.__version__)" \
 && rm -f /tmp/zamceno.txt
