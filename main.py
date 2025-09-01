import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.deep_services import transcribe_audio
from mangum import Mangum

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    from services.groq_service import generate_response
    bot_reply = generate_response(request.message)
    return {"user": request.message, "bot": bot_reply}


@app.post("/audio-to-text")
async def audio_to_text_endpoint(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Call your Deepgram service with file path
        text = await transcribe_audio(tmp_path)

        # Delete temp file after processing
        os.remove(tmp_path)

        return {"transcription": text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/")
def root():
    return {"message": "Groq + FastAPI server is running!"}


# @app.post("/audio-to-text")
# async def audio_to_text_endpoint(file: UploadFile = File(...)):
#     try:
#         text = await audio_to_text(file)
#         return {"transcription": text}
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return {"error": str(e)}

@app.post("/audio-to-text")
async def audio_to_text_endpoint(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Call your Deepgram service with file path
        text = await transcribe_audio(tmp_path)

        # Delete temp file after processing
        os.remove(tmp_path)

        return {"transcription": text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "Groq + FastAPI server is running!"}


handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
