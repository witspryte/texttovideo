import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"en-ET-MekdesNeural")
    await communicate.save(outputFilename)





