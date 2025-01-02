import shutil
import os
from pathlib import Path
from tqdm import tqdm
from logger import logger


def copy_with_info(src, dst):
    """
    自定义拷贝函数，用于拷贝单个文件并在拷贝时输出信息。

    :param src: 源文件路径
    :param dst: 目标文件路径
    """
    try:
        # 拷贝文件
        shutil.copy2(src, dst)
        logger.info(f"Copied: {src} -> {dst}")
    except shutil.Error as e:
        logger.error(f"Failed to copy {src}: {e}")
    except IOError as e:
        logger.error(f"IO error->{e.errno}:{e.strerror}")


def copy_directory_tree_with_info(src, dst):
    """
    拷贝整个目录树到目标路径，如果目标路径不存在则创建，并在拷贝时输出信息。

    :param src: 源目录的路径
    :param dst: 目标目录的路径
    """

    if os.path.exists(dst):
        logger.info(f"Removing existing directory: {dst}")
        shutil.rmtree(dst)

    try:
        shutil.copytree(src, dst, copy_function=copy_with_info)
        logger.info(f"Directory copied successfully from {src} to {dst}")
    except Exception as e:
        logger.error(f"Falied to copy directory: {e}")


def copy_file_with_progress(src, dst, file_size=None, file_pbar=None):
    """
    复制单个文件并显示文件级别的进度条。

    :param src: 源文件路径
    :param dst: 目标文件路径
    :param file_size: 文件大小（字节），用于进度条的总进度
    :param file_pbar: 文件级别的进度条对象
    """
    try:
        if file_size is None:
            file_size = os.path.getsize(src)

        if file_pbar is None:
            file_pbar = tqdm(total=file_size, unit="B", unit_scale=True,
                             desc=f"Copying {os.path.basename(src)}")

        copied = 0
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                buf = fsrc.read(1024 * 8)  # 每次读取 8KB
                if not buf:
                    break
                fdst.write(buf)
                copied += len(buf)
                file_pbar.update(len(buf))  # 更新文件级别的进度条

        file_pbar.close()
        # print(f"Copied: {src} -> {dst}", end='\r', flush=True)
    except Exception as e:
        logger.error(f"Failed to copy file {src}: {e}")


def copy_directory_with_progress(src, dst):
    """
    拷贝整个目录树到目标路径，如果目标路径不存在则创建，并在拷贝时显示单文件进度和总进度。

    :param src: 源目录的路径
    :param dst: 目标目录的路径
    """
    if not os.path.isdir(src):
        logger.error(f"Source directory {src}"
                     "does not exist or is not a directory")
        return

    # 如果目标目录已存在，则删除它
    if os.path.exists(dst):
        logger.info(f"Removing existing directory: {dst}")
        shutil.rmtree(dst)

    try:
        # 获取源目录中所有文件的路径列表
        all_files = list(Path(src).rglob('*'))
        file_count = sum(1 for item in all_files if item.is_file())
        total_size = sum(os.path.getsize(file)
                         for file in all_files if file.is_file())
        logger.info(f"Total files to copy: {file_count}, "
                    f"Total size: {total_size / (1024 * 1024):.2f} MB")

        # 创建总体进度条
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Total Progress") as overall_pbar:
            def copy_with_progress(src, dst):
                file_size = os.path.getsize(src)

                # 创建文件级别的进度条
                with tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Copying {os.path.basename(src)}", leave=False) as file_pbar:
                    copy_file_with_progress(src, dst, file_size, file_pbar)
                    overall_pbar.update(file_size)  # 更新总体进度条

            # 使用自定义的 copy_function 并传递给 shutil.copytree()
            shutil.copytree(src, dst, copy_function=copy_with_progress)

        logger.info(f"Directory copied successfully from {src} to {dst}")
    except Exception as e:
        logger.error(f"Failed to copy directory: {e}")


def move_all_files_and_dirs(from_dir, to_dir, overwrite=False):
    """
    移动一个目录下的所有子文件和子目录到另一个目录。

    :param from_dir: 源目录路径
    :param to_dir: 目标目录路径
    :param overwrite: 如果目标目录中已存在同名文件或目录，是否覆盖（默认为False）
    """
    from_path = Path(from_dir)
    to_path = Path(to_dir)

    # 确保源目录存在
    if not from_path.exists():
        logger.error(f"源目录 '{from_dir}' 不存在")

    # 确保目标目录存在，如果不存在则创建
    to_path.mkdir(parents=True, exist_ok=True)

    # 遍历源目录中的所有文件和子目录
    for item in from_path.iterdir():
        to_item = to_path / item.name

        # 如果目标路径已存在且是一个目录
        if to_item.exists() and to_item.is_dir() and item.is_dir():
            # 递归移动源子目录中的内容到目标子目录
            move_all_files_and_dirs(item, to_item, overwrite)
        else:
            # 如果目标路径已存在且不是目录
            if to_item.exists():
                if overwrite:
                    # 如果选择覆盖，则删除目标路径
                    if to_item.is_file() or to_item.is_symlink():
                        to_item.unlink()
                    else:
                        shutil.rmtree(to_item)
                else:
                    # 如果选择不覆盖，则跳过
                    logger.warning(f"跳过 '{to_item}'，因为目标路径已存在")
                    continue

            # 移动文件或目录
            shutil.move(str(item), str(to_item))
            logger.info(f"移动 '{item}' 到 '{to_item}'")


def move_directory_tree_with_info(src, dst):
    """
    移动整个目录树到目标路径，如果目标路径不存在则创建，并在移动时输出信息。

    :param src: 源目录的路径
    :param dst: 目标目录的路径
    """

    if os.path.exists(dst):
        logger.info(f"Removing existing directory: {dst}")
        shutil.rmtree(dst)

    try:
        shutil.move(src, dst)
        logger.info(f"Directory moved successfully from {src} to {dst}")
    except Exception as e:
        logger.error(f"Falied to move directory: {e}")


def pack_directory(src, output_filename, archive_format='zip'):
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


def pack_directory_to_specific_location(src, output_dir, archive_name, archive_format='zip') -> str:
    if not os.path.isdir(src):
        print(f"源目录 {src} 不存在或不是一个目录")
        return None

    if not os.path.isdir(output_dir):
        print(f"输出目录 {output_dir} 不存在")
        return None

    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 构建完整的输出文件路径（不包括扩展名）
        output_filename = os.path.join(output_dir, archive_name)

        # 打包目录
        output_path = shutil.make_archive(output_filename, archive_format, src)
        print(f"成功将 {src} 打包为 {output_path}")
        return output_path
    except shutil.Error as e:
        print(f"shutil.error: {e}")
        return None
    except OSError as e:
        print(f"OS error: {e}")
        return None


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
        shutil.unpack_archive(zip_path, extract_to, format='zip')
        print(f"成功将 {zip_path} 解压缩到 {extract_to}")
    except shutil.ReadError as e:
        print(f"读取 ZIP 文件时出错: {e}")
    except Exception as e:
        print(f"解压缩时出错: {e}")
