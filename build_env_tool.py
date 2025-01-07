from logger import logger
import configparser
import os
import argparse
from datetime import datetime

ci_config = configparser.ConfigParser()
build_config = configparser.ConfigParser()


def _set_env_if_not_exist(key: str, value: str):
    if key in os.environ:
        logger.info(f"env set by ci: {key}={value}")
    else:
        os.environ[key] = value
        logger.info(f"env set by local: {key}={value}")


def _set_app_env(config):
    for key, value in config["App"].items():
        _set_env_if_not_exist(key.upper(), value)
    for key, value in config["App.KeyStore"].items():
        _set_env_if_not_exist(key.upper(), value)


def _set_bundle_env(config):
    for key, value in config["Bundle"].items():
        _set_env_if_not_exist(key.upper(), value)


def set_ci_env(path: str):
    if not os.path.exists(path):
        logger.error(f"Config file not found: {path}")
        return
    ci_config.read(path)
    for key, value in ci_config[os.name].items():
        _set_env_if_not_exist(key.upper(), value)
    for key, value in ci_config["ci"].items():
        _set_env_if_not_exist(key.upper(), value)


def set_build_env(config_path: str):
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return
    build_config.read(config_path)
    _set_app_env(build_config)
    _set_bundle_env(build_config)


def set_package_env(package_name: str):
    os.environ['PACKAGE_NAME'] = package_name
    if not build_config.has_section(package_name):
        logger.error(f"Package section not found: {package_name}")
        return
    for key, value in build_config[package_name].items():
        _set_env_if_not_exist(key.upper(), value)


def load_config_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ci", "--ci_config", type=str)
    parser.add_argument("-build", "--build_config", type=str)
    args = parser.parse_args()
    set_ci_env(args.ci_config)
    set_build_env(args.build_config)


def check_environ(env_vars):
    """检查需要用到环境变量有没有被正确设置

    Args:
        env_vars (string[]): 环境变量名数组

    Returns:
        bool: 都正确设置返回true否则返回false
    """
    for var in env_vars:
        if var not in os.environ:
            logger.error(f"Error: Environment variable {var} is not set.")
            return False
    return True


if __name__ == "__main__":
    set_ci_env("cfg/ci_env.ini")
    set_build_env("cfg/build_env.ini")
