"""Cross-platform queued audio player."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class NullPlayer:
    """Mock player for testing and headless environments."""

    def __init__(self) -> None:
        self.played_clips: list[str] = []

    def play(self, audio_path: str | Path) -> bool:
        self.played_clips.append(str(audio_path))
        return True

    def stop(self) -> None:
        pass


class AudioPlayer:
    """Non-blocking audio player respecting mute and system audio tools."""

    def __init__(self, muted: bool = False, gain: float = 1.0) -> None:
        self.muted = muted
        self.gain = gain
        self._current_process: Optional[subprocess.Popen] = None

    def play(self, audio_path: str | Path) -> bool:
        """Play the specified audio clip if not muted."""
        if self.muted:
            return False

        path_str = str(audio_path)
        if not os.path.exists(path_str):
            return False

        # Terminate any actively playing audio
        self.stop()

        try:
            if sys.platform.startswith("linux"):
                # Use aplay for wav or paplay/ffplay/mpv if installed
                if path_str.endswith(".wav") and shutil.which("aplay"):
                    self._current_process = subprocess.Popen(["aplay", "-q", path_str])
                elif shutil.which("paplay"):
                    self._current_process = subprocess.Popen(["paplay", path_str])
                elif shutil.which("ffplay"):
                    self._current_process = subprocess.Popen(
                        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path_str]
                    )
            elif sys.platform == "darwin":
                if shutil.which("afplay"):
                    self._current_process = subprocess.Popen(["afplay", path_str])
            elif sys.platform == "win32":
                import winsound
                if path_str.endswith(".wav"):
                    winsound.PlaySound(path_str, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception:
            return False

    def stop(self) -> None:
        """Interrupt and stop current audio playback."""
        if self._current_process is not None:
            try:
                self._current_process.terminate()
            except Exception:
                pass
            self._current_process = None
