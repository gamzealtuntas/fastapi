from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from langdetect import detect, LangDetectException

app = FastAPI(
    title="Sentiment API",
    version="1.0.0",
    description="Türkçe/İngilizce duygu analizi (pozitif/negatif/nötr) için REST API"
)

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Analiz edilecek metin")
    lang: Optional[Literal["tr", "en"]] = Field(default=None)

class AnalyzeResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    score: float
    lang: Literal["tr", "en"]
    model: str

# 🔁 İstersen modeli burada değiştirebilirsin (örnek: emrecan/bert-base-turkish-sentiment-analysis)
tr_model_id = "savasy/bert-base-turkish-sentiment-cased"
en_model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"

device = 0 if torch.cuda.is_available() else -1

tr_pipeline = None
en_pipeline = None

def load_pipelines():
    global tr_pipeline, en_pipeline

    tr_tok = AutoTokenizer.from_pretrained(tr_model_id)
    tr_mod = AutoModelForSequenceClassification.from_pretrained(tr_model_id)
    tr_pipeline = pipeline(
        "text-classification",
        model=tr_mod,
        tokenizer=tr_tok,
        device=device,
        top_k=1
    )

    en_tok = AutoTokenizer.from_pretrained(en_model_id)
    en_mod = AutoModelForSequenceClassification.from_pretrained(en_model_id)
    en_pipeline = pipeline(
        "text-classification",
        model=en_mod,
        tokenizer=en_tok,
        device=device,
        top_k=1
    )

def normalize_label(raw_label: str) -> str:
    """
    Modelden dönen etiketi normalize eder.
    Büyük/küçük harf, Türkçe/İngilizce varyasyonlara dayanıklıdır.
    """
    l = raw_label.strip().lower()

    if "positive" in l or "pos" in l or "olumlu" in l:
        return "positive"
    if "negative" in l or "neg" in l or "olumsuz" in l:
        return "negative"
    if "neutral" in l or "neu" in l or "nötr" in l or "notr" in l:
        return "neutral"

    # Label_0/1/2 varsa (örneğin: LABEL_0, LABEL_1)
    l = raw_label.strip().upper()
    if "LABEL_0" in l:
        return "negative"
    if "LABEL_1" in l:
        return "neutral"
    if "LABEL_2" in l:
        return "positive"

    return "neutral"

def detect_lang(text: str, forced: Optional[str]) -> str:
    if forced in ("tr", "en"):
        return forced
    try:
        code = detect(text)
        return "tr" if code.startswith("tr") else "en"
    except LangDetectException:
        if any(ch in text for ch in "çğıöşüÇĞİÖŞÜ"):
            return "tr"
        return "en"

@app.on_event("startup")
def _startup():
    load_pipelines()

@app.get("/health")
def health():
    return {"status": "ok", "device": "cuda" if device == 0 else "cpu"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text boş olamaz.")

    lang = detect_lang(req.text, req.lang)

    if lang == "tr":
        clf = tr_pipeline
        model_id = tr_model_id
    else:
        clf = en_pipeline
        model_id = en_model_id

    if clf is None:
        raise HTTPException(status_code=503, detail="Model yüklenemedi.")

    try:
        raw_result = clf(req.text)

        if isinstance(raw_result, list):
            if isinstance(raw_result[0], list):
                result = raw_result[0][0]
            else:
                result = raw_result[0]
        else:
            result = raw_result

        print("🔎 Model çıktısı:", result)  # Terminalde göster

        sentiment = normalize_label(result["label"])
        score = round(float(result["score"]), 4)

        return AnalyzeResponse(
            sentiment=sentiment,
            score=score,
            lang=lang,
            model=model_id
        )

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {ex}")
