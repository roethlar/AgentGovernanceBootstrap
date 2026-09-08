"""Keep fixture Git subprocesses independent of user/system configuration."""
import os


def isolate_git():
    for key in list(os.environ):
        if key.startswith("GIT_CONFIG_") or key in {
            "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        }:
            os.environ.pop(key)
    os.environ.update(
        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_SYSTEM=os.devnull, GIT_TEMPLATE_DIR="",
        GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.hooksPath",
        GIT_CONFIG_VALUE_0=os.devnull,
    )
