import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"am-ET-MekdesNeural")
    await communicate.save(outputFilename)





