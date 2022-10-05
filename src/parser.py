from subprocess import PIPE, Popen
from time import perf_counter
from typing import Any, List

from loguru import logger

from src.downloader import temp_folder


class Parser(object):
    def __init__(self, patcher, env):
        self._PATCHES = []
        self._EXCLUDED = []
        self.patcher = patcher
        self.keystore_name = env.str("KEYSTORE_FILE_NAME", "revanced.keystore")
        self.build_extended = env.bool("BUILD_EXTENDED", False)
        self.extended_apps = ["youtube", "youtube_music"]
        self.keystore_name = env.str("KEYSTORE_FILE_NAME", "revanced.keystore")
        self.normal_cli_jar = "revanced-cli.jar"
        self.normal_patches_jar = "revanced-patches.jar"
        self.normal_integrations_apk = "revanced-integrations.apk"
        self.cli_jar = (
            f"inotia00-{self.normal_cli_jar}"
            if self.build_extended
            else self.normal_cli_jar
        )
        self.patches_jar = (
            f"inotia00-{self.normal_patches_jar}"
            if self.build_extended
            else self.normal_patches_jar
        )
        self.integrations_apk = (
            f"inotia00-{self.normal_integrations_apk}"
            if self.build_extended
            else self.normal_integrations_apk
        )

    def include(self, name: str) -> None:
        self._PATCHES.extend(["-i", name])

    def exclude(self, name: str) -> None:
        self._PATCHES.extend(["-e", name])
        self._EXCLUDED.append(name)

    def get_excluded_patches(self) -> List[Any]:
        return self._EXCLUDED

    def patch_app(self, app: str, version: str, is_experimental: bool = False) -> None:
        logger.debug(f"Sending request to revanced cli for building {app} revanced")
        cli = self.normal_cli_jar
        patches = self.normal_patches_jar
        integrations = self.normal_integrations_apk
        if self.build_extended and app in self.extended_apps:
            cli = self.cli_jar
            patches = self.patches_jar
            integrations = self.integrations_apk
        args = [
            "-jar",
            cli,
            "-a",
            app + ".apk",
            "-b",
            patches,
            "-m",
            integrations,
            "-o",
            f"Re-{app}-{version}-output.apk",
            "--keystore",
            self.keystore_name,
        ]
        if is_experimental:
            logger.debug("Using experimental features")
            args.append("--experimental")
        args[1::2] = map(lambda i: temp_folder.joinpath(i), args[1::2])

        if self._PATCHES:
            args.extend(self._PATCHES)

        start = perf_counter()
        process = Popen(["java", *args], stdout=PIPE)
        for line in process.stdout:
            logger.debug(line.decode(), flush=True, end="")
        process.wait()
        logger.info(
            f"Patching completed for app {app} in {perf_counter() - start:.2f} seconds."
        )
