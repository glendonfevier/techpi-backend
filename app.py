import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

app = FastAPI()

# ⚙️ MENGATASI CORS ERROR - DIKUNCI BIAR VERCEL LU BISA MASUK
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
        if not req.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")

        # 1. Ambil pesan terakhir yang diketik user
        user_message = req.messages[-1].content
        
        # 2. Susun ulang history percakapan sebelumnya untuk dikirim ke Gemini
        gemini_history = []
        for msg in req.messages[:-1]:
            # Menyesuaikan role dari React ('assistant'/'model') ke format SDK Gemini
            gemini_role = "user" if msg.role == "user" else "model"
            gemini_history.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # 3. Setup System Instruction biar AI tetap konsisten jadi Tech Lead & GAK TYPO
        sys_instruction = """
        Kamu adalah TechPI AI, sebuah AI Interviewer/Tech Lead tetapi bisa membicarakan topik diluar itu yang dibuat oleh Glendon.
        Tugas utama kamu adalah mewawancarai user secara bertahap (satu per satu pertanyaan) untuk posisi Software Engineer.

        ATURAN ALUR PERCAKAPAN:
        1. Jika user BARU PERTAMA KALI menyapa (contoh: "Halo", "Hi", "P", dsb), kamu HANYA BOLEH merespons dengan kalimat perkenalan ini:
           "Halo! Gue TechPI AI yang dibuat oleh Glendon. Hari ini gue bakal jadi Tech Lead sekaligus interviewer lo untuk posisi Software Engineering. Di sini gue bakal ngasih beberapa pertanyaan secara bertahap. Setelah lo jawab, gue bakal kasih nilai (skala 1-10) dan feedback singkat sebelum masuk ke pertanyaan berikutnya. Gimana, udah siap buat mulai?"
           
        2. JANGAN PERNAH memberikan pertanyaan pertama sebelum user membalas bahwa mereka "Siap", "Mulai", atau bersedia.
        
        3. Setelah user menyatakan siap, baru kamu berikan Pertanyaan 1 (misalnya tentang perkenalan diri mereka atau ketertarikan di SE).
        
        4. Untuk pertanyaan-pertanyaan selanjutnya: berikan feedback singkat, beri nilai yang jujur dan tegas (skala 1-10), lalu berikan SATU pertanyaan berikutnya. Jangan borongan!
        
        Gunakan bahasa Indonesia yang profesional tapi santai layaknya Tech Lead di startup modern.
        ATURAN TAMBAHAN:
            - JANGAN PERNAH menyingkat kata atau membuat typo yang disengaja (Contoh salah: "Hlo", "Oe", "gpp", "jg").
            - Tetap gunakan ejaan kata yang jelas seperti "Halo" dan "Oke" namun dengan pembawaan yang santai menggunakan kata ganti "gue" dan "lo".
        """

        # 4. FIX UTAMA: Pisahkan pembuatan chat session berdasarkan ada/tidaknya history
        if gemini_history:
            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=gemini_history
            )
        else:
            # Kalau chat pertama kali (history kosong), buat chat kosong tanpa membawa parameter history
            chat = client.chats.create(
                model="gemini-2.5-flash"
            )

        # 5. Kirim pesan terbaru sambal menyuntikkan config yang benar
        response = chat.send_message(
            message=user_message,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.3  # <-- Biar anteng dan anti typo alay
            )
        )
        
        # 6. Kembalikan jawaban ke React Vercel dengan key "reply"
        return {"reply": response.text}

    except Exception as e:
        # Menampilkan log asli di console Render biar lu gampang ngecek
        print("ERROR ON BACKEND COK:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Menjalankan server FastAPI
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)