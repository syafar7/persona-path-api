from inference import SkillGapAnalyzer

analyzer = SkillGapAnalyzer(
    tfidf_path='models/tfidf_vectorizer.pkl',
    tfidf_matrix_path='models/tfidf_matrix.pkl',
    df_path='models/df_processed.csv'
)

def test(role, skills, level, note):
    r = analyzer.predict(role, skills, level)
    score = r["match_score"]
    gap = r["skill_gap"]
    print(f"[{note}]")
    print(f"  Role={role} | Skills={skills} | Level={level}")
    print(f"  Score={score}% | Gap={gap}")
    print()

test('cybersecurity', 'pandas', 'entry', 'HARUSNYA 0%: pandas tidak relevan ke cybersecurity')
test('cybersecurity', 'html, css, react', 'entry', 'HARUSNYA 0%: web skills tidak relevan ke cybersecurity')
test('cybersecurity', 'linux, python', 'entry', 'HARUSNYA ADA SKOR: linux & python valid')
test('cybersecurity', 'kali linux', 'entry', 'HARUSNYA ADA SKOR: kali linux alias ke security skills')
test('data analyst', 'pandas', 'entry', 'HARUSNYA ~22%: pandas alias ke python+data visualization')
test('data analyst', 'pandas, sql', 'entry', 'HARUSNYA ~33%')
test('frontend developer', 'react', 'entry', 'HARUSNYA ADA SKOR: react alias ke javascript')
test('backend developer', 'django', 'entry', 'HARUSNYA ADA SKOR: django alias ke python')
test('backend developer', 'pandas', 'entry', 'HARUSNYA 0%: pandas bukan backend skill')
