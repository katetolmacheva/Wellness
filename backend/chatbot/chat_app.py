from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

import base64
import hashlib
import json
import os
import re
import textwrap
import uuid
from io import BytesIO
from typing import List, Literal, Optional

import fitz  # PyMuPDF
import uvicorn

load_dotenv()

app = FastAPI()

# Разрешаем запросы с фронта (Next.js)
cors_raw = os.environ.get("CHAT_CORS_ORIGINS", "*").strip()
cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()] if cors_raw else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- CLIENTS ---------

GROQ_API_KEY = (os.environ.get("GROQ_API_KEY") or "").strip()
GROQ_CHAT_MODEL = (os.environ.get("GROQ_CHAT_MODEL") or "groq/compound").strip()
GROQ_TITLE_MODEL = (os.environ.get("GROQ_TITLE_MODEL") or GROQ_CHAT_MODEL).strip()
GROQ_MODERATION_MODEL = (os.environ.get("GROQ_MODERATION_MODEL") or GROQ_CHAT_MODEL).strip()

# Клиенты инициализируем только если ключ задан, чтобы сервис мог стартовать
# (в dev/preview окружениях ключ может быть не задан).
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
vision_client = (
    OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    if GROQ_API_KEY
    else None
)

# --------- SYSTEM PROMPT FOR CHAT ---------

SYSTEM_PROMPT = r"""
СИСТЕМНЫЙ ПРОМПТ
CONTEXT (Контекст и роль)
Вы — wellness-ассистент на платформе с проверенной информацией о здоровом образе
жизни от сертифицированных врачей и экспертов. Ваша задача — помогать
пользователям с общими вопросами о wellness, ЗОЖ и профилактике на основе научно
обоснованной информации.

КРИТИЧЕСКИЕ ОГРАНИЧЕНИЯ
ВЫ НЕ ЯВЛЯЕТЕСЬ врачом, психологом или медицинским специалистом. Вы НЕ
предоставляете медицинские консультации, НЕ ставите диагнозы, НЕ интерпретируете
симптомы, НЕ назначаете лечение или лекарства, НЕ отменяете и НЕ корректируете
назначения врачей. Если вы не уверены в информации, отвечайте "Я не знаю точно" и
рекомендуйте проконсультироваться со специалистом.

ПРОТОКОЛЫ ЭКСТРЕННЫХ СИТУАЦИЙ (ОБЯЗАТЕЛЬНО К ИСПОЛНЕНИЮ)
При обнаружении следующих признаков НЕМЕДЛЕННО прекратите обычное
взаимодействие и выведите экстренное сообщение:
КРАСНЫЕ ФЛАГИ:
- Упоминание суицидальных мыслей, желания причинить себе вред или самоповреждения
- Острая боль в груди, затруднённое дыхание
- Признаки инсульта (внезапная слабость лица/конечностей, нарушение речи, головокружение)
- Признаки инфаркта (давящая боль в груди, отдающая в руку/челюсть)
- Тяжёлая травма или кровотечение
- Острые психотические состояния

ЭКСТРЕННОЕ СООБЩЕНИЕ:
"То, что вы описываете, требует немедленной медицинской помощи. Пожалуйста, позвоните 112 или 103 (скорая помощь) прямо сейчас. Если вы испытываете мысли о самоповреждении, позвоните на телефон доверия 8-800-2000-122 (бесплатно, круглосуточно)."

МЕДИЦИНСКИЕ ТРИГГЕРЫ ДЛЯ ПЕРЕНАПРАВЛЕНИЯ К ВРАЧУ
Если пользователь упоминает любое из следующего, вы ОБЯЗАНЫ мягко, но явно
рекомендовать консультацию с врачом:
- Конкретные симптомы: боль любой локализации, температура, высыпания, кашель, головокружение, тошнота и т.д.
- Диагнозы или заболевания любого типа
- Вопросы о лекарствах, БАДах, дозировках, совместимости препаратов
- Беременность, планирование беременности, грудное вскармливание
- Здоровье детей и подростков до 18 лет
- Острые состояния
- Психические расстройства, тревожность, депрессия, панические атаки
- Хронические проблемы со сном более 2-3 недель
- Резкие изменения веса, аппетита или самочувствия

ФОРМАТ ОТВЕТА ПРИ МЕДИЦИНСКИХ ТРИГГЕРАХ:
1. Выразите понимание и эмпатию
2. Дайте ОБЯЗАТЕЛЬНЫЙ дисклеймер: "Это не медицинская консультация. То, что вы описываете, требует консультации с врачом [указать специализацию, если очевидна]."
3. Можете добавить 2-3 общих wellness-совета, НО подчеркните: "Эти рекомендации не заменяют профессиональную диагностику."
4. Предложите помощь в подготовке вопросов к приёму

РАЗРЕШЁННЫЕ ТЕМЫ (WELLNESS-ЗОНА)
Питание, физическая активность (ВОЗ 150–300 минут умеренной активности в неделю), сон и восстановление, стресс-менеджмент, превентивные практики.

ТРЕБОВАНИЯ К ИСТОЧНИКАМ И ФАКТЧЕКИНГУ
Только научно обоснованная информация (ВОЗ, Минздрав РФ, клин. руководства, рецензируемые журналы). Избегать псевдонауки.

ОБЯЗАТЕЛЬНЫЕ ДИСКЛЕЙМЕРЫ
"Это не медицинская консультация. При наличии симптомов или вопросов о своём здоровье обратитесь к врачу."
Повторять каждые 3-4 обмена в длинных диалогах.

OUTPUT (Формат ответа)
1. Краткое признание запроса (1 предложение)
2. Основная информация (2-4 абзаца)
3. Практические рекомендации (3-5 пунктов)
4. Дисклеймер (если применимо)
5. 1 уточняющий вопрос (опционально)

TONE
Дружелюбный, поддерживающий, эмпатичный, но профессиональный. Без категоричности.
""".strip()

# --------- CHAT HELPERS ---------


def extract_sources(executed_tools):
    if not executed_tools:
        return []
    tool = executed_tools[0]
    raw_results = getattr(tool, "search_results", None)
    if not raw_results:
        return []
    out = []
    for item in raw_results:
        title = getattr(item, "title", None)
        url = getattr(item, "url", None)
        if title and url:
            out.append({"title": title, "url": url})
    return out


Role = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str = Field(min_length=1)


class ChatIn(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1)


MAX_HISTORY_MESSAGES = 5
MAX_MESSAGE_CHARS = 1800
MAX_TOTAL_CHARS = 7000

MAX_HISTORY_MESSAGES = int(os.environ.get("CHAT_MAX_HISTORY_MESSAGES", "5"))
MAX_MESSAGE_CHARS = int(os.environ.get("CHAT_MAX_MESSAGE_CHARS", "1200"))
MAX_TOTAL_CHARS = int(os.environ.get("CHAT_MAX_TOTAL_CHARS", "4500"))

MAX_TITLE_INPUT_CHARS = int(os.environ.get("CHAT_MAX_TITLE_INPUT_CHARS", "700"))
MAX_CHAT_OUTPUT_TOKENS = int(os.environ.get("CHAT_MAX_OUTPUT_TOKENS", "800"))
MAX_TITLE_OUTPUT_TOKENS = int(os.environ.get("CHAT_TITLE_OUTPUT_TOKENS", "20"))


def compact_chat_history(history: List[ChatMessage]) -> List[ChatMessage]:
    recent = history[-MAX_HISTORY_MESSAGES:]
    trimmed: List[ChatMessage] = []
    total = 0

    # Идем с конца, чтобы сохранить самые свежие реплики.
    for msg in reversed(recent):
        content = msg.content.strip()
        if not content:
            continue

        if len(content) > MAX_MESSAGE_CHARS:
            content = content[:MAX_MESSAGE_CHARS]

        if total + len(content) > MAX_TOTAL_CHARS:
            remaining = MAX_TOTAL_CHARS - total
            if remaining <= 0:
                break
            content = content[:remaining]

        trimmed.append(ChatMessage(role=msg.role, content=content))
        total += len(content)

        if total >= MAX_TOTAL_CHARS:
            break

    return list(reversed(trimmed))


def ask_groq_structured(history: List[ChatMessage]) -> dict:
    if not client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY не задан")
    history = compact_chat_history(history)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]

    try:
        resp = client.chat.completions.create(
            model=GROQ_CHAT_MODEL,
            messages=messages,
            max_tokens=MAX_CHAT_OUTPUT_TOKENS,
            temperature=0.4,
        )
    except Exception as e:
        # Groq SDK кидает исключения при 4xx/5xx. Возвращаем корректный статус.
        print("Groq chat error:", repr(e))
        status_code = getattr(e, "status_code", None)
        error_text = str(e)
        if status_code == 413 or "413" in error_text or "request_too_large" in error_text:
            raise HTTPException(
                status_code=413,
                detail="Слишком длинный запрос к ИИ. Сократите текст сообщения и попробуйте снова.",
            )
        raise HTTPException(status_code=502, detail=f"Ошибка Groq API: {str(e)}")

    msg = resp.choices[0].message
    answer = (msg.content or "").strip()

    reasoning = getattr(msg, "reasoning", None)
    if reasoning:
        reasoning = textwrap.shorten(reasoning, width=350, placeholder=" ...")

    sources = extract_sources(getattr(msg, "executed_tools", None))

    return {"answer": answer, "reasoning": reasoning, "sources": sources}


@app.post("/chat")
def chat(body: ChatIn):
    return ask_groq_structured(body.messages)


# ---------- ГЕНЕРАЦИЯ НАЗВАНИЯ ЧАТА ----------

class TitleIn(BaseModel):
    text: str = Field(min_length=1)


@app.post("/generate-title")
def generate_title(body: TitleIn):
    if not client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY не задан")

    title_system = (
        "Ты генерируешь очень короткие названия чатов на русском. "
        "Дай заголовок 1–2 слова, без кавычек, без точки в конце. "
        "Он должен отражать тему, а не копировать текст дословно."
    )

    text = body.text.strip()
    if len(text) > MAX_TITLE_INPUT_CHARS:
        text = text[:MAX_TITLE_INPUT_CHARS].rstrip()

    try:
        resp = client.chat.completions.create(
            model=GROQ_TITLE_MODEL,
            messages=[
                {"role": "system", "content": title_system},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            max_tokens=MAX_TITLE_OUTPUT_TOKENS,
        )
    except Exception as e:
        print("Groq title error:", repr(e))
        status_code = getattr(e, "status_code", None)
        error_text = str(e)

        if status_code == 413 or "413" in error_text or "request_too_large" in error_text:
            fallback = text.split("\n")[0][:18].strip()
            return {"title": fallback or "Новый чат"}

        raise HTTPException(status_code=502, detail=f"Ошибка Groq API: {str(e)}")

    title = (resp.choices[0].message.content or "").strip()
    title = title.strip('*"“”«» .')

    if len(title) > 18:
        title = title[:18].rstrip()

    return {"title": title or "Новый чат"}


# ---------- МОДЕРАЦИЯ СТАТЕЙ ----------

ArticleModerationDecision = Literal["approved", "rejected"]


class ArticleModerationIn(BaseModel):
    title: str = Field(min_length=3)
    category: str = Field(min_length=2)
    annotation: str = Field(min_length=10)
    content_text: str = Field(min_length=50)


class ArticleModerationResult(BaseModel):
    decision: ArticleModerationDecision
    confidence_score: int
    reasons: List[str] = []
    red_flags: List[str] = []
    health_topic_match: bool
    topic_relevance: bool
    is_safe_content: bool


ARTICLE_MODERATION_PROMPT = """
Ты — строгая система премодерации статей для wellness-платформы.

Твоя задача: решить, можно ли публиковать статью.

ПРАВИЛА МОДЕРАЦИИ:
1) Статья должна быть по теме здоровья / wellness / ЗОЖ.
2) Статья должна соответствовать заявленной категории и теме.
3) Контент должен быть безопасным: без провокаций, оскорблений, разжигания ненависти,
   призывов к насилию, саморазрушению, опасным практикам и другим вредным материалам.
4) Не допускать псевдонаучные, заведомо вредные или опасные рекомендации.
5) Если есть сомнения — отклоняй (decision = "rejected").

ВЕРНИ СТРОГО JSON и ничего больше.
Формат:
{
  "decision": "approved | rejected",
  "confidence_score": 0,
  "reasons": ["..."],
  "red_flags": ["..."],
  "health_topic_match": true,
  "topic_relevance": true,
  "is_safe_content": true
}
""".strip()


def harden_article_decision(data: ArticleModerationResult) -> ArticleModerationResult:
    is_confident = data.confidence_score >= 80
    is_clean = len(data.red_flags) == 0
    must_approve = (
        data.health_topic_match
        and data.topic_relevance
        and data.is_safe_content
        and is_confident
        and is_clean
    )
    data.decision = "approved" if must_approve else "rejected"
    return data


@app.post("/article/moderate")
def moderate_article(body: ArticleModerationIn):
    if not client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY не задан")
    user_text = (
        f"{ARTICLE_MODERATION_PROMPT}\n\n"
        f"НАЗВАНИЕ:\n{body.title.strip()}\n\n"
        f"КАТЕГОРИЯ:\n{body.category.strip()}\n\n"
        f"АННОТАЦИЯ:\n{body.annotation.strip()}\n\n"
        f"ТЕКСТ СТАТЬИ:\n{body.content_text.strip()[:20000]}"
    )

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODERATION_MODEL,
            messages=[{"role": "user", "content": user_text}],
            temperature=0.1,
        )
    except Exception as e:
        print("Groq moderation error:", repr(e))
        raise HTTPException(status_code=502, detail=f"Ошибка Groq API: {str(e)}")

    raw_text = (resp.choices[0].message.content or "").strip()
    json_text = clean_json_text(raw_text)

    try:
        parsed = json.loads(json_text)
        result = ArticleModerationResult(**parsed)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Модель вернула невалидный ответ модерации: {str(e)}",
        )

    hardened = harden_article_decision(result)
    return hardened.model_dump()


# ---------- ВЕРИФИКАЦИЯ ЭКСПЕРТА ----------

UPLOAD_DIR = "uploads/expert_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


VerificationDecision = Literal["approved", "rejected"]


class DiplomaAnalysis(BaseModel):
    document_type: str
    is_realistic_official_document: bool
    matches_selected_education: bool
    confidence_score: int

    full_name: Optional[str] = None
    institution: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    graduation_year: Optional[str] = None
    document_number: Optional[str] = None

    red_flags: List[str] = []
    reasons: List[str] = []

    decision: VerificationDecision


EXPERT_VERIFICATION_PROMPT = """
Ты система очень строгой автоматической верификации экспертов для wellness-платформы.

Твоя задача — проверить, является ли загруженный документ реальным официальным
документом об образовании, и совпадает ли он с описанием образования,
которое указал пользователь.

КРИТИЧЕСКИЕ ПРАВИЛА:
1. Проверяй МАКСИМАЛЬНО СТРОГО.
2. Ничего не додумывай.
3. Если есть хоть малейшие сомнения — decision = "rejected".
4. "approved" ставь только если:
   - документ похож на официальный документ об образовании;
   - ключевые данные читаемы;
   - найдено ФИО;
   - найдено учебное заведение;
   - найдена специальность или квалификация;
   - описание образования пользователя совпадает с документом;
   - нет признаков подделки;
   - confidence_score очень высокий.
5. Если документ не выглядит официальным, плохо читается, обрезан,
   имеет следы редактирования, содержит противоречия или не совпадает
   с описанием образования — rejected.

ЧТО НУЖНО ПРОВЕРИТЬ:
- тип документа;
- похож ли он на официальный документ;
- совпадает ли с описанием пользователя;
- ФИО;
- учебное заведение;
- квалификация;
- специальность;
- год окончания / выдачи;
- номер документа;
- признаки подделки;
- признаки низкого качества;
- итоговое решение.

Считай красными флагами:
- отсутствуют ключевые поля;
- документ сильно размыт;
- обрезаны края / печати / важные поля;
- странная верстка или шрифты;
- похоже на редактирование или монтаж;
- текст противоречив;
- это не диплом / не удостоверение / не официальный документ об образовании;
- описание пользователя не совпадает с документом.

Верни СТРОГО JSON и ничего больше.
Формат JSON:
{
  "document_type": "diploma | certificate | unknown | other",
  "is_realistic_official_document": true,
  "matches_selected_education": true,
  "confidence_score": 95,
  "full_name": "строка или null",
  "institution": "строка или null",
  "qualification": "строка или null",
  "specialization": "строка или null",
  "graduation_year": "строка или null",
  "document_number": "строка или null",
  "red_flags": ["...", "..."],
  "reasons": ["...", "..."],
  "decision": "approved | rejected"
}
""".strip()


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save_uploaded_file(file_bytes: bytes, original_name: str) -> str:
    ext = os.path.splitext(original_name or "")[1].lower()
    safe_name = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    return save_path


def file_to_data_url(file_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def pdf_to_png_data_urls(pdf_bytes: bytes, max_pages: int = 3) -> List[str]:
    """
    Рендерим первые страницы PDF в PNG и отправляем их как изображения в vision-модель.
    Для диплома обычно хватает 1-2 страниц.
    """
    data_urls: List[str] = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_count = min(len(doc), max_pages)

    for i in range(pages_count):
        page = doc.load_page(i)

        # Увеличиваем масштаб для лучшей читаемости текста
        matrix = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        png_bytes = pix.tobytes("png")
        data_urls.append(file_to_data_url(png_bytes, "image/png"))

    return data_urls


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Пытаемся дополнительно вытащить текст из PDF.
    Это не основная проверка, но помогает модели.
    """
    text_parts: List[str] = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        txt = page.get_text("text")
        if txt:
            text_parts.append(txt)

    text = "\n".join(text_parts).strip()
    return text[:15000]  # не раздуваем запрос


def clean_json_text(raw_text: str) -> str:
    raw_text = raw_text.strip()

    # Убираем ```json ... ```
    raw_text = re.sub(r"^```json\s*", "", raw_text, flags=re.IGNORECASE)
    raw_text = re.sub(r"^```\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    # Если модель вернула лишний текст, пытаемся вытащить JSON-объект
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw_text = raw_text[start:end + 1]

    return raw_text.strip()


def extract_response_text(response) -> str:
    direct = (getattr(response, "output_text", None) or "").strip()
    if direct:
        return direct

    output = getattr(response, "output", None) or []
    chunks: List[str] = []
    for item in output:
        contents = getattr(item, "content", None) or []
        for c in contents:
            text = getattr(c, "text", None)
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())

    return "\n".join(chunks).strip()


def harden_decision(data: DiplomaAnalysis) -> DiplomaAnalysis:
    """
    Дополнительная серверная страховка.
    Даже если модель сказала approved, мы перепроверяем.
    """
    must_have = all([
        data.is_realistic_official_document,
        data.matches_selected_education,
        bool(data.full_name),
        bool(data.institution),
        bool(data.specialization or data.qualification),
        data.confidence_score >= 90,
        len(data.red_flags) == 0,
    ])

    data.decision = "approved" if must_have else "rejected"
    return data


def normalize_person_name(value: Optional[str]) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().lower().replace("ё", "е"))


def names_match(expected_first: str, expected_last: str, detected_full_name: Optional[str]) -> bool:
    expected_first_n = normalize_person_name(expected_first)
    expected_last_n = normalize_person_name(expected_last)
    detected_n = normalize_person_name(detected_full_name)

    if not expected_first_n or not expected_last_n or not detected_n:
        return False

    return expected_first_n in detected_n and expected_last_n in detected_n


def build_verification_input(
    education_description: str,
    expected_first_name: str,
    expected_last_name: str,
    extracted_text: str,
    image_data_urls: List[str],
):
    content = [
        {
            "type": "input_text",
            "text": (
                f"{EXPERT_VERIFICATION_PROMPT}\n\n"
                f"ОЖИДАЕМОЕ ФИО ПОЛЬЗОВАТЕЛЯ:\n"
                f"Имя: {expected_first_name.strip()}\n"
                f"Фамилия: {expected_last_name.strip()}\n"
                f"Это ФИО ОБЯЗАТЕЛЬНО должно совпадать с ФИО в документе. "
                f"Если ФИО не совпадает — decision = rejected.\n\n"
                f"ОПИСАНИЕ ОБРАЗОВАНИЯ ОТ ПОЛЬЗОВАТЕЛЯ:\n"
                f"{education_description.strip()}\n\n"
                f"ИЗВЛЕЧЕННЫЙ ТЕКСТ ДОКУМЕНТА (если удалось извлечь):\n"
                f"{extracted_text if extracted_text else '[не извлечён]'}"
            ),
        }
    ]

    for data_url in image_data_urls:
        content.append(
            {
                "type": "input_image",
                "detail": "high",
                "image_url": data_url,
            }
        )

    return [
        {
            "role": "user",
            "content": content,
        }
    ]


def call_vision_verification(
    education_description: str,
    expected_first_name: str,
    expected_last_name: str,
    extracted_text: str,
    image_data_urls: List[str],
) -> DiplomaAnalysis:
    if not vision_client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY не задан")
    input_payload = build_verification_input(
        education_description=education_description,
        expected_first_name=expected_first_name,
        expected_last_name=expected_last_name,
        extracted_text=extracted_text,
        image_data_urls=image_data_urls,
    )

    response = vision_client.responses.create(
        model=VISION_MODEL,
        input=input_payload,
    )

    raw_text = extract_response_text(response)
    if not raw_text:
        raise HTTPException(
            status_code=502,
            detail="Модель не вернула распознаваемый текст при проверке диплома",
        )
    json_text = clean_json_text(raw_text)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Модель вернула невалидный JSON при проверке диплома: {str(e)}",
        )

    try:
        analysis = DiplomaAnalysis(**data)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Не удалось провалидировать ответ модели: {str(e)}",
        )

    analysis = harden_decision(analysis)

    if not names_match(expected_first_name, expected_last_name, analysis.full_name):
        analysis.decision = "rejected"
        if "ФИО в документе не совпадает с ФИО профиля" not in analysis.red_flags:
            analysis.red_flags.append("ФИО в документе не совпадает с ФИО профиля")
        if "Имя и фамилия документа должны совпадать с данными аккаунта" not in analysis.reasons:
            analysis.reasons.append("Имя и фамилия документа должны совпадать с данными аккаунта")

    return analysis


@app.post("/expert/verify")
async def verify_expert(
    education_description: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    file: UploadFile = File(...),
):
    education_description = education_description.strip()
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not education_description:
        raise HTTPException(status_code=400, detail="Нужно указать образование")
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="Нужно передать имя и фамилию профиля")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только PDF, JPG и PNG",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Файл пустой")

    # Ограничение на слишком большие файлы
    max_size_mb = 10
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимум {max_size_mb} МБ",
        )

    save_path = save_uploaded_file(file_bytes, file.filename or "document")
    file_hash = sha256_of_bytes(file_bytes)

    extracted_text = ""
    image_data_urls: List[str] = []

    try:
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_bytes)
            image_data_urls = pdf_to_png_data_urls(file_bytes, max_pages=3)
        else:
            image_data_urls = [file_to_data_url(file_bytes, file.content_type)]

        if not image_data_urls:
            raise HTTPException(
                status_code=400,
                detail="Не удалось подготовить документ для проверки",
            )

        analysis = call_vision_verification(
            education_description=education_description,
            expected_first_name=first_name,
            expected_last_name=last_name,
            extracted_text=extracted_text,
            image_data_urls=image_data_urls,
        )

        return {
            "status": analysis.decision,
            "verified": analysis.decision == "approved",
            "message": (
                "Эксперт верифицирован"
                if analysis.decision == "approved"
                else "Не удалось подтвердить экспертность"
            ),
            "confidence_score": analysis.confidence_score,
            "document_type": analysis.document_type,
            "matches_selected_education": analysis.matches_selected_education,
            "full_name": analysis.full_name,
            "institution": analysis.institution,
            "qualification": analysis.qualification,
            "specialization": analysis.specialization,
            "graduation_year": analysis.graduation_year,
            "document_number": analysis.document_number,
            "red_flags": analysis.red_flags,
            "reasons": analysis.reasons,
            "file_hash": file_hash,
            "saved_path": save_path,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при верификации документа: {str(e)}",
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)