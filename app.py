import streamlit as st
import pandas as pd
import edge_tts
import asyncio
import io
import zipfile
import tempfile
import os
from pathlib import Path
import base64
from pydub import AudioSegment

# 常见的英语音色选项
ENGLISH_VOICES = {
    "Aria (美国女声)": "en-US-AriaNeural",
    "Jenny (美国女声)": "en-US-JennyNeural",
    "Guy (美国男声)": "en-US-GuyNeural",
    "Davis (美国男声)": "en-US-DavisNeural",
    "Jane (美国女声)": "en-US-JaneNeural",
    "Jason (美国男声)": "en-US-JasonNeural",
    "Sara (美国女声)": "en-US-SaraNeural",
    "Tony (美国男声)": "en-US-TonyNeural",
    "Libby (英国女声)": "en-GB-LibbyNeural",
    "Maisie (英国女声)": "en-GB-MaisieNeural",
    "Ryan (英国男声)": "en-GB-RyanNeural",
    "Sonia (英国女声)": "en-GB-SoniaNeural",
    "Thomas (英国男声)": "en-GB-ThomasNeural"
}

async def text_to_speech_async(text, filename, temp_dir, voice="en-US-AriaNeural"):
    """使用Edge TTS将文本转换为语音并保存为MP3文件"""
    communicate = edge_tts.Communicate(text, voice)
    output_path = os.path.join(temp_dir, f"{filename}.mp3")
    await communicate.save(output_path)
    return output_path

def text_to_speech(text, filename, temp_dir, voice="en-US-AriaNeural", voice2=None):
    """同步包装器，支持双音色"""
    return asyncio.run(text_to_speech_async_dual(text, filename, temp_dir, voice, voice2))

async def text_to_speech_async_dual(text, filename, temp_dir, voice1, voice2=None):
    """支持双音色的TTS转换函数"""
    if voice2 is None or voice2 == voice1:
        # 单音色模式
        return await text_to_speech_async(text, filename, temp_dir, voice1)
    
    # 双音色模式
    # 生成第一个音色的音频
    temp_file1 = os.path.join(temp_dir, f"{filename}_voice1.mp3")
    communicate1 = edge_tts.Communicate(text, voice1)
    await communicate1.save(temp_file1)
    
    # 生成第二个音色的音频
    temp_file2 = os.path.join(temp_dir, f"{filename}_voice2.mp3")
    communicate2 = edge_tts.Communicate(text, voice2)
    await communicate2.save(temp_file2)
    
    # 使用pydub合并音频
    audio1 = AudioSegment.from_mp3(temp_file1)
    audio2 = AudioSegment.from_mp3(temp_file2)
    
    # 添加0.5秒间隔
    silence = AudioSegment.silent(duration=500)  # 500ms = 0.5秒
    
    # 合并音频：音色1 + 间隔 + 音色2
    combined_audio = audio1 + silence + audio2
    
    # 保存合并后的音频
    output_path = os.path.join(temp_dir, f"{filename}.mp3")
    combined_audio.export(output_path, format="mp3")
    
    # 清理临时文件
    if os.path.exists(temp_file1):
        os.remove(temp_file1)
    if os.path.exists(temp_file2):
        os.remove(temp_file2)
    
    return output_path

def create_zip_file(audio_files):
    """创建包含所有音频文件的ZIP文件"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, filename in audio_files:
            if os.path.exists(file_path):
                zip_file.write(file_path, f"{filename}.mp3")
    
    zip_buffer.seek(0)
    return zip_buffer

def get_audio_player_html(audio_path):
    """生成音频播放器HTML"""
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio controls>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        您的浏览器不支持音频播放。
    </audio>
    """
    return audio_html

def main():
    st.set_page_config(
        page_title="TTS 文本转语音应用",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 TTS 文本转语音应用 (Edge TTS)")
    st.markdown("---")
    
    # 音色选择和试听区域
    st.subheader("🎤 音色选择")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_voice_name = st.selectbox(
            "第一个音色（必选）",
            options=list(ENGLISH_VOICES.keys()),
            index=0,
            help="选择主要的英语音色"
        )
        selected_voice = ENGLISH_VOICES[selected_voice_name]
    
    with col2:
        # 添加"无"选项到音色列表
        voice_options = ["无（仅使用第一个音色）"] + list(ENGLISH_VOICES.keys())
        selected_voice2_name = st.selectbox(
            "第二个音色（可选）",
            options=voice_options,
            index=0,
            help="选择第二个音色，如果选择则会与第一个音色合并播放"
        )
        selected_voice2 = None if selected_voice2_name == "无（仅使用第一个音色）" else ENGLISH_VOICES[selected_voice2_name]
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # 添加间距
        if st.button("🔊 试听音色", help="点击试听选中的音色组合"):
            test_text = "Hello! This is a voice preview. How do you like this voice?"
            with st.spinner("正在生成试听音频..."):
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        preview_path = text_to_speech(test_text, "preview", temp_dir, selected_voice, selected_voice2)
                        if os.path.exists(preview_path):
                            audio_html = get_audio_player_html(preview_path)
                            if selected_voice2:
                                st.markdown(f"**🎵 双音色试听：{selected_voice_name} + {selected_voice2_name}**", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**🎵 单音色试听：{selected_voice_name}**", unsafe_allow_html=True)
                            st.markdown(audio_html, unsafe_allow_html=True)
                        else:
                            st.error("❌ 试听音频生成失败")
                except Exception as e:
                    st.error(f"❌ 试听失败: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("""
    ### 使用说明
    1. **选择音色**：选择第一个音色（必选），可选择第二个音色实现双音色效果
    2. **试听音色**：点击试听按钮预听音色效果
       - 单音色：仅使用第一个音色
       - 双音色：第一个音色播放完毕后，间隔0.5秒，再播放第二个音色
    3. **上传文件**：上传Excel文件(.xlsx格式)
    4. **文件格式**：确保Excel文件包含两列
       - 第一列：音频文件名
       - 第二列：要转换的英文文本内容
    5. **开始转换**：点击转换按钮进行批量处理
    6. **下载音频**：获取包含所有MP3文件的ZIP压缩包
    """)
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择Excel文件", 
        type=['xlsx'], 
        help="请上传包含音频名和文本内容的Excel文件"
    )
    
    if uploaded_file is not None:
        try:
            # 读取Excel文件
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ 文件上传成功！共找到 {len(df)} 行数据")
            
            # 显示数据预览
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10))
            
            # 检查数据格式
            if len(df.columns) < 2:
                st.error("❌ Excel文件至少需要包含两列数据！")
                return
            
            # 获取列名
            filename_col = df.columns[0]
            text_col = df.columns[1]
            
            st.info(f"📝 将使用 '{filename_col}' 作为文件名，'{text_col}' 作为转换文本")
            
            # 转换按钮
            if st.button("🎯 开始转换", type="primary"):
                if len(df) == 0:
                    st.error("❌ 没有找到有效数据！")
                    return
                
                # 创建临时目录
                with tempfile.TemporaryDirectory() as temp_dir:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    audio_files = []
                    
                    # 逐行处理数据
                    for index, row in df.iterrows():
                        filename = str(row[filename_col]).strip()
                        text_content = str(row[text_col]).strip()
                        
                        if not filename or not text_content:
                            st.warning(f"⚠️ 跳过第 {index + 1} 行：文件名或文本内容为空")
                            continue
                        
                        # 清理文件名，移除不合法字符
                        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        
                        status_text.text(f"正在处理: {filename}...")
                        
                        try:
                            # 转换文本为语音（支持双音色）
                            audio_path = text_to_speech(text_content, filename, temp_dir, selected_voice, selected_voice2)
                            audio_files.append((audio_path, filename))
                            
                        except Exception as e:
                            st.error(f"❌ 处理 '{filename}' 时出错: {str(e)}")
                            continue
                        
                        # 更新进度条
                        progress = (index + 1) / len(df)
                        progress_bar.progress(progress)
                    
                    if audio_files:
                        status_text.text("正在创建ZIP文件...")
                        
                        # 创建ZIP文件
                        zip_buffer = create_zip_file(audio_files)
                        
                        status_text.text(f"✅ 转换完成！成功生成 {len(audio_files)} 个音频文件")
                        progress_bar.progress(1.0)
                        
                        # 提供下载链接
                        st.download_button(
                            label="📥 下载音频文件包",
                            data=zip_buffer.getvalue(),
                            file_name="tts_audio_files.zip",
                            mime="application/zip",
                            type="primary"
                        )
                        
                        st.success(f"🎉 所有音频文件已准备就绪！点击上方按钮下载ZIP文件。")
                    else:
                        st.error("❌ 没有成功生成任何音频文件！")
        
        except Exception as e:
            st.error(f"❌ 处理文件时出错: {str(e)}")
    
    # 侧边栏信息
    with st.sidebar:
        st.header("ℹ️ 应用信息")
        st.markdown("""
        **功能特点：**
        - 🎤 多种英语音色选择
        - 🔊 音色试听功能
        - 🎭 **双音色合并功能**
        - 📁 支持Excel文件上传
        - 🎵 批量文本转语音
        - 📦 自动打包下载
        - ⚡ 基于Edge TTS高质量合成
        
        **双音色模式：**
        - 可同时选择两个不同音色
        - 每段文本用两个音色各读一遍
        - 音色间自动添加0.5秒间隔
        - 生成更丰富的音频效果
        
        **支持格式：**
        - 输入：.xlsx Excel文件
        - 输出：.mp3 音频文件（ZIP打包）
        
        **可用音色：**
        - 美国英语：Aria, Jenny, Guy, Davis等
        - 英国英语：Libby, Ryan, Thomas等
        
        **注意事项：**
        - 确保Excel文件格式正确
        - 建议使用英文文本内容
        - 双音色模式文件会更大
        - 文件名避免特殊字符
        """)
        
        st.markdown("---")
        st.markdown("💡 **提示**: 先试听音色，选择您喜欢的声音再进行批量转换。")

if __name__ == "__main__":
    main()