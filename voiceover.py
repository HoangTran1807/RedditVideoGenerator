import edge_tts

voiceoverDir = "Voiceovers"

voice = 'en-US-GuyNeural'

async def create_voice_over(fileName, text):
    filePath = f"{voiceoverDir}/{fileName}.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filePath)
    return filePath