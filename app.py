import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq  # Memanggil library Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Menyedot kunci Groq dari brankas .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MASTER_JOB_SKILLS = {
    "Data Scientist": ["Python", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "Statistics"],
    "Backend Developer": ["PHP", "MySQL", "Python", "Flask", "Laravel", "Git", "REST API"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Tailwind CSS", "Bootstrap"]
}

def get_ai_recommendation(target_role, missing_skills):
    if not missing_skills:
        return "Luar biasa! Kamu sudah memiliki fondasi skill dasar yang kuat untuk profesi ini. Pertahankan dan buat portofolio!"
    
    if not client:
        return "Sistem AI sedang disiapkan. Silakan mulai belajar dari YouTube atau dokumentasi resmi."

    skills_text = ", ".join(missing_skills)
    prompt = f"""
    Berperanlah sebagai mentor IT yang ramah. User sedang belajar untuk menjadi {target_role}, 
    namun saat ini belum menguasai skill berikut: {skills_text}. 
    Tolong berikan 3 langkah ringkas, praktis, dan memotivasi tentang cara mulai mempelajari skill tersebut. 
    Gunakan bahasa Indonesia yang santai tapi profesional. Jangan terlalu panjang.
    """

    try:
        # Menembak server Groq (Sangat Cepat & Stabil)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            # Menggunakan model Llama 3 yang super cepat dan gratis
            # Menggunakan model Llama 3.1 terbaru yang aktif di Groq
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        # Mengambil jawaban utuh (bukan streaming)
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"ERROR GROQ: {e}")
        return "Maaf, asisten AI sedang sibuk. Silakan pelajari skill yang kurang melalui dokumentasi resmi di internet."

@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    data = request.get_json()
    
    target_role = data.get('target_role', 'Data Scientist')
    user_skills_raw = data.get('user_skills', '')

    user_skills_list = [s.strip().lower() for s in user_skills_raw.split(',') if s.strip()]
    required_skills = MASTER_JOB_SKILLS.get(target_role, MASTER_JOB_SKILLS["Data Scientist"])

    skill_gap = []
    matched_count = 0

    for skill in required_skills:
        if skill.lower() in user_skills_list:
            matched_count += 1
        else:
            skill_gap.append(skill)

    total_required = len(required_skills)
    match_score = int((matched_count / total_required) * 100) if total_required > 0 else 0

    # Memanggil Groq
    ai_recommendation = get_ai_recommendation(target_role, skill_gap)

    response = {
        "status": "success",
        "pesan": "API berhasil diproses secara dinamis!",
        "target_role": target_role,
        "input_user": user_skills_raw,
        "match_score": match_score,
        "skill_gap": skill_gap,
        "ai_recommendation": ai_recommendation 
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)