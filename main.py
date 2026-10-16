import time
from News_fetchar import get_new_articles, mark_as_seen
from ai_agent import analyze_and_summarize
from telegram_send import send_to_telegram

# وقت الفحص بالثواني 
CHECK_INTERVAL = 300 

def warm_up_database():
    """
    تشتغل مرة وحدة بس أول ما يشتغل البوت:
    تسجل الأخبار الموجودة حالياً بالداتابيس بدون إرسال، حتى البوت يراقب فقط الجديد اللي ينزل من هاللحظة وصاعداً.
    """
    print("🔄 sync the last artical save....")
    existing_articles = get_new_articles()
    for article in existing_articles:
        mark_as_seen(article["link"])
    print(f"✅ skipped of last artical done :{len(existing_articles)} the bot now ready for new fetch of artical....\n")

def check_for_new_drop():
    """تفحص إذا نزل خبر جديد خلال آخر 5 دقائق"""
    articles = get_new_articles()

    # إذا ما نزل شي جديد، يظل ساكت وما يسوي أي شي
    if not articles:
        return print("we dot`t have now artical!")

    for article in articles:
        try:
            print(f"🔔 we get new artical from: {article['title']}")
            
            # 1. الذكاء الاصطناعي يقرأ الخبر ويسوي ملخص الصديق
            analysis = analyze_and_summarize(article)

            # 2. إذا الخبر مهم، يدزه فوراً للتليجرام
            if analysis.is_worth_sending:
                
                send_to_telegram(analysis.friend_message)
            else:
                print("⏭️ is not important we skipped ")

            # 3. نقفل الخبر بالداتابيس حتى ما يتكرر أبد
            mark_as_seen(article["link"])

        except Exception as e:
            print(f"⚠️ worining!!: {e}")

if __name__ == "__main__":
    # 1. نصفر العداد أول ما نشغل السكربت
    warm_up_database()
    
    print("👀 the bot now in silent mode....")
    
    # 2. حلقة مستمرة تشتغل بالخلفية
    while True:
        check_for_new_drop()
        time.sleep(CHECK_INTERVAL)  # البوت ينام 5 دقائق كاملة بدون ما يصرف أي موارد