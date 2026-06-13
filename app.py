import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class MessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageModel]

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        if not req.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")

        user_message = req.messages[-1].content
        
        # Amankan parsing history
        gemini_history = []
        for msg in req.messages[:-1]:
            # Kita amankan: jika role dari react adalah 'user', pakai 'user', selain itu wajib 'model'
            gemini_role = "user" if msg.role == "user" else "model"
            gemini_history.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        sys_instruction = """
        kamu adalah asisten AI TechPI yang dibuat oleh Glendon.
        Tugas kamu adalah menjawab semua pertanyaan yang user inginkan dengan bahasa indonesia yang sopan dan profesional.
        """

        # BENTENG UTAMA ANTI EROR 500:
        if gemini_history:
            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=gemini_history
            )
        else:
            chat = client.chats.create(
                model="gemini-2.5-flash"
            )

        response = chat.send_message(
            message=user_message,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.1
            )
        )
        
        return {"reply": response.text}

    except Exception as e:
        print("ERROR ON BACKEND COK:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)