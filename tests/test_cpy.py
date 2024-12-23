import shutil
import os


def copy_with_info(src, dst):
    """
    自定义拷贝函数，用于拷贝单个文件并在拷贝时输出信息。

    :param src: 源文件路径
    :param dst: 目标文件路径
    """
    try:
        # 拷贝文件
        shutil.copy2(src, dst)
        print(f"Copied: {os.path.relpath(src)} -> {os.path.relpath(dst)}")
    except Exception as e:
        print(f"Failed to copy {src}: {e}")


def copy_directory_tree_with_info(src, dst):
    """
    拷贝整个目录树到目标路径，如果目标路径不存在则创建，并在拷贝时输出信息。

    :param src: 源目录的路径
    :param dst: 目标目录的路径
    """

    if os.path.exists(dst):
        print(f"Removing existing directory: {dst}")
        shutil.rmtree(dst)
        
    try:
        shutil.copytree(src, dst, copy_function=copy_with_info)
        print(f"Directory copied successfully from {src} to {dst}")
    except Exception as e:
        print(f"Falied to copy directory: {e}")


# 源目录路径和目标目录路径
source_dir = 'E:\\cwcx\\bundles\\Android\\ResPackage\\1.0.0-24-12-20-191209'
destination_dir = 'E:\\cwcx\\bundles\\Android\\ResPackage\\latest'

# 拷贝整个目录树
copy_directory_tree_with_info(source_dir, destination_dir)
