import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.deep_services import transcribe_audio

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


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from groq import Groq

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # change "*" to your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Groq client
# client = Groq(api_key="YOUR_GROQ_API_KEY")

# # Store conversation history (in memory for now, later you can use Redis/DB)
# conversation_history = {}

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# @app.post("/chat")
# async def chat(request: ChatRequest):
#     session_id = request.session_id

#     # Initialize session history if new
#     if session_id not in conversation_history:
#         conversation_history[session_id] = [
#             {"role": "system", "content": "You are a helpful AI assistant."}
#         ]

#     # Add user message to history
#     conversation_history[session_id].append({"role": "user", "content": request.message})

#     # Call Groq API with full history
#     chat_completion = client.chat.completions.create(
#         model="llama-3.1-8b-instant",  # or another Groq model
#         messages=conversation_history[session_id],
#     )

#     reply = chat_completion.choices[0].message["content"]

#     # Add bot reply to history
#     conversation_history[session_id].append({"role": "assistant", "content": reply})

#     return {"bot": reply}
