import os
import ctypes
import logging
import tempfile
import argparse
import PySimpleGUI as sg
from rich import console
from ctypes import wintypes
from pydub import AudioSegment
from rich.progress import Progress
from rich.logging import RichHandler

# Step 0: 初始化程序
Con = console.Console(record=True)

# 初始化解析器
parser = argparse.ArgumentParser(description="Audio Processor")
# 定义 --debug 参数
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
# 定义 --verbose 参数作为 --debug 的子参数
parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
# 定义输入文件，可以使用列表或多次添加
parser.add_argument(
    "-i", "--input", nargs="+", help="Input files (can be a list or multiple entries)"
)
# 定义输出文件
parser.add_argument("-o", "--output", help="Make output file")
args = parser.parse_args()

input_files_provided = args.input is not None and len(args.input) > 0
output_file_provided = args.output is not None

# 设置日志级别
if args.debug:
    log_level = logging.DEBUG if args.verbose else logging.INFO
else:
    log_level = logging.ERROR

# 调试专用，一般不显示日志
FORMAT = "%(message)s"
logging.basicConfig(
    level=log_level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

# 如果没有提供输入文件或输出文件，则打印日志
if not input_files_provided:
    sg.theme("DarkAmber")
    logging.info("Input file not provided.")

if not output_file_provided:
    logging.info("Output file not provided.")

if not input_files_provided or not output_file_provided:
    # Step 1: 定义 OPENFILENAMEW 结构体
    class OPENFILENAME(ctypes.Structure):
        _fields_ = [
            ("lStructSize", wintypes.DWORD),
            ("hwndOwner", wintypes.HWND),
            ("hInstance", wintypes.HINSTANCE),
            ("lpstrFilter", wintypes.LPCWSTR),
            ("lpstrCustomFilter", wintypes.LPWSTR),
            ("nMaxCustFilter", wintypes.DWORD),
            ("nFilterIndex", wintypes.DWORD),
            ("lpstrFile", wintypes.LPWSTR),
            ("nMaxFile", wintypes.DWORD),
            ("lpstrFileTitle", wintypes.LPWSTR),
            ("nMaxFileTitle", wintypes.DWORD),
            ("lpstrInitialDir", wintypes.LPCWSTR),
            ("lpstrTitle", wintypes.LPCWSTR),
            ("Flags", wintypes.DWORD),
            ("nFileOffset", wintypes.WORD),
            ("nFileExtension", wintypes.WORD),
            ("lpstrDefExt", wintypes.LPCWSTR),
            ("lCustData", wintypes.LPARAM),
            ("lpfnHook", wintypes.LPVOID),
            ("lpTemplateName", wintypes.LPCWSTR),
            ("pvReserved", wintypes.LPVOID),
            ("dwReserved", wintypes.DWORD),
            ("FlagsEx", wintypes.DWORD),
        ]

    # Step 2: 使用WinAPI的CFileDialog选择文件
    def select_files(allow_to_munti_select=True, save_mode=False):
        OFN_FILEMUSTEXIST = 0x00001000
        OFN_PATHMUSTEXIST = 0x00000800
        OFN_ALLOWMULTISELECT = 0x00000200
        OFN_OVERWRITEPROMPT = 0x00000002  # 保存模式下提示覆盖文件

        buffer_size = (
            4096 if allow_to_munti_select else 1024
        )  # 根据多文件选择决定缓冲区大小
        file_buffer = ctypes.create_unicode_buffer(buffer_size)

        open_file_name = OPENFILENAME()
        open_file_name.lStructSize = ctypes.sizeof(OPENFILENAME)
        open_file_name.hwndOwner = None
        open_file_name.lpstrFilter = "MP3 Files (*.mp3)\0*.mp3\0WAV Files (*.wav)\0*.wav\0FLAC Files (*.flac)\0*.flac\0M4A Files (*.m4a)\0*.m4a\0All Files (*.*)\0*.*\0"
        open_file_name.lpstrFile = ctypes.cast(file_buffer, wintypes.LPWSTR)
        open_file_name.nMaxFile = buffer_size
        open_file_name.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST

        # 使用保存模式选项
        if save_mode:
            ext = (
                os.path.splitext(file_buffer.value)[1][1:] or "mp3"
            )  # 默认扩展名为 mp3
            open_file_name.lpstrDefExt = ext
            open_file_name.Flags |= OFN_OVERWRITEPROMPT

        elif allow_to_munti_select:
            open_file_name.Flags |= OFN_ALLOWMULTISELECT

        # 调用保存文件或选择文件的 API 方法
        if save_mode:
            if ctypes.windll.comdlg32.GetSaveFileNameW(ctypes.byref(open_file_name)):
                file_path = file_buffer.value
                return [file_path]
        else:
            if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(open_file_name)):
                files = file_buffer.value.split(" ")
                if len(files) > 1 and os.path.isdir(
                    files[0]
                ):  # 多文件选择时，第一个是目录路径
                    dir_path = files[0]
                    file_paths = [
                        os.path.join(dir_path, f) for f in files[1:] if f
                    ]  # 拼接路径
                else:
                    file_paths = [f for f in files if f]  # 单文件情况，过滤空字符串
                return file_paths
        return []

    if not output_file_provided:
        file_list = select_files()
    else:
        file_list = args.input
    logging.info(f"输入文件位置: {file_list}")
    if not output_file_provided:
        ctypes.windll.user32.MessageBoxW(0, "请选择保存文件的位置", "保存提示", 1)
        save_name = select_files(allow_to_munti_select=False, save_mode=True)[0]
    else:
        save_name = args.output
    logging.info(f"保存路径: {save_name}")
else:
    file_list = args.input
    logging.info(f"输入文件位置: {file_list}")
    save_name = args.output
    logging.info(f"保存路径: {save_name}")


# Step 3: 计算最大音频长度
audio_segments = [AudioSegment.from_file(file) for file in file_list]
max_length = max(audio.duration_seconds for audio in audio_segments)


# Step 4: 叠加音频文件
def overlay_audio(audio_segments, max_length, use_TUI=False):
    temp_files = []
    total_files = len(audio_segments)

    if use_TUI:
        with Progress() as progress:
            task = progress.add_task("合并音频...", total=total_files)

            for i, audio in enumerate(audio_segments):
                repeat_count = int(max_length // audio.duration_seconds) + 1
                extended_audio = (audio * repeat_count)[: int(max_length * 1000)]

                # 保存到临时文件
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as temp_file:
                    temp_path = temp_file.name
                    extended_audio.export(temp_path, format="wav")
                    temp_files.append(temp_path)

                progress.update(task, completed=i + 1)
    else:
        layout = [
            [sg.Text("正在合并音频")],
            [
                sg.ProgressBar(
                    total_files, orientation="h", size=(20, 20), key="progress"
                )
            ],
            [sg.Cancel()],
        ]
        window = sg.Window("进度", layout, finalize=True)

        for i, audio in enumerate(audio_segments):
            repeat_count = int(max_length // audio.duration_seconds) + 1
            extended_audio = (audio * repeat_count)[: int(max_length * 1000)]

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
                extended_audio.export(temp_path, format="wav")
                temp_files.append(temp_path)

            window["progress"].update(i + 1)
            event, _ = window.read(timeout=10)
            if event == sg.WIN_CLOSED or event == "Cancel":
                break

        window.close()

    # 合并临时文件
    final_audio = AudioSegment.from_file(temp_files[0], format="wav")
    for temp_file in temp_files[1:]:
        temp_audio = AudioSegment.from_file(temp_file, format="wav")
        final_audio = final_audio.overlay(temp_audio)

    # 清理临时文件
    for temp_file in temp_files:
        os.remove(temp_file)

    return final_audio


final_audio = overlay_audio(audio_segments, max_length)

# Step 5: 输出结果
logging.info(
    f"即将开始，文件名：{os.path.splitext(save_name)[0]+os.path.splitext(save_name)[1]}"
)
final_audio.export(save_name, format=os.path.splitext(save_name)[1][1:])
logging.info(f"合并完成，已保存到：{save_name}")
