import os
from pathlib import Path

from google import genai
from google.genai import errors, types

from dotenv import load_dotenv

# .env dosyasının yolunu belirle ve yükle
ENV_DOSYASI = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_DOSYASI)

def dogal_dilden_sql_uret(veritabani_semasi: str, kullanici_talebi: str) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 75)
    print(" YAPAY ZEKA DESTEKLİ DOĞAL DİLDEN SQL ÜRETİCİ ".center(75))
    print("=" * 75)

    
    api_anahtari = os.getenv("API_KEY")

    if not api_anahtari:
        print("\n[HATA] API_KEY tanımlanmamış!")
        return

    print("\n[AŞAMA 1] VERİTABANI ŞEMASI VE KULLANICI TALEBİ ALINDI...")

    sistem_mesaji = """
    Sen uzman bir Veritabanı Mimarı ve Kıdemli SQL Geliştiricisisin.
    Kullanıcının sana vereceği veritabanı şemasını ve doğal dildeki talebini analiz et.
    Bu bilgilere dayanarak en uygun, optimize edilmiş SQL sorgusunu yaz.

    Çıktın KESİNLİKLE sadece saf SQL sorgusu olmalıdır. 
    Markdown blokları (örn. ```sql), açıklama veya ek metin kesinlikle yazma.
    """

    prompt = f"""
    Veritabanı Şeması:
    {veritabani_semasi}

    Kullanıcı Talebi:
    {kullanici_talebi}
    """

    print("\n[AŞAMA 2] SQL ÇEVİRİSİ İÇİN GEMİNİ'YE BAĞLANILIYOR...\n")

    try:
        # Gemini istemcisini oluştur
        with genai.Client(api_key=api_anahtari) as client:
            print("Gemini isteği gönderiliyor...")
            # Gemini API isteğini gönder
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sistem_mesaji,
                    temperature=0.1,
                ),
            )
            print("Gemini yanıtı alındı!")

        uretilen_sql = response.text.strip()
        
        print("=" * 75)
        print(" ÜRETİLEN SQL SORGUSU ".center(75))
        print("=" * 75)
        print(uretilen_sql)
        print("=" * 75)

    except errors.APIError as hata:
        print(f"\n[HATA] Gemini API isteği başarısız: {hata}")


sema = """
1. Musteriler Tablosu: musteri_id, ad_soyad, eposta, sehir
2. Siparisler Tablosu: siparis_id, musteri_id, tutar, siparis_tarihi
"""

talep = """
Son 30 günde 25000 TL üzeri alışveriş yapan Muğla'daki
müşterilerin adını, e-posta adresini ve toplam harcama tutarını getir.
"""

if __name__ == "__main__":
    dogal_dilden_sql_uret(sema, talep)