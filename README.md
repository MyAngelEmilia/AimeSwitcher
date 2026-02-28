# Aime 卡号快切

长按数字键 (0-9) 快速切换 Aime 卡号，适用于需要频繁更换刷卡身份的场景。

## 背景

买了一个 maimai 控制器在家玩，偶尔有几个不同的朋友来家里打。每次换人都要手动改 `aime.txt` 里的卡号，太麻烦了；买个读卡器又要花几十块钱，没必要。于是就有了这个项目 —— 长按一个数字键就能一键切卡，省事又省钱。

本项目全程由 Cursor 生成。

## 功能

- **长按数字键触发** — 按住 0-9 任意数字键（大键盘/小键盘均可）超过阈值即触发切换
- **自动写入卡号** — 将预设卡号写入指定的 `aime.txt` 文件
- **模拟长按 Enter** — 写入完成后自动模拟长按 Enter 键（时长可配置）
- **浮窗通知** — 切换成功后右上角弹出浮窗提示，显示脱敏卡号和备注，不会抢走当前程序焦点
- **GUI 配置界面** — 可视化设置 0-9 对应卡号和备注、文件路径、按键参数
- **数据持久化** — 配置自动保存到 JSON 文件，关闭重开不丢失

## 项目结构

```
AimeSwitcher/
├── main.py            # 程序入口
├── app.py             # 主窗口 UI，组装所有模块
├── config.py          # 配置管理（加载/保存/默认值/路径）
├── theme.py           # 调色板与字体常量
├── widgets.py         # 自定义 UI 控件（ModernButton）
├── toast.py           # 不抢焦点的浮窗通知
├── key_listener.py    # 全局键盘监听与长按检测
├── switcher.py        # 卡号写入 + Enter 模拟
├── requirements.txt   # Python 依赖
├── build.bat          # 一键编译为 exe
└── README.md
```

## 使用方法

### 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

> 需要**管理员权限**运行（`keyboard` 库需要管理员权限进行全局键盘监听）。

### 编译为 exe

双击 `build.bat`，编译产物在 `dist\Aime卡号快切.exe`。

将 exe 复制到目标目录（与 `DEVICE\aime.txt` 同级），双击运行即可。

### 配置文件

首次运行会在 exe 同目录自动生成 `aime_switcher_config.json`：

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `aime_path` | aime.txt 文件路径 | `./DEVICE/aime.txt` |
| `enter_duration` | Enter 长按秒数 | `3.0` |
| `long_press_threshold` | 长按触发阈值（毫秒） | `500` |
| `debug` | 是否显示日志面板 | `false` |
| `cards` | 0-9 数字键对应的卡号和备注 | 空 |

## 依赖

- Python 3.10+
- [keyboard](https://github.com/boppreh/keyboard)
- tkinter（Python 内置）
- Windows（使用 Win32 API 实现不抢焦点浮窗）
