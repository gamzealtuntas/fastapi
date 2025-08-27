# Sentiment Analysis API
Bu proje Türkçe ve İngilizce metinler için duygu analizi (pozitif, negatif, nötr) yapan bir REST API uygulamasıdır.  
FastAPI, HuggingFace Transformers ve PyTorch kullanılarak geliştirilmiştir.

## Kurulum
### 1. Reposu Klonla
```bash
git clone https://github.com/gamzealtuntas/fastapi.git
cd fastapi

##Sanal ortam oluşturma
python -m venv venv

##windows
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate

##Linux/Mac:
source venv/bin/activate

##gerekli kütüphaneleri kur
pip install -r requirements.txt

##Eğer requirements.txt yoksa:
pip install fastapi uvicorn transformers torch langdetect


##çalıştırma
##Normal çalıştırma:

uvicorn main:app --reload

##Windows üzerinde run.bat ile çalıştırmak için:

.\app\run.bat



##Örnek istek:

{
  "text": "Bugün çok güzel bir gün"
}


##Örnek cevap:

{
  "sentiment": "positive",
  "score": 0.9876,
  "lang": "tr",
  "model": "savasy/bert-base-turkish-sentiment-cased"
}


##Türkçe için savasy/bert-base-turkish-sentiment-cased modeli kullanılmaktadır.

##İngilizce için cardiffnlp/twitter-roberta-base-sentiment-latest modeli kullanılmaktadır.

##GPU varsa otomatik CUDA üzerinde çalışır, yoksa CPU üzerinde çalışır.