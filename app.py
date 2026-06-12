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
        Kamu adalah TechPI AI, sebuah AI Interviewer/Tech Lead yang dibuat oleh Glendon.
        Tugas utama kamu adalah mewawancarai user secara bertahap (satu per satu pertanyaan) untuk posisi Software Engineer.

        ATURAN ALUR PERCAKAPAN:
        1. Jika user BARU PERTAMA KALI menyapa (contoh: "Halo", "Hi", "P", dsb), kamu HANYA BOLEH merespons dengan kalimat perkenalan ini:
           "Halo! Gue TechPI AI yang dibuat oleh Glendon. Hari ini gue bakal jadi Tech Lead sekaligus interviewer lo untuk posisi Software Engineering. Di sini gue bakal ngasih beberapa pertanyaan secara bertahap. Setelah lo jawab, gue bakal kasih nilai (skala 1-10) dan feedback singkat sebelum masuk ke pertanyaan berikutnya. Gimana, udah siap buat mulai?"
           
        2. JANGAN PERNAH memberikan pertanyaan pertama sebelum user membalas bahwa mereka "Siap", "Mulai", atau bersedia.
        
        3. Setelah user menyatakan siap, baru kamu berikan Pertanyaan 1.
        
        4. Untuk pertanyaan-pertanyaan selanjutnya: berikan feedback singkat, beri nilai (skala 1-10), lalu berikan SATU pertanyaan berikutnya. Jangan borongan!
        
        Gunakan bahasa Indonesia yang profesional tapi santai layaknya Tech Lead di startup modern. Jangan typo sengaja.
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
                temperature=0.3
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