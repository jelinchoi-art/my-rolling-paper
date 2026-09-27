import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import os
import math
import random
import glob

# Streamlit 기본 설정
st.set_page_config(page_title="🍁 가을 감성 롤링페이퍼", layout="wide")

DATA_FILE = "messages.json"
TARGET_IMG = "target.jpg"  # 메인 얼굴/상체 이미지
PHOTOS_DIR = "photos"      # 단체 사진들이 들어가는 폴더
SECRET_CODE = "6969"       # 비밀번호

# 데이터 불러오기 / 저장 함수
def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_message(name, message):
    msgs = load_messages()
    msgs.append({"name": name, "message": message})
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)

# 폴라로이드 액자 스타일 사진 생성
def create_polaroid(img_path, size=650):
    try:
        raw_img = Image.open(img_path).convert("RGBA")
        raw_img = ImageOps.fit(raw_img, (size, int(size * 0.75)), Image.Resampling.LANCZOS)
        
        # 폴라로이드 바탕 액자 (흰 테두리 + 약간의 그림자 느김)
        frame_w, frame_h = size + 60, int(size * 0.75) + 120
        frame = Image.new('RGBA', (frame_w, frame_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)
        
        # 액자 배경 (따뜻한 흰색)
        draw.rounded_rectangle([0, 0, frame_w, frame_h], radius=20, fill=(255, 253, 248, 250), outline='#D5C4B1', width=3)
        
        # 사진 부착
        frame.paste(raw_img, (30, 30))
        return frame
    except Exception as e:
        return None

# A3 300 DPI 고해상도 롤링페이퍼 생성기
def generate_paper():
    # A3 (3508 x 4960 pixels)
    WIDTH, HEIGHT = 3508, 4960
    
    # 가을 느낌의 따뜻한 크림/메이플 톤 배경 바탕 (#FAF4E8)
    canvas = Image.new('RGB', (WIDTH, HEIGHT), color='#FAF4E8')
    draw = ImageDraw.Draw(canvas)
    center_x, center_y = WIDTH // 2, HEIGHT // 2

    # ----------------------------------------------------
    # 1. 배경 단체 사진 배치 (폴라로이드 감성 스타일)
    # ----------------------------------------------------
    group_photo_files = []
    if os.path.exists(PHOTOS_DIR):
        exts = ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.PNG')
        for ext in exts:
            group_photo_files.extend(glob.glob(os.path.join(PHOTOS_DIR, ext)))
    
    # 랜덤 시드 고정으로 메시지 추가시 사진 위치가 흔들리지 않게 고정
    random.seed(42)

    if group_photo_files:
        photo_count = len(group_photo_files)
        bg_radius_x, bg_radius_y = 1000, 1500
        
        for idx, p_path in enumerate(group_photo_files):
            pol_img = create_polaroid(p_path, size=700)
            if pol_img:
                angle = (2 * math.pi / photo_count) * idx + 0.3  # 약간 지그재그 배치
                px = center_x + int(bg_radius_x * math.cos(angle))
                py = center_y + int(bg_radius_y * math.sin(angle))
                
                # 자연스러운 기울임
                rot_deg = random.randint(-18, 18)
                rot_pol = pol_img.rotate(rot_deg, expand=True, resample=Image.Resampling.BICUBIC)
                
                canvas.paste(rot_pol, (px - rot_pol.width//2, py - rot_pol.height//2), rot_pol)

    # 시드 해제 (메시지 폰트/색상 난수 사용을 위함)
    random.seed()

    # ----------------------------------------------------
    # 2. 중앙 메인 프로필 사진 배치 (원형 액자)
    # ----------------------------------------------------
    if os.path.exists(TARGET_IMG):
        profile = Image.open(TARGET_IMG).convert("RGBA")
        size = 1100  # A3 크기에 맞춘 대형 프로필
        profile = ImageOps.fit(profile, (size, size), Image.Resampling.LANCZOS)
        
        # 원형 크롭 마스크
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        
        # 가을 테두리 선 추가
        draw.ellipse([center_x - size//2 - 15, center_y - size//2 - 15, 
                      center_x + size//2 + 15, center_y + size//2 + 15], 
                     outline='#C87D32', width=14)
        
        canvas.paste(profile, (center_x - size//2, center_y - size//2), mask)
    else:
        draw.ellipse([center_x-550, center_y-550, center_x+550, center_y+550], outline='#C87D32', width=14)

    # ----------------------------------------------------
    # 3. 수집된 메시지 카드 배치
    # ----------------------------------------------------
    messages = load_messages()
    if not messages:
        return canvas

    fonts = ["fonts/NanumPen.ttf", "fonts/NanumBarunPen.ttf", "fonts/SingleDay-Regular.ttf"]
    
    card_colors = [
        (255, 250, 240, 245),  # 따뜻한 아이보리
        (253, 242, 230, 245),  # 피치 베이지
        (245, 235, 220, 245),  # 샌드 베이지
        (255, 245, 230, 245)   # 은은한 앰버
    ]

    radius_x, radius_y = 1350, 1900
    total = len(messages)

    for i, msg in enumerate(messages):
        angle = (2 * math.pi / total) * i
        px = center_x + int(radius_x * math.cos(angle))
        py = center_y + int(radius_y * math.sin(angle))

        txt_content = f"{msg['message']}\n\n- {msg['name']} -"
        
        font_path = random.choice(fonts) if fonts else None
        try:
            font = ImageFont.truetype(font_path, 75)
        except:
            font = ImageFont.load_default()

        card_w, card_h = 820, 460
        card = Image.new('RGBA', (card_w, card_h), (255, 255, 255, 0))
        card_draw = ImageDraw.Draw(card)
        
        bg_color = random.choice(card_colors)
        card_draw.rounded_rectangle([0, 0, card_w - 20, card_h - 20], radius=35, fill=bg_color, outline='#D8C3A5', width=4)
        card_draw.text((40, 40), txt_content, font=font, fill='#3D312A')

        rotated_card = card.rotate(random.randint(-12, 12), expand=True, resample=Image.Resampling.BICUBIC)
        canvas.paste(rotated_card, (px - card_w//2, py - card_h//2), rotated_card)

    return canvas

# --- 웹 화면 UI ---
st.title("🍁 가을 감성 롤링페이퍼 남기기")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("✍️ 메시지 작성하기")
    with st.form("msg_form", clear_on_submit=True):
        name = st.text_input("작성자 이름")
        message = st.text_area("축하 메시지", height=180)
        secret_code = st.text_input("비밀번호", type="password", help="공유받으신 4자리 암호를 입력해주세요.")
        
        submitted = st.form_submit_button("롤링페이퍼에 추가하기")
        
        if submitted:
            if secret_code == SECRET_CODE:
                if name and message:
                    save_message(name, message)
                    st.success("🎉 메시지가 성공적으로 등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("이름과 메시지를 모두 입력해주세요.")
            else:
                st.error("🔒 비밀번호가 올바르지 않습니다.")

with col2:
    st.subheader("🖼️ 실시간 롤링페이퍼 현황 (A3 고해상도)")
    paper_img = generate_paper()
    
    st.image(paper_img, use_container_width=True)
    
    paper_img.save("rolling_paper_A3_300dpi.png", dpi=(300, 300))
    with open("rolling_paper_A3_300dpi.png", "rb") as file:
        st.download_button(
            label="🖨️ A3 고해상도 인쇄용 이미지 다운로드",
            data=file,
            file_name="rolling_paper_A3_300dpi.png",
            mime="image/png"
        )