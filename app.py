import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types

app = FastAPI()

# Setup CORS biar React Vercel bisa akses tanpa diblokir
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

# ==================== SCHEMA / MODEL DATA ====================

class MessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageModel]

class ATSRequest(BaseModel):
    job_description: str
    resume_text: str


# ==================== ENDPOINT 1: MOCK INTERVIEW CHAT ====================

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        if not req.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")

        user_message = req.messages[-1].content

        # Parsing history chat agar aman untuk SDK Gemini terbaru
        gemini_history = []
        for msg in req.messages[:-1]:
            gemini_role = "user" if msg.role == "user" else "model"
            gemini_history.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # Instruksi sistem — identitas Hireloop
        sys_instruction = """
        Kamu adalah Hireloop AI, sebuah AI Career Assistant & Tech Lead modern yang dibuat oleh Glendon.
        Aplikasi Hireloop ini memiliki dua fitur utama: "Mock Interview" dan "ATS Resume Fixer".

        ATURAN MERESPONS USER:
        1. Jika user menyapa atau ingin melakukan Simulasi Interview:
           - Berperanlah sebagai Tech Lead startup yang asyik (pake gue/lo).
           - Mulai dengan perkenalan yang keren, dan tunggu sampai user bilang "Siap" atau "Mulai" baru berikan Pertanyaan Pertama.
           - Berikan interview secara bertahap (satu per satu pertanyaan, kasih nilai skala 1-10 setiap user menjawab).
           - Setiap kali kamu memberi nilai, SELALU tulis dalam format persis: "Skor: X/10" di baris tersendiri, supaya bisa dideteksi sistem.

        2. Jika user bertanya tentang CV, LinkedIn, ATS, atau tips karier umum:
           - Jawablah sebagai HR Director / Career Mentor yang solutif dan membantu.
           - Berikan tips-tips taktis agar CV mereka menarik dan mudah lolos screening perusahaan.

        Gaya bahasa wajib menggunakan bahasa Indonesia yang santai layaknya di startup modern, sopan, dan solutif.
        Jangan pernah ketik "Hlo" atau "Oe", ketiklah "Halo" dan "Oke" dengan bener ya!
        """

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


# ==================== ENDPOINT 2: ATS RESUME FIXER ====================

@app.post("/optimize-ats")
async def optimize_ats_endpoint(req: ATSRequest):
    try:
        if not req.job_description or not req.resume_text:
            raise HTTPException(status_code=400, detail="Job description and Resume text cannot be empty")

        ats_prompt = f"""
        Kamu adalah seorang Professional Resume Writer dan HR Director senior. Tugas kamu adalah mengoptimalkan CV/Resume user agar lolos dari sistem penyaringan otomatis ATS (Applicant Tracking System) berdasarkan Lowongan Kerja (Job Description) yang dituju.

        LOWONGAN KERJA (JOB DESCRIPTION):
        \"\"\"{req.job_description}\"\"\"

        CV / RESUME USER SAAT INI:
        \"\"\"{req.resume_text}\"\"\"

        Analisislah kedua teks di atas, lalu berikan output dalam format Markdown yang rapi dengan struktur berikut:

        ### 🎯 1. ATS Match Score & Analisis Singkat
        Berikan prediksi skor kelulusan ATS dari skala 0-100% berdasarkan CV saat ini (tulis dalam format persis "Skor ATS: X%" di baris pertama agar bisa dideteksi sistem). Jelaskan secara singkat kata kunci (keywords) apa saja yang kurang atau hilang di CV user.

        ### 📝 2. Hasil Optimasi "Professional Summary"
        Tuliskan ulang bagian ringkasan profil (Summary) CV user agar terlihat sangat relevan dengan lowongan kerja di atas. Gunakan bahasa Inggris (atau sesuaikan dengan bahasa lowongan kerja tersebut). Buat agar kuat, profesional, dan kaya akan kata kunci ATS.

        ### 💼 3. Tips Penyesuaian Pengalaman Kerja (Job Experience)
        Berikan 3-4 poin bullet points berisi rekomendasi aksi nyata atau kalimat pencapaian (achievement) yang wajib user masukkan ke dalam deskripsi pengalaman kerja mereka agar auto-lolos screening.

        Berikan respons dengan gaya bicara yang suportif, solutif, dan profesional, tapi tetap santai (pake gue/lo jika memberikan pengantar singkat).
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=ats_prompt,
            config=types.GenerateContentConfig(
                temperature=0.4
            )
        )

        return {"result": response.text}

    except Exception as e:
        print("ERROR ON ATS COK:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RUN SERVER (WAJIB PALING BAWAH) ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
