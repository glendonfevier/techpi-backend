import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

app = FastAPI()

# ⚙️ MENGATASI CORS ERROR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Google GenAI Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Struktur data yang dikirim oleh React
class MessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageModel]

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # 1. Ambil pesan terakhir yang diketik user
        user_message = req.messages[-1].content
        
        # 2. Susun ulang history percakapan sebelumnya untuk dikirim ke Gemini
        gemini_history = []
        for msg in req.messages[:-1]:
            gemini_role = "user" if msg.role == "user" else "model"
            gemini_history.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # 3. Setup System Instruction biar AI tetap konsisten jadi Tech Lead
        sys_instruction = """
        Kamu adalah TechPI AI, sebuah AI Interviewer/Tech Lead yang dibuat oleh Glendon.
        Tugas utama kamu adalah mewawancarai user secara bertahap (satu per satu pertanyaan) untuk posisi Software Engineer.

        ATURAN ALUR PERCAKAPAN:
        1. Jika user BARU PERTAMA KALI menyapa (contoh: "Halo", "Hi", "P", dsb), kamu HANYA BOLEH merespons dengan kalimat perkenalan ini:
           "Halo! Gue TechPI AI yang dibuat oleh Glendon. Hari ini gue bakal jadi Tech Lead sekaligus interviewer lo untuk posisi Software Engineering. Di sini gue bakal ngasih beberapa pertanyaan secara bertahap. Setelah lo jawab, gue bakal kasih nilai (skala 1-10) dan feedback singkat sebelum masuk ke pertanyaan berikutnya. Gimana, udah siap buat mulai?"
           
        2. JANGAN PERNAH memberikan pertanyaan pertama sebelum user membalas bahwa mereka "Siap", "Mulai", atau bersedia.
        
        3. Setelah user menyatakan siap, baru kamu berikan Pertanyaan 1 (misalnya tentang perkenalan diri mereka atau ketertarikan di SE).
        
        4. Untuk pertanyaan-pertanyaan selanjutnya: berikan feedback singkat, beri nilai yang jujur dan tegas (skala 1-10), lalu berikan SATU pertanyaan berikutnya. Jangan borongan!
        
        Gunakan bahasa Indonesia yang profesional tapi santai layaknya Tech Lead di startup modern.
        """

        # 4. Buat chat session baru yang membawa history masa lalu
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=gemini_history,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.7
            )
        )

        # 5. Kirim pesan terbaru dan dapatkan balasan
        response = chat.send_message(user_message)
        
        # 6. Kembalikan jawaban ke React
        return {"reply": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Menjalankan server di port 5000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)