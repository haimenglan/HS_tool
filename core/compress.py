import shutil
import os

def zip_folder(folder_path):
    """
    压缩文件(夹)为zip格式：
    指令shutil.make_archive, 可选参数如下：
        1.base_name： 生成的压缩包的名字或者路径，不带.zip后缀的。
            1) 给的是路径，例如 D:\a\b 将在D盘a文件夹下生成一个b.zip的压缩包
            2）如果带”.zip“，比如D:\a\b.zip 将在D盘a文件夹生成一个b.zip.zip的压缩包
            3）给的只有压缩包名字则在当前工作目录（python工作目录下）生成”名字.zip“
        2.format： 压缩包种类，“zip”, “tar”, “bztar”，“gztar”
        3.root_dir: 如果不指定base_dir, 则是要压缩的文件夹路径，如果指定了basedir？
        4.base_dir： 如果root_dir 和 base_dir都是folder_path, 则压缩后的文件会包含系统的全路径
    """
    base_name = folder_path  # 生成的压缩文件位置为 要压缩的文件夹所在路径
    zip_path = shutil.make_archive(base_name, "zip", root_dir=os.path.dirname(folder_path),
                                   base_dir=os.path.basename(folder_path))
    # zip_f = zipfile.ZipFile(zip_path, mode)
    # zip_f.write(book_path, arcname="note/" + os.path.basename(book_path)) # arcname 是写入的文件在压缩包里面的路径
    return zip_path
