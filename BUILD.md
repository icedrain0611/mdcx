# MDCx 120250810 Windows 本地构建记录

## 产物

| 项目 | 值 |
| --- | --- |
| 文件 | `MDCx-120250810-manual-windows-x86_64.exe` |
| 路径 | `D:\mdcx-icedrain\MDCx-120250810-manual-windows-x86_64.exe` |
| 大小 | 112,087,101 字节（106.9 MB） |
| SHA256 | `7700af464f8bba292cc75dacbc4e88dc1fa38a19bc82948605e8bd8d0eda3fb3` |
| 形态 | PyInstaller 单文件、无控制台窗口（`-F -w`） |
| 构建时间 | 2026-11-14 15:12（第二版，含自定义匹配规则） |

> 第一版（未修改源码，2026-11-14 14:36）SHA256 为 `5bd4598206acb16fb63883c7925813c3a6b843bdaeb1a8fdab6232d1e4b6b6cf`，字节数 112,087,244；已被第二版覆盖。

## 第二版定制修改

在原版基础上增加「无码破解」路径匹配关键字：`-LTX`、`jasna`，均为不区分大小写匹配。

改动文件（3 个）：

| 文件 | 位置 | 改动 |
| --- | --- | --- |
| `src/models/core/file.py` | `get_file_info()` 内「判断是否是马赛克破坏版」分支，原第 1124-1136 行 | 条件新增 `or "-ltx" in file_path.lower()`、`or "jasna" in file_path.lower()` |
| `src/views/MDCx.py` | `label_116` 文案（原第 11652 行，运行时真正加载的 UI 代码） | 关键字列表加入「-LTX」、「jasna」，并注明不区分大小写 |
| `src/views/MDCx.ui` | 同名 label 的 `text` 属性（原第 14017 行，Qt Designer 源文件） | 与上一行文案保持同步 |

判定逻辑现在是：

```python
        if (
            "-uncensored." in file_path.lower()
            or "umr." in file_path.lower()
            or "破解" in file_path
            or "克破" in file_path
            or (umr_style and umr_style in file_path)
            or "-u." in file_path.lower()
            or "-uc." in file_path.lower()
            or "-ltx" in file_path.lower()
            or "jasna" in file_path.lower()
        ):
            destroyed = umr_style
            mosaic = "无码破解"
```

新增关键字只影响「识别为无码破解」，命名后缀仍取配置项 `umr_style`（默认 `-破解`），未改动默认值。

### 修改验证

1. 逻辑测试（调用真实 `get_file_info()`，测试目录 `build-work\ruletest`）：

   | 测试文件 | 番号解析 | mosaic | 重命名后名称 | 结果 |
   | --- | --- | --- | --- | --- |
   | `ABC-123-LTX.mp4` | ABC-123 | 无码破解 | ABC-123-破解 | PASS |
   | `ABC-124-jasna.mp4` | ABC-124 | 无码破解 | ABC-124-破解 | PASS |
   | `XYZ-777-JaSNA.mkv` | XYZ-777 | 无码破解 | XYZ-777-破解 | PASS |
   | `ABCD-125-lTx.mp4` | ABCD-125 | 无码破解 | ABCD-125-破解 | PASS |
   | `ABCD-126-normal.mp4` | ABCD-126 | （空） | ABCD-126 | PASS（未误判） |

   （`mosaic` 通过 `json_data["mosaic"]` 读取，`config.init()` 已初始化）

2. GUI 文案测试：实例化 `Ui_MDCx` 后读取 `label_116.text()`，包含 `-uncensored.`/`破解`/`克破`/`UMR.`/`-LTX`/`jasna`/`不区分大小写`。
3. 打包产物测试：解包 exe 内 `PYZ.pyz`，在 `models.core.file` 字节码常量中找到 `-ltx`、`jasna`；在 `views.MDCx` 常量中找到新文案全文。确认改动确实进入 exe，不是只改了源码。
4. 启动冒烟：从独立空目录启动，14 秒后子进程窗口标题 `MDCx`、工作集约 167 MB，进程正常；随后已终止。


## 源码

- 仓库：https://github.com/sqzw-x/mdcx
- Tag：`120250810`
- 下载地址：`https://codeload.github.com/sqzw-x/mdcx/zip/refs/tags/120250810`（release 页的 Source code (zip)）
- 解压位置：`D:\mdcx-icedrain\build-work\src\mdcx-120250810`
- 原始压缩包：`D:\mdcx-icedrain\build-work\mdcx-120250810-src.zip`（6.11 MB）

未使用 git（本机未安装），直接用 tag 的源码 zip，内容与仓库该 tag 一致。

## 工具链

| 组件 | 版本 / 位置 |
| --- | --- |
| Python | 3.9.13 x64（官方安装包，独立目录 `D:\mdcx-icedrain\build-work\py39`，未改动系统 Python） |
| pip | 24.0（依赖走清华镜像 `pypi.tuna.tsinghua.edu.cn`） |
| PyInstaller | 6.14.1（requirements.txt 锁定版本） |
| PyQt5 | 5.15.6（+ PyQt5-Qt5 5.15.2） |
| OpenCV | opencv-contrib-python-headless 4.7.0.68 |
| NumPy | 1.26.4 |
| curl-cffi | 0.6.0b9 |

版本选择依据 `.github/workflows/release.yml`：官方 CI 的 `PYTHON_VERSION: 3.9`、Windows job 用 `pip install -r requirements.txt`，requirements 里的固定版本（PyQt5 5.15.6、opencv 4.7.0.68、numpy 1.26.4）在 Python 3.13 上没有可用 wheel，因此必须用 3.9 复刻。

## 构建命令

构建脚本直接使用仓库自带 `scripts/build-action.ps1`（CI 中为 `scripts/build-action`），等价的显式调用：

```powershell
$env:PYTHONPATH = "<src>\src"
& "D:\mdcx-icedrain\build-work\py39\python.exe" -m PyInstaller -n MDCx -F `
  -i "resources/Img/MDCx.ico" -w main.py -p "./src" `
  --add-data "resources:resources" --add-data "libs:." `
  --hidden-import socks --hidden-import urllib3 --hidden-import _cffi_backend `
  --collect-all curl_cffi
```

注意：本机 PowerShell 会话里 `python` 是解释器别名（指向 3.13 沙箱解释器），会遮住 PATH，直接 `python -m PyInstaller` 会报 `No module named PyInstaller`；必须用 py39 的绝对路径调用。

## 校验

1. `main.py` 通过 `py_compile`，依赖导入自检通过（PyQt5/cv2/numpy/lxml/pyquery/curl_cffi/socks/urllib3/zhconv/langid/oshash/ping3/PIL）。
2. 打包内容经 `pyi-archive_viewer` 核对，关键项均在包内：`resources\Img\MDCx.ico`、`resources\zhconv\zhcdict.json`、`libs\libcrypto-1_1-x64.dll`、`libssl-1_1-x64.dll`、`PyQt5\Qt5\bin\Qt5Core.dll`。
3. 启动冒烟测试：exe 从独立空目录启动，12 秒后进程存活，子进程窗口标题为 `MDCx`、工作集约 164 MB，确认 GUI 正常创建；测试后已终止进程。运行期资源通过 `sys._MEIPASS` 定位，单文件模式无路径依赖。

未做的验证：未进行真实刮削任务（需要对应站点与代理环境）；未做 Digital Signature 签名（官方 CI 产物同样未签名）。

## 目录结构

```
D:\mdcx-icedrain\
├─ MDCx-120250810-manual-windows-x86_64.exe   ← 交付产物
├─ BUILD.md                                    ← 本记录
└─ build-work\
   ├─ mdcx-120250810-src.zip                   ← 源码包
   ├─ src\mdcx-120250810\                      ← 源码、dist\MDCx.exe、build 中间产物
   ├─ py39\                                    ← 构建专用 Python 3.9.13
   ├─ python-3.9.13-amd64.exe                  ← 安装包
   ├─ build.log                                  ← 第一版构建日志
   ├─ build2.log                                 ← 第二版（含 -LTX/jasna 规则）构建日志
   ├─ archive.txt                              ← 打包清单
   ├─ selftest_rule.py                         ← 匹配规则测试脚本
   ├─ selftest_gui_text.py                     ← GUI 文案测试脚本
   ├─ check_pyz.py                             ← exe 内字节码核对脚本
   ├─ ruletest\                                ← 规则测试用样本文件
   └─ smoketest\, smoketest2\                  ← 两次冒烟测试工作目录
```

如需清理，删除 `build-work` 即可，不影响已交付的 exe。

## 发布

| 项目 | 值 |
| --- | --- |
| 仓库 | https://github.com/icedrain0611/mdcx |
| 分支 | `120250810-ltx`（独立历史，`master` 保持上游重构版不变） |
| Tag / Release | `120250810-ltx` |
| Release 页面 | https://github.com/icedrain0611/mdcx/releases/tag/120250810-ltx |
| Release 附件 | `MDCx-120250810-manual-windows-x86_64.exe`、`MDCx-120250810-ltx-src.zip`、`SHA256SUMS.txt` |

仓库内容 = 上游 tag `120250810` 的全部文件 + 上表 3 个定制文件 + 本文件。

刻意排除（已在 `.gitignore` 中）：`config.ini` 与 `【4K】/【中文字幕】/【LTX】.ini`（含站点登录 cookie、本地代理配置，不外发）、`userdata/`（运行时缓存与映射数据）、`build/`、`dist/`、`MDCx.spec`、`MDCx.config`（构建中间产物）。可执行文件只作为 Release 附件分发，不进仓库（单文件 106.9 MB，超过 Git 单文件 100 MB 限制）。