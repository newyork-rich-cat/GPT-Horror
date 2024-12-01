import pygame
import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pygame 초기화
pygame.init()

# 화면 설정 (크기 확대)
screen = pygame.display.set_mode((1280, 960))  # 화면 크기 확대
pygame.display.set_caption('공포 텍스트 어드벤처 게임')

# 시스템 폰트 설정 (한글을 지원하는 폰트 사용)
font = pygame.font.SysFont("malgungothic", 24)  # Windows에서 'malgungothic' 사용, 다른 시스템에서는 적절한 폰트로 변경

# 텍스트 출력 함수
def render_text(text, y_position):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (20, y_position + i * 30))

# 텍스트 자동 줄 바꿈 함수
def wrap_text(text, max_width):
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_surface = font.render(test_line, True, (255, 255, 255))
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line)
            current_line = word
    if current_line:
        wrapped_lines.append(current_line)
    return "\n".join(wrapped_lines)

# 초기 설정
def create_game():
    system_message = {
        "role": "system",
        "content": (
            "당신은 공포 텍스트 기반 어드벤처 게임의 게임 마스터입니다. "
            "각 응답은 이야기를 계속 진행시키며 플레이어에게 선택지를 제공합니다. "
            "선택지는 명확하고 숫자로 구분되어야 합니다. "
            "공포감을 극대화하기 위해 세부적인 묘사와 긴장감을 포함하세요."
        )
    }
    return [system_message]

def get_response(messages):
    """OpenAI API를 호출하여 응답을 가져옵니다."""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return completion.choices[0].message.content

def get_initial_scene(game_history):
    """초기 게임 상황을 GPT로부터 받아옵니다."""
    return get_response(game_history)

def get_next_scene(user_choice, game_history):
    """사용자 입력을 받아 다음 스토리를 생성합니다."""
    game_history.append({"role": "user", "content": user_choice})
    return get_response(game_history)

# 게임 시작
def main():
    # 게임 초기화
    game_history = create_game()

    # 초기 화면
    initial_scene = get_initial_scene(game_history)
    game_history.append({"role": "assistant", "content": initial_scene})

    running = True
    user_input = ""
    current_scene = initial_scene

    while running:
        screen.fill((0, 0, 0))  # 배경색 설정 (검정)
        
        # 제목 출력
        title_surface = font.render("🌌 공포 텍스트 어드벤처 게임 🌌", True, (255, 0, 0))
        screen.blit(title_surface, (450, 20))

        # 현재 장면 출력 (자동 줄 바꿈 적용)
        wrapped_text = wrap_text(current_scene, 1200)  # 최대 너비 1200으로 줄 바꿈
        render_text(wrapped_text, 100)

        # "당신의 선택" 텍스트를 화면 맨 아래로 출력
        option_y_position = 760  # 화면 크기 960에서 200 정도 여유를 둔 위치
        render_text("당신의 선택: " + user_input, option_y_position)

        pygame.display.flip()  # 화면 갱신

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Enter 키가 눌렸을 때 사용자 입력 처리
                    if user_input.lower() == "종료":
                        print("게임을 종료합니다. 감사합니다!")
                        running = False
                    else:
                        # 다음 장면 생성
                        try:
                            next_scene = get_next_scene(user_input, game_history)
                            game_history.append({"role": "assistant", "content": next_scene})
                            current_scene = next_scene
                            user_input = ""  # 입력 초기화
                        except Exception as e:
                            print(f"에러가 발생했습니다: {e}")
                            running = False
                elif event.key == pygame.K_BACKSPACE:
                    # 백스페이스 키로 입력 지우기
                    user_input = user_input[:-1]
                else:
                    # 다른 키 입력 처리
                    user_input += event.unicode

    pygame.quit()

if __name__ == "__main__":
    main()
