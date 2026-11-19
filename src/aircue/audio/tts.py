"""Text-to-Speech (TTS) engine abstraction and offline test audio synthesizer.

Backends:
- 'beep': Generates valid synthetic WAV tone audio locally with no external network or TTS dependencies (ideal for tests and CI).
- 'gtts': Google Text-to-Speech (requires network).
- 'piper': Offline neural TTS engine (via local piper binary/voices).
"""
from __future__ import annotations

import math
import os
import struct
import wave
from pathlib import Path


def synthesize_beep_wav(output_path: str | Path, duration_s: float = 0.5, freq_hz: float = 440.0) -> str:
    """Generate a clean synthetic sine-wave WAV file locally without external libraries."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    sample_rate = 16000
    n_samples = int(sample_rate * duration_s)

    with wave.open(str(out), "w") as wav_file:
        # Channels=1 (mono), SampWidth=2 (16-bit), FrameRate=16000
        wav_file.setparams((1, 2, sample_rate, n_samples, "NONE", "not compressed"))
        frames = bytearray()
        for i in range(n_samples):
            # Apply subtle fade-in and fade-out envelope to avoid audio clicks
            envelope = min(1.0, i / (0.05 * sample_rate), (n_samples - i) / (0.05 * sample_rate))
            value = int(32767.0 * 0.5 * envelope * math.sin(2.0 * math.pi * freq_hz * (i / sample_rate)))
            frames.extend(struct.pack("<h", value))
        wav_file.writeframes(frames)

    return str(out)


def synthesize_gtts(text: str, language: str, output_path: str | Path) -> str:
    """Synthesize speech using gTTS."""
    from gtts import gTTS

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=text, lang="hi" if language == "hi" else "en")
    tts.save(str(out))
    return str(out)


def synthesize_speech(
    text: str,
    language: str,
    output_path: str | Path,
    backend: str = "beep",
    piper_voice: str | None = None,
) -> str:
    """Synthesize speech for given text into output_path using requested backend."""
    out = Path(output_path)
    if backend == "beep":
        return synthesize_beep_wav(out)
    elif backend == "gtts":
        try:
            return synthesize_gtts(text, language, out)
        except Exception:
            # Fallback to beep if offline or network fails
            return synthesize_beep_wav(out)
    elif backend == "piper":
        # Check if piper command line is available
        import shutil
        import subprocess

        piper_bin = shutil.which("piper")
        if piper_bin and piper_voice and os.path.exists(piper_voice):
            cmd = [piper_bin, "--model", piper_voice, "--output_file", str(out)]
            proc = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
            if proc.returncode == 0:
                return str(out)
        # Fallback to beep if piper binary or voice model is unavailable
        return synthesize_beep_wav(out)
    else:
        return synthesize_beep_wav(out)
