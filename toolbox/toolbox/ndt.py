import subprocess
import os
from rich.console import Console
import yaml
import ffmpeg
import json
import re
import youtube_dl


# 初始化 rich 控制台
Con = Console()

# 初始化链接
Urls = {"Bilibili": [], "Other": []}

# 打开并加载 YAML 配置
try:
    with open("BBDown.yml", "r") as _f_:
        Cfg = yaml.load(_f_, Loader=yaml.FullLoader)
        if Cfg is None:  # Adding this check to handle the case where YAML file is empty
            Cfg = {"mode": None, "path": None}
except FileNotFoundError:
    Cfg = {"mode": None, "path": None}

try:
    with open("easylist.txt", "r") as _f_:
        content = _f_.read()
        if content:
            Urls = {"Bilibili": [], "Other": []}
            for line in content.split("\n"):
                if "bilibili.com" in line:
                    Urls["Bilibili"].append(line)
                else:
                    Urls["Other"].append(line)
except FileNotFoundError:
    pass


class BBDown:
    Option = "BBDown "
    Modelist = [
        "",
        "--video-only",
        "--audio-only",
        "--danmaku-only",
        "--cover-only",
        "--sub-only",
    ]

    def __init__(self):
        self.run()

    def getpath(self):
        """
        提示用户输入下载路径，并更新全局 Option 和 Cfg 字典中的路径值。
        """
        if Tool.getyn(Con.input("[green]需要保存在当前目录下吗？[/green][Y/n] ")):
            Cfg["path"] = ""
        else:
            path = Con.input("[green]请输入保存路径:")
            self.Option = self.Option + ' --work-dir "' + path + '"'
            Cfg["path"] = path

    def givepath(self):
        """
        提示用户确认或输入下载路径，并更新全局 Option 和 Cfg 字典中的路径值。
        """
        if Cfg.get("path") is None:
            self.getpath()
        else:
            if Tool.getyn(
                Con.input(f"[green]继续使用 {Cfg['path']} 文件夹？[/green][Y/n] ")
            ):
                self.Option = self.Option + "--work-dir " + Cfg["path"] + " "
            else:
                self.getpath()
        print()

    def getmode(self):
        """
        提示用户选择下载模式，并更新全局 Option 和 Cfg 字典中的模式值。
        """
        Mode = int(
            Con.input(
                """
[blue]0. 无选项[/blue]
[red]1. 仅视频[/red]
[orange]2. 仅音频[/orange]
[yellow]3. 仅弹幕[/yellow]
[blue]4. 仅封面[/blue]
[cyan]5. 仅字幕[/cyan]
[purple]9. 退出[/purple]
[green bold]请选择你需要的模式[/green bold]:"""
            )
        )
        if Mode == 9:
            exit()  # 用户自定退出
        self.Option = self.Option + " " + self.Modelist[Mode] + " "
        Cfg["mode"] = Mode

    def givemode(self):
        """
        提示用户确认或选择下载模式，并更新全局 Option 和 Cfg 字典中的模式值。
        """
        if Cfg.get("mode") is None:
            self.getmode()
        else:
            ModeList = [
                "无",
                "[red]仅视频[/red]",
                "[orange]仅音频[/orange]",
                "[yellow]仅弹幕[/yellow]",
                "[blue]仅封面[/blue]",
                "[cyan]仅字幕[/cyan]",
            ]
            Get_Real_Mode = Con.input(
                f"[green]继续使用 {ModeList[Cfg['mode']]} 模式？[/green][Y/n] "
            )
            if Tool.getyn(Get_Real_Mode):
                self.Option += f"{self.Modelist[Cfg['mode']]} "
            else:
                self.getmode()
            print()

    def run(self):
        """
        协调整个下载流程，包括获取模式、路径和 URL，并执行下载任务。
        """
        if not Urls["Bilibili"]:
            Con.print("[red]今日无事可做[/red]")
            print()
        else:
            global Option
            self.givemode()
            self.givepath()

            for i, url in enumerate(Urls["Bilibili"]):
                Temp = f"{self.Option} {url}"
                Con.print(f"[green]正在执行第[/green][red]{i}[/red][green]个任务!")
                subprocess.run(Temp, shell=True)

            Con.print("[green bold]下载完成！")
            with open("BBDown.yml", "w") as _f_:
                yaml.dump(data=Cfg, stream=_f_, allow_unicode=True)


class Lux:
    Option = "lux "
    Mode = None

    def __init__(self):
        self.run()

    def getmode(self):
        """
        提示用户选择下载模式
        """
        Mode = int(
            Con.input(
                """
[blue]0. 无选项[/blue]
[red]1. 仅视频[/red]
[orange]2. 仅音频[/orange]
[yellow]3. 不支持[/yellow]
[blue]4. 仅封面[/blue]
[cyan]5. 仅字幕[/cyan]
[purple]9. 退出[/purple]
[green bold]请选择你需要的模式[/green bold]:"""
            )
        )
        if Mode == 9:
            exit()  # 用户自定退出
        Cfg["mode"] = Mode
        return Mode

    def givemode(self):
        """
        提示用户确认或选择下载模式
        """
        if Cfg.get("mode") is None:
            Mode = self.getmode()
        else:
            ModeList = [
                "无",
                "[red]仅视频[/red]",
                "[orange]仅音频[/orange]",
                "[bold red]（不支持）[/bold red]",
                "[blue]仅封面[/blue]",
                "[cyan]仅字幕[/cyan]",
            ]
            Get_Real_Mode = Con.input(
                f"[green]继续使用 {ModeList[Cfg['mode']]} 模式？[/green][Y/n] "
            )
            if Tool.getyn(Get_Real_Mode):
                Mode = Cfg["mode"]
            else:
                Mode = self.getmode()
            print()
        return Mode

    def getpath(self):
        """
        提示用户输入下载路径，并更新全局 Option 和 Cfg 字典中的路径值。
        """
        if Tool.getyn(Con.input("[green]需要保存在当前目录下吗？[/green][Y/n] ")):
            Cfg["path"] = ""
        else:
            path = Con.input("[green]请输入保存路径: ")
            self.Option += f' -o "{path}"'
            Cfg["path"] = path

    def givepath(self):
        """
        提示用户确认或输入下载路径，并更新全局 Option 和 Cfg 字典中的路径值。
        """
        global Option
        if Cfg.get("path") is None:
            self.getpath()
        else:
            if Tool.getyn(
                Con.input(f"[green]继续使用 {Cfg['path']} 文件夹？[/green][Y/n] ")
            ):
                self.Option += f"-o {Cfg['path']} "
            else:
                self.getpath()
        print()

    def run(self):
        """
        协调整个下载流程，包括获取模式、路径和 URL，并执行下载任务。
        """
        if not Urls["Other"]:
            Con.print("[red]今日无事可做[/red]")
            print()
        else:
            global Option
            flag = False
            Mode = self.givemode()
            self.givepath()

            if Mode not in [0, 1, 4]:
                for url in Urls["Other"]:
                    result = json.loads(
                        subprocess.run(
                            f"lux -j {url}", shell=True, stdout=subprocess.PIPE
                        ).stdout
                    )
                    print(type(result))
                    video = f"{result[0]['title']}.{result[0]['streams'][list(result[0]['streams'].keys())[-1]]['ext']}"
                    audio = f"{result[0]['title']}.mp3"
                    cover = f"{result[0]['title']}.png"
                    flag = True

            elif Mode == 4:
                self.Option += " -C "

            for i, url in Urls["Other"]:
                Temp = f"{self.Option} {url}"
                Con.print(f"[green]正在执行第[/green][red]{i}[/red][green]个任务!")
                subprocess.run(Temp, shell=True)

            Con.print("[green bold]下载完成！")

            if flag:
                match Mode:
                    case 2:
                        FFmpegTool.get_audio(video, audio)
                        os.remove(video)
                    case 3:
                        FFmpegTool.get_cover(video, cover)
                        os.remove(video)

            with open("BBDown.yml", "w") as _f_:
                yaml.dump(data=Cfg, stream=_f_, allow_unicode=True)


class FFmpegTool:
    @staticmethod
    def get_audio(video, audio):
        """
        从视频中提取音频
        :param video: 输入视频文件路径
        :param audio: 输出音频文件路径
        """
        ffmpeg.run(ffmpeg.output(ffmpeg.input(video), audio))

    @staticmethod
    def get_cover(video, photo, time="00:00:00"):
        """
        从视频中提取封面
        :param video: 输入视频文件路径
        :param photo: 输出封面图像文件路径
        :param time: 提取封面的时间点，默认在第1帧
        """
        (
            ffmpeg.input(video, ss=time)  # 指定时间点
            .output(photo, vframes=1)  # 提取一帧
            .run()
        )


class Tool:
    @staticmethod
    def getyn(yn: str) -> bool:
        """
        获取用户输入的 yes/no 答案，并返回布尔值。
        :param yn: 用户输入的字符串
        :return: True 如果输入是 'Y' 或空字符串，否则 False
        """
        yn = yn.upper()
        return yn == "Y" or yn == ""

    @staticmethod
    def inputurls():
        """
        提示用户输入多个 URL，并将其添加到 Urls 列表中。
        """
        global Urls
        _range = 1
        while True:
            url = Con.input(f"[yellow]请输入第{_range}个Url(输入E退出)：")
            if url.upper() == "E":
                break
            else:
                if (
                    "bilibili.com" in url
                    or "AV" in url.upper()
                    or "BV" in url.upper()
                    or "FAV" in url.upper()
                    or "AU" in url.upper()
                ):
                    # url=Tool.sweep_url(url)
                    Urls["Bilibili"].append(url)
                else:
                    # url=Tool.sweep_url(url)
                    Urls["Other"].append(url)
                _range += 1
        print()

    @staticmethod
    def sweep_url(url):
        """
        清洗输入的 URL，去除多余的空格和特殊字符。
        :param url: 输入的 URL
        :return: 清洗后的 URL
        """
        clean_url = re.sub(r"【(?:[^【】]|【(?:[^】]|【[^】]*】)*】)*】", "", url)
        clean_url = re.sub(r"\s+", " ", clean_url).strip()
        return clean_url


def main():
    Tool.inputurls()
    Lux()
    BBDown()

def module(mode, *url):
    pass


# 主函数，负责协调整个流程
if __name__ == "__main__":
    main()
