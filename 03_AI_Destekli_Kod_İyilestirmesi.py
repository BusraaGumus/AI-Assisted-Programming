import os
from pathlib import Path

from google import genai
from google.genai import errors, types

from dotenv import load_dotenv

ENV_DOSYASI = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_DOSYASI)

def kod_optimize_et(spagetti_kod: str) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 75)
    print(" YAPAY ZEKA DESTEKLİ KOD İYİLEŞTİRME VE OPTİMİZASYON ".center(75))
    print("=" * 75)

    # API anahtarını ortam değişkeninden al

    api_anahtari = os.getenv("API_KEY")

    if not api_anahtari:
        print("\n[HATA] API_KEY tanımlanmamış!")
        return

    sistem_mesaji = """
    Sen kıdemli bir Yazılım Mimarı ve Performans Uzmanısın.

    Kullanıcının gönderdiği kötü yazılmış (spagetti)
    Python kodunu analiz et.

    1. Değişken isimlerini anlamlı hale getir (Clean Code).
    2. Algoritmanın çalışma hızını iyileştir.
       Örneğin O(n^2) yerine mümkünse O(n) kullan.
    3. Type Hint (Tip belirteçleri) ekle.
    4. Kodun mevcut işlevselliğini koru.
    5. Gereksiz döngüleri ortadan kaldır.

    Çıktın KESİNLİKLE sadece düzeltilmiş Python kodu olmalıdır.
    Ek açıklama veya Markdown yazma.
    """

    print("\n[AŞAMA 1] OPTİMİZE EDİLECEK SPAGETTİ KOD SİSTEME ALINDI...")
    print("\n[AŞAMA 2] REFACTORING İÇİN YAPAY ZEKAYA BAĞLANILIYOR...\n")

    try:
        # Gemini istemcisini oluştur.
        with genai.Client(api_key=api_anahtari) as client:
            # Gemini API isteğini gönder.
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=spagetti_kod,
                config=types.GenerateContentConfig(
                    system_instruction=sistem_mesaji,
                    temperature=0.2,
                ),
            )

        temiz_kod = response.text
        print("\n[AŞAMA 3] YAPAY ZEKA TARAFINDAN OPTİMİZE EDİLEN KOD ALINDI.\n")
        print("=" * 75)
        print(temiz_kod)
    except errors.APIError as hata:
        print(f"\n[HATA] Gemini API isteği başarısız: {hata}")


kotu_kod = """
def bul(1):
    for i in range(len(1)):
        for j in range (i+1, len(1)):
            if 1[i] == 1[j] and 1[i] not in r:
            r.append(1[i])
    return r
"""


if __name__ == "__main__":
    kod_optimize_et(kotu_kod)