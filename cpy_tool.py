import shutil
import os
from pathlib import Path
from logger import logger

def copy_file_to(from_path, to_path):
    """
    将文件从 from_path 拷贝到 to_path。

    参数:
    from_path (str): 源文件的路径。
    to_path (str): 目标文件的路径或目标目录。

    返回:
    str: 拷贝后的目标文件路径。
    """
    try:
        # 检查源文件是否存在
        if not os.path.exists(from_path):
            logger.error(f"源文件 {from_path} 不存在")

        # 如果 to_path 是目录，则将文件拷贝到该目录中
        if os.path.isdir(to_path):
            to_path = os.path.join(to_path, os.path.basename(from_path))

        # 执行文件拷贝
        shutil.copy(from_path, to_path)
        print(f"文件已从 {from_path} 拷贝到 {to_path}")

    except Exception as e:
        print(f"拷贝文件时出错: {e}")
        return


def copy_director_with_info(src, dst, overwrite=False):
    """
    拷贝整个目录到目标路径，目标不存在则创建，显示拷贝详细信息

    Args:
        src (str): 源目录路径
        dst (str): 目标目录路径
        overwrite (bool): 是否覆盖目标目录中的文件，默认为 False
    """
    if not os.path.isdir(src):
        logger.error(f"源目录 {src} 不存在或不是一个目录")
        return

    # 如果目标目录不存在，则创建
    if not os.path.exists(dst):
        os.makedirs(dst)
        logger.info(f"目标目录 {dst} 不存在，已创建")

    try:
        all_files = list(Path(src).rglob("*"))
        file_count = sum(1 for item in all_files if item.is_file())
        copied_count = 0

        for item in all_files:
            relative_path = os.path.relpath(item, src)
            target_path = os.path.join(dst, relative_path)

            if item.is_file():
                # 如果目标文件已存在且 overwrite 为 False，则跳过
                if os.path.exists(target_path) and not overwrite:
                    logger.info(f"文件已存在，跳过: {target_path}")
                    continue

                # 确保目标文件的父目录存在
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # 拷贝文件
                shutil.copy2(item, target_path)
                copied_count += 1
                logger.info(
                    f"Copied {copied_count}/{file_count}: {item} -> {target_path}"
                )
            elif item.is_dir():
                # 如果是目录，则确保目标目录存在
                os.makedirs(target_path, exist_ok=True)

        logger.info(f"目录拷贝完成: {src} -> {dst}")
    except Exception as e:
        logger.error(f"拷贝目录失败: {e}")


def move_directory_tree_with_info(from_path, to_path):
    """
    移动整个目录树到目标路径，如果目标路径不存在则创建，并在移动时输出信息。

    :param src: 源目录的路径
    :param dst: 目标目录的路径
    """
    if not os.path.exists(from_path):
        logger.error(f"Source directory does not exist: {from_path}")
        return

    if os.path.exists(to_path):
        logger.warning(f"Removing existing directory: {to_path}")
        shutil.rmtree(to_path)

    try:
        shutil.move(from_path, to_path)
        logger.info(f"Directory moved successfully from {from_path} to {to_path}")
    except Exception as e:
        logger.error(f"Falied to move directory: {e}")


def zip_directory(src, output_filename, archive_format="zip"):
    """
    将指定目录打包为压缩文件。

    :param src: 源目录路径
    :param output_filename: 输出压缩文件的名称（不包括扩展名）
    :param archive_format: 压缩格式，默认为 'zip'，支持 'zip', 'tar', 'gztar', 'bztar', 'xztar'
    :return: None
    """
    if not os.path.isdir(src):
        print(f"源目录 {src} 不存在或不是一个目录")
        return

    try:
        # 获取输出文件的完整路径（包括扩展名）
        output_path = shutil.make_archive(output_filename, archive_format, src)
        print(f"成功将 {src} 打包为 {output_path}")
    except shutil.Error as e:
        print(f"shutil.error: {e}")
    except OSError as e:
        print(f"OS error: {e}")

def unzip_file(zip_path, extract_to):
    """
    解压缩 ZIP 文件到指定路径。

    :param zip_path: ZIP 文件的路径
    :param extract_to: 解压缩的目标目录路径
    :return: None
    """
    if not os.path.isfile(zip_path):
        print(f"ZIP 文件 {zip_path} 不存在")
        return

    try:
        # 确保目标目录存在
        os.makedirs(extract_to, exist_ok=True)

        # 解压缩 ZIP 文件
        shutil.unpack_archive(zip_path, extract_to, format="zip")
        print(f"成功将 {zip_path} 解压缩到 {extract_to}")
    except shutil.ReadError as e:
        print(f"读取 ZIP 文件时出错: {e}")
    except Exception as e:
        print(f"解压缩时出错: {e}")
