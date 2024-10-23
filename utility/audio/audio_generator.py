import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"en-US-JennyNeural")
    await communicate.save(outputFilename)





