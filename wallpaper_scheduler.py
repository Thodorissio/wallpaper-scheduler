import json
import ctypes
import glob
import logging
import os
import random

try:
    import astral
except ImportError:
    import subprocess

    subprocess.check_call(["pip", "install", "astral"])

from astral import LocationInfo
from astral.sun import sun

from datetime import datetime
from typing import List


class WallpaperScheduler:
    def __init__(self):

        self.logger = self._get_logger()

        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            self.logger.error("Configuration file not found.")
            raise
        except json.JSONDecodeError:
            self.logger.error("Error decoding JSON configuration file.")
            raise

        self.morning_wallpapers = self._get_wallpapers(config["morning_wallpaper_dir"])
        self.night_wallpapers = self._get_wallpapers(config["night_wallpaper_dir"])

        self.location = LocationInfo(
            config["city"],
            config["country"],
            config["timezone"],
            config["latitude"],
            config["longitude"],
        )

    def _get_logger(self):
        logger = logging.getLogger("WallpaperScheduler")
        logger.setLevel(logging.WARNING)

        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, "wallpaper_scheduler.log")

        handler = logging.FileHandler(log_file_path)
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _get_wallpapers(self, dir_path: str) -> List[str]:
        """returns a list of wallpapers from the given directory"""
        wallpapers = glob.glob(os.path.join(dir_path, "*.jpg")) + glob.glob(
            os.path.join(dir_path, "*.png")
        )
        if not wallpapers:
            self.logger.warning(f"No wallpapers found in {dir_path}.")
        return wallpapers

    def _get_random_wallpaper(self) -> str:
        """returns a random wallpaper based on the time of day"""
        current_hour = datetime.now().hour
        s = sun(
            self.location.observer, date=datetime.now(), tzinfo=self.location.timezone
        )
        sunrise = s["sunrise"].hour
        sunset = s["sunset"].hour

        if sunrise <= current_hour < sunset:
            wallpaper = random.choice(self.morning_wallpapers)
        else:
            wallpaper = random.choice(self.night_wallpapers)

        return wallpaper

    def set_wallpaper(self) -> None:
        """sets the wallpaper to a random one based on the time of day"""
        try:
            wallpaper = self._get_random_wallpaper()
            ctypes.windll.user32.SystemParametersInfoW(
                20,
                0,
                wallpaper,
                6,
            )
        except Exception as e:
            self.logger.error(f"Error setting wallpaper: {e}")


def main():
    scheduler = WallpaperScheduler()
    scheduler.set_wallpaper()


if __name__ == "__main__":
    main()
