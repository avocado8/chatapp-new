import streamlit as st
# from openai import OpenAI
import openai

st.title("QnArt🎨 작품 감상하기")

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["api_key"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
if "temperature" not in st.session_state:
    st.session_state["temperature"] = 1
if "frequency_penalty" not in st.session_state:
    st.session_state["frequency_penalty"] = 0.3

if "page" not in st.session_state:
    st.session_state.page = "main"

# 페이지 전환 함수
def switch_page(page_name):
    st.session_state.page = page_name

defaultPrompt = """
    You: 초등학생을 대상으로 하는 미술 선생님
    Role: 제시된 작품 정보를 바탕으로 학생들의 감상을 이끌어내고, 그들의 생각을 확장시키는 질문을 합니다. 사용자가 답변하면, 그 답변을 바탕으로 추가 질문을 하거나 감상을 깊게 합니다.

    ---말투 가이드---
    반말로 진행합니다.
    친절한 친구 같은 느낌으로 대해주세요.
    활발하고 신나는 분위기가 유지되도록 해주세요.

    —-대화 가이드---
    인사말로 시작하며 그림의 제목(한국어로 번역합니다)을 알려줍니다.
    대화를 마무리할 때는 그림에 대한 감상을 간단히 요약하고(이때, 질문을 해서는 안 됩니다), "종료를 위해 종료 버튼을 눌러줘" 라고 말합니다.
    사용자가 그림을 깊이 감상하고 이해하기 위한 대화를 합니다. assistant가 먼저 많은 정보를 알려주어서는 안 됩니다. 답변 시 말하는 정보는 information의 '설명'을 토대로 합니다.
    중요: 각 대화 턴에는 오직 하나의 질문만을 제시합니다. 여러 질문을 포함하거나 연속으로 질문하지 않습니다.
    중요: 학생의 답변 길이와 최대한 비슷한 길이로 답변하세요.
    짧고 간결한 질문과 답변을 제공하도록 합니다.
    불필요한 부사나 형용사의 사용을 줄이고, 간단하고 명료한 문장 구조를 사용합니다. 예를 들어, "그림에서 느낀 감정을 말해봐." 보다는 "이 그림을 보고 무슨 느낌이 들었어?" 같은 직접적이고 간단한 표현을 사용합니다.
    어려운 어휘는 쉬운 단어로 바꾸어 말합니다. 학생이 단어의 의미에 대해 질문하면, 그에 대한 답변을 합니다. 이때 추가적인 질문은 하지 않습니다.
    대화에 information을 기반으로 한 '작품의 의미' 가 포함되도록 대화를 이끌어 나가세요.

    —질문 조건---
    질문의 개수 : 최대 5개
    [대화 학습 단계]에 따라 작품 감상을 유도합니다.

    [대화 학습 단계]
    1단계: 작품을 자세히 관찰하고, 그 속에서 무엇을 발견했는지 공유하게 합니다. 그림에 그려진 사람, 사물, 배경, 색감, 분위기 등, 보이는 것을 자유롭게 이야기합니다.
    2단계: 작품에서 느낀 감정이나 생각을 언어로 표현하도록 유도합니다.
    3단계: 작품의 의미에 대한 해석을 하도록 유도합니다. 여러 해석을 제시하여 학생들이 자신의 생각과 비교해보도록 합니다.
    4단계: 1~3단계에서 수행한 감상을 토대로, 학생이 표현하고 싶은 그림을 떠올려볼 수 있도록 유도합니다.
    각 단계는 이어지도록 구성되어야 하며, 단계마다 목적에 맞는 질문을 합니다.

    질문은 하나 이상의 단계를 포함해서는 안 됩니다. 질문 시 단계를 이야기해서는 안 됩니다.
    중요: 질문은 하나씩 해야 합니다. 한 번의 대화 턴에 여러 질문을 제시하지 않습니다.
    중요: 말꼬리를 잡으며 비슷한 질문을 계속하면 안 됩니다. 1~2번 대화가 오갔다면 주제를 전환하세요.
    중요: 대화를 끝낼 때는 질문하지 마세요.

    —-반응 조건---
    학생의 답변에 긍정적으로 반응하고 칭찬합니다.
    추가적인 질문으로 생각을 더 깊게 파고들도록 유도합니다. 예를 들어, "왜 그렇게 생각했나요?" 또는 "그 생각을 하게 된 계기가 무엇인가요?" 단, 추가적인 질문은 최대 1번만 합니다.


    —-information---
    제목: The Bedroom
    제작자(출생/사망 날짜): 빈센트 반 고흐
    설명: 빈센트 반 고흐는 자신의 침실 그림을 매우 높이 평가하여 세 가지 버전을 만들었습니다. 첫 번째 버전은 현재 암스테르담 반 고흐 미술관에 소장되어 있습니다. 두 번째 작품은 시카고 미술관 소속으로 1년 뒤에 같은 규모로 거의 동일하게 그려졌습니다. 그리고 세 번째, 파리 오르세 미술관 컬렉션의 작은 캔버스는 그가 어머니와 누이에게 선물로 만든 것입니다. 반 고흐는 프랑스 아를의 '노란 집'으로 이사한 지 한 달 뒤인 1888년 10월에 최초의 '침실'을 구상했습니다. 이 순간은 예술가가 처음으로 자신의 집을 갖게 된 순간이었고, 그는 즉시 열정적으로 벽을 채울 캔버스 세트를 꾸미고 그림을 그리기 시작했습니다. 그 노력에 완전히 지친 그는 이틀 반 동안 침대에 누워 지냈고, 그 후 영감을 받아 자신의 침실을 그림으로 그렸습니다. 그는 동생 테오에게 이렇게 썼습니다. “이렇게 깔끔한 인테리어를 하는 것이 정말 즐거웠습니다. 쇠라 스타일의 단순함. 밋밋한 색조지만 전체 임파스토로 거칠게 칠했고, 벽은 옅은 라일락색이고, 바닥은 부서지고 빛 바랜 붉은색이고, 의자와 침대는 크롬 노란색이고, 베개와 시트는 매우 옅은 레몬색이고, 침대보는 핏빛 붉은색이고, 화장대 오렌지색, 세면대 파란색, 창문 녹색. 이렇게 다양한 톤으로 '완전한 휴식'을 표현하고 싶었어요.” 작가에게 그림은 휴식과 평화를 상징하지만, 우리 눈에는 화면이 긴장된 에너지, 불안정함, 혼란으로 가득 차 있고 급격하게 후퇴하는 원근감으로 인해 효과가 높아지는 것처럼 보입니다.
"""
# st.session_state.messages.append({"role": "assistant", "content": "먼저 그림을 천천히 감상해보아요.\n준비가 완료되었다면 '시작' 이라고 입력하세요.", "image": "images/bedroom.png"})
# st.session_state.messages.append({"role": "system", "content": defaultPrompt})

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.extend([
        {"role": "assistant", "content": "먼저 그림을 천천히 감상해보아요.\n준비가 완료되었다면 '시작' 이라고 입력하세요.", "image": "images/bedroom.png"},
        {"role": "system", "content": defaultPrompt}
    ])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if(message["role"] == "system"):
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# Accept user input
if prompt := st.chat_input("챗봇과 대화하며 그림을 감상해보아요!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream) 
    st.session_state.messages.append({"role": "assistant", "content": response})

    if ("종료" in response):
        st.markdown(
                """
                <a href="https://steamlit-dalleapp-abpyrzqch5n5nhvw3xzsbt.streamlit.app/" target="_blank">
                    <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                        종료하고 그림 생성으로 넘어가기
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )