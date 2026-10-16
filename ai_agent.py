from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
# النتيجة اللي نريدها: قرار الإرسال + سالفة الصديق الصافية فقط
class NewsAnalysis(BaseModel):
    is_worth_sending: bool = Field(
        description="True فقط إذا كان الخبر مهماً وقوياً (نموذج ذكاء اصطناعي جديد، تقنية مهمة، هاردوير جديد من الشركات الكبرى). False للأخبار العادية."
    )
    friend_message: str = Field(
        description="ملخص الخبر باللهجة العراقية أو العربية البسيطة كأنك صديق تسولف لصديقك (مثلاً تبدأ بـ: ما سمعت؟ أو تدري اليوم...) تشرح شنو نزل وشنو فائدته وتأثيره، بدون أي عناوين رسمية أو روابط."
    )

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_and_summarize(article: dict) -> NewsAnalysis:
    prompt = f"""
    أقرأ هذا الخبر التقني. إذا كان مهماً، لخصه لي كأنك صديقي التقني وتسولف وياي ببساطة.
    لا تكتب عناوين رسمية ولا نقاط معقدة ولا تذكر المصدر أو الرابط.
    فقط احكيلي باختصار ولطافة: شنو اللي نزل اليوم؟ وشنو فائدته الحقيقية أو شلون راح يغير الشغل؟

    عنوان الخبر: {article['title']}
    تفاصيل الخبر: {article['summary']}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NewsAnalysis,
            temperature=0.4, # رفعناها شوية حتى يكون أسلوب الكلام طبيعي وحلو
        ),
    )

    return NewsAnalysis.model_validate_json(response.text)