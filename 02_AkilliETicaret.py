import os
import json
from dotenv import load_dotenv

# .env dosyasını okuyarak içindeki bilgileri sisteme yükler
load_dotenv() 

# API KEY'ini güvenli bir şekilde .env dosyasından alır
api_key = os.getenv("API_KEY") 
DOSYA_ADI = "urunler.json"


def urunleri_yukle() -> list:
    """JSON dosyasından ürünleri okur. Dosya bozuk veya yoksa boş liste döner."""
    if not os.path.exists(DOSYA_ADI):
        return []
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            return json.load(dosya)
    except (json.JSONDecodeError, IOError):
        print("[HATA] Veritabanı dosyası okunamadı, boş bir liste ile başlanıyor.")
        return []

def urunleri_kaydet(urunler: list):
    """Ürünler listesini JSON dosyasına güvenli şekilde kaydeder."""
    try:
        with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
            json.dump(urunler, dosya, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"[HATA] Dosya kaydedilemedi: {e}")

def urun_kodu_uret(mevcut_urunler: list) -> str:
    """URN-0001 formatında ardışık yeni ürün kodu üretir."""
    return f"URN-{(len(mevcut_urunler) + 1):04d}"


# ==========================================
# API İŞLEMLERİ
# ==========================================
def api_urun_analizi(aciklama: str) -> dict:
    """Gemini API ile açıklamayı analiz eder, güvenli bir JSON sözlüğü döndürür."""
    current_api_key = os.getenv("API_KEY")
    if not current_api_key:
        raise ValueError("API anahtarı bulunamadı! Lütfen .env dosyanızı kontrol edin.")

    try:
        from google import genai
        from google.genai import types
    except ModuleNotFoundError:
        raise ModuleNotFoundError("google-genai paketi eksik. (pip install google-genai)")

    sistem_mesaji = """
    Sen bir e-ticaret asistanısın. Girilen ürün bilgisini SADECE JSON olarak döndür.
    Zorunlu JSON anahtarları: "urun_adi", "kategori", "seo_etiketleri", "satis_aciklamasi"
    """
    
    client = genai.Client(api_key=current_api_key)
    
    # Model ismi gemini-3.8-flash olarak ayarlandı
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=aciklama,
        config=types.GenerateContentConfig(
            system_instruction=sistem_mesaji,
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    
    veri = json.loads(response.text)
    gerekli_alanlar = {"urun_adi", "kategori", "seo_etiketleri", "satis_aciklamasi"}
    
    if not gerekli_alanlar.issubset(veri.keys()):
        raise ValueError("API eksik veya hatalı veri döndürdü.")
        
    return veri


def sayi_al(mesaj: str, veri_tipi=int):
    """Kullanıcıdan hata yapmadan, negatif olmayan sayı almayı garantiler."""
    while True:
        try:
            deger = veri_tipi(input(mesaj))
            if deger < 0:
                print("[HATA] Bu değer negatif olamaz!")
                continue
            return deger
        except ValueError:
            print("[HATA] Lütfen geçerli bir sayı giriniz!")

def stok_durumu_yazdir(stok: int):
    """Stok miktarına göre uyarı mesajı verir."""
    if stok == 0:
        print("[UYARI] STOKTA YOK!")
    elif 1 <= stok <= 4:
        print(f"[UYARI] KRİTİK STOK! Yalnızca {stok} adet kaldı.")


# ==========================================
# MENÜ FONKSİYONLARI
# ==========================================
def urun_ekle_menu():
    print("\n--- 1. YENİ ÜRÜN EKLE ---")
    while not (aciklama := input("Ürün açıklaması: ").strip()):
        print("[HATA] Açıklama boş olamaz!")

    fiyat = sayi_al("Ürün fiyatı: ", float)
    stok = sayi_al("Stok miktarı: ", int)

    print("[API] Ürün bilgileri oluşturuluyor...")
    try:
        api_verisi = api_urun_analizi(aciklama)
    except Exception as e:
        print(f"[HATA] API işlemi başarısız: {e}")
        return

    urunler = urunleri_yukle()
    yeni_urun = {
        "urun_kodu": urun_kodu_uret(urunler),
        "fiyat": fiyat,
        "stok": stok,
        **api_verisi
    }

    urunler.append(yeni_urun)
    urunleri_kaydet(urunler)

    print("\n[BAŞARILI] Ürün kaydedildi.")
    print(f"Ürün Kodu: {yeni_urun['urun_kodu']}")
    print(f"Ürün Adı: {yeni_urun['urun_adi']}")
    print(f"Kategori: {yeni_urun['kategori']}")
    print(f"Fiyat   : {yeni_urun['fiyat']} TL\nStok    : {yeni_urun['stok']}")
    stok_durumu_yazdir(yeni_urun['stok'])

def urunleri_listele_menu():
    print("\n--- 2. ÜRÜNLERİ LİSTELE ---")
    urunler = urunleri_yukle()
    if not urunler:
        print("[UYARI] Henüz hiç ürün eklenmemiş.")
        return

    for u in urunler:
        print(f"[{u['urun_kodu']}] {u['urun_adi']} | {u['kategori']} | {u['fiyat']} TL | Stok: {u['stok']}")
        stok_durumu_yazdir(u['stok'])

def urun_ara_menu():
    print("\n--- 3. ÜRÜN ARA ---")
    anahtar = input("Aranacak kelime veya kod: ").strip().lower()
    
    bulunanlar = [u for u in urunleri_yukle() if anahtar in u['urun_adi'].lower() or anahtar in u['urun_kodu'].lower()]
    
    if bulunanlar:
        print(f"\n[SONUÇ] {len(bulunanlar)} ürün bulundu:")
        for u in bulunanlar:
            print(f"- {u['urun_kodu']}: {u['urun_adi']} (Stok: {u['stok']})")
    else:
        print("[SONUÇ] Eşleşen ürün bulunamadı.")

def stok_guncelle_menu():
    print("\n--- 4. STOK GÜNCELLE ---")
    kod = input("Ürün kodu (Örn: URN-0001): ").strip().upper()
    urunler = urunleri_yukle()
    
    for u in urunler:
        if u['urun_kodu'] == kod:
            print(f"Bulunan Ürün: {u['urun_adi']} | Güncel Stok: {u['stok']}")
            yeni_stok = sayi_al("Yeni stok miktarı: ", int)
            eski_stok = u['stok']
            u['stok'] = yeni_stok
            
            urunleri_kaydet(urunler)
            print(f"\n[BAŞARILI] Stok {eski_stok} -> {yeni_stok} olarak güncellendi.")
            stok_durumu_yazdir(yeni_stok)
            return
            
    print("[HATA] Belirtilen koda sahip ürün bulunamadı.")


def ana_menu():
    while True:
        print("\n" + "="*30)
        print(" E-TİCARET YÖNETİM PANELİ ")
        print("="*30)
        print("1 - Yeni Ürün Ekle\n2 - Ürünleri Listele\n3 - Ürün Ara\n4 - Stok Güncelle\n5 - Çıkış")
        
        secim = input("Seçiminiz: ").strip()
        
        if secim == "1": urun_ekle_menu()
        elif secim == "2": urunleri_listele_menu()
        elif secim == "3": urun_ara_menu()
        elif secim == "4": stok_guncelle_menu()
        elif secim == "5":
            print("Sistemden çıkılıyor. İyi çalışmalar!")
            break
        else:
            print("[HATA] Geçersiz seçim! Lütfen 1 ile 5 arasında bir sayı girin.")

if __name__ == "__main__":
    ana_menu()