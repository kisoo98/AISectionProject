from flask import Flask, request, render_template, session
import random
from dotenv import load_dotenv
import os
from openai import OpenAI

app = Flask(__name__)
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# 비밀키 설정 
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# 예시로 시나리오
preset_prompts = [
    "오래된 도시의 외곽, 무너져 내린 폐허 속에서 희미한 불빛이 반짝이고 있다.",
    "깊은 숲속에 이상한 빛이 반짝이고 있었습니다.",
    "무더운 여름날, 갑자기 하늘에서 거대한 배가 나타났습니다.",
    "어느 날, 정체를 알 수 없는 초대장이 도착한다.",
    "여행 중에 들른 작은 마을, 하지만 이상할 정도로 고요하다. 사람들은 어디론가 사라졌고, 남은 것은 엉망이 된 집들과 길거리에 남아있는 흔적들 뿐이다."
]

def generate_story(user_input):
    previous_story = session.get('story', '')
    
    prompt = random.choice(preset_prompts)
    
    messages = [
        {"role": "system", "content": "You are a creative storyteller."},
        {"role": "user", "content": f"{previous_story}\n{prompt}\n\n사용자의 입력: {user_input}\n\n이 이야기는 TRPG 형식입니다. 이야기의 끝에서 사용자가 할 수 있는 행동을 물어보세요. 예를 들어, '무엇을 할까요?'와 같은 질문을 덧붙여서 사용자가 선택할 수 있도록 유도하세요."}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        story = completion.choices[0].message.content.strip()
        
        session['story'] = previous_story + '\n' + story
        
        return story
    except Exception as e:
        return f"오류 발생: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    story = ""
    
    if request.method == "POST":
        if request.form.get("reset") == "true":
            # 세션 초기화 (이야기 초기화)
            session.pop('story', None)
            story = "이야기가 초기화되었습니다. 새로운 이야기를 시작하세요."
        else:
            user_input = request.form.get("user_input", "")
            story = generate_story(user_input)
    
    return render_template("index.html", story=story)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
