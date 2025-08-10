# TTS 文本转语音应用

一个基于 Streamlit 的文本转语音应用，支持批量处理 Excel 文件中的文本内容，并生成对应的音频文件。

## 功能特点

- 📁 支持 Excel 文件上传（.xlsx 格式）
- 🎵 批量文本转语音处理
- 📦 自动打包所有音频文件为 ZIP
- 🌐 支持中英文语音合成
- 💻 简洁易用的 Web 界面

## 使用方法

### 1. 准备 Excel 文件

创建一个 Excel 文件，包含两列：
- **第一列**：音频文件名（不需要包含扩展名）
- **第二列**：要转换的文本内容

示例：
| 文件名 | 文本内容 |
|--------|----------|
| 欢迎词 | 欢迎使用我们的产品 |
| 介绍 | 这是一个功能强大的应用 |
| 结束语 | 谢谢您的使用 |

### 2. 运行应用

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

### 3. 使用步骤

1. 在浏览器中打开应用
2. 上传准备好的 Excel 文件
3. 预览数据确认格式正确
4. 点击"开始转换"按钮
5. 等待处理完成
6. 下载生成的 ZIP 文件

## 部署到 Streamlit Cloud

1. 将代码推送到 GitHub 仓库
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 连接 GitHub 仓库
4. 选择 `app.py` 作为主文件
5. 部署完成后即可在线使用

## 技术栈

- **Streamlit**: Web 应用框架
- **pandas**: Excel 文件处理
- **pyttsx3**: 文本转语音引擎
- **openpyxl**: Excel 文件读取

## 注意事项

- 确保 Excel 文件格式正确（.xlsx）
- 文件名避免使用特殊字符
- 文本内容不宜过长，建议每段不超过 500 字
- 生成的音频文件为 WAV 格式

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！