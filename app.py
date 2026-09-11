import json
import os
import urllib.parse
import webbrowser
import streamlit as st

st.set_page_config(
    page_title="SepaDent - Akıllı Klinik Asistanı", page_icon="🦷", layout="wide"
)

st.title("🦷 SepaDent - Klinik Operasyon ve Asistan Paneli")
st.markdown(
    "Günlük iş yükünü sıfırlayan, tam entegre akıllı klinik yönetim sistemi."
)

# --- VERİ DOSYASI YÖNETİMİ (Kalıcı Hafıza) ---
DOSYA_ADI = "klinik_veri.json"


def veri_yukle():
  if os.path.exists(DOSYA_ADI):
    with open(DOSYA_ADI, "r", encoding="utf-8") as f:
      return json.load(f)
  return {
      "stoklar": {
          "Eldiven (Kutu)": 3,
          "Cerrahi Maske": 12,
          "Kompozit Dolgu Malzemesi": 2,
          "Frez Seti": 5,
          "Dezenfektan (Litre)": 1,
      },
      "randevular": [
          {
              "Saat": "09:30",
              "Hasta": "Ahmet Yılmaz",
              "İşlem": "Kanal Tedavisi",
              "Not": "Penisilin alerjisi var!",
          },
          {
              "Saat": "11:00",
              "Hasta": "Ayşe Demir",
              "İşlem": "Rutin Kontrol",
              "Not": "Hiçbir not yok.",
          },
          {
              "Saat": "14:15",
              "Hasta": "Mehmet Kaya",
              "İşlem": "Diş Taşı Temizliği",
              "Not": "Tansiyon hastası.",
          },
      ],
      "laboratuvar": [
          {
              "Hasta": "Fatma Şahin",
              "Islem": "Zirkon Kuron (Üst Çene)",
              "Durum": "Laboratuvarda",
              "Not": "Ölçü 2 gün önce gönderildi.",
          },
          {
              "Hasta": "Ali Öztürk",
              "Islem": "İskelet Protez",
              "Durum": "Prova Bekliyor",
              "Not": "Yarın provaya gelecek.",
          },
      ],
      "finans": [
          {
              "Hasta": "Ahmet Yılmaz",
              "ToplamBorc": 3500,
              "Odenen": 1500,
              "Kalan": 2000,
          },
          {"Hasta": "Ayşe Demir", "ToplamBorc": 1200, "Odenen": 1200, "Kalan": 0},
          {
              "Hasta": "Mehmet Kaya",
              "ToplamBorc": 5000,
              "Odenen": 2000,
              "Kalan": 3000,
          },
      ],
      "kasa": {"nakit": 3500, "kart": 4200},
  }


def veri_kaydet(veri):
  with open(DOSYA_ADI, "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)


# Verileri hafızadan yükle
klinik_verisi = veri_yukle()

# Eksik anahtarların eski json dosyalarında hata vermemesi için kontrol
if "kasa" not in klinik_verisi:
  klinik_verisi["kasa"] = {"nakit": 3500, "kart": 4200}
  veri_kaydet(klinik_verisi)

# --- SEKMELER ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📦 Canlı Stok",
        "📅 Randevular",
        "🔬 Laboratuvar",
        "💰 Borç Takibi",
        "📊 Günlük Kasa & Ciro",
    ]
)

with tab1:
  st.subheader("Sarf Malzeme ve Kritik Stok Yönetimi")
  st.markdown(
      "Malzemeleri azaltıp artırabilir, kritik seviyedekileri tek tıkla"
      " tedarikçiye bildirebilirsin."
  )

  kritik_malzemeler = []

  for malzeme, miktar in klinik_verisi["stoklar"].items():
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
    col1.write(f"**{malzeme}**")
    col2.write(f"Stok: **{miktar}**")

    if col3.button("➖", key=f"stok_azalt_{malzeme}"):
      if klinik_verisi["stoklar"][malzeme] > 0:
        klinik_verisi["stoklar"][malzeme] -= 1
        veri_kaydet(klinik_verisi)
        st.rerun()

    if col4.button("➕", key=f"stok_artir_{malzeme}"):
      klinik_verisi["stoklar"][malzeme] += 1
      veri_kaydet(klinik_verisi)
      st.rerun()

    if miktar <= 3:
      col5.error("⚠️ Kritik Seviye!")
      kritik_malzemeler.append(f"- {malzeme}: {miktar} adet kaldı")
    else:
      col5.success("Yeterli")

  st.write("---")

  tedarikci_telefon = st.text_input(
      "Tedarikçi WhatsApp Numarası (Örn: 905551112233)", "90", key="ted_tel_input"
  )

  if st.button(
      "📲 Tek Tıkla Tedarik Listesi Gönder", key="tedarik_gonder_btn"
  ):
    if not kritik_malzemeler:
      st.warning("Şu an kritik seviyede azalan malzeme bulunmuyor.")
    elif not tedarikci_telefon or len(tedarikci_telefon) < 10:
      st.warning("Lütfen geçerli bir tedarikçi telefon numarası girin.")
    else:
      stok_mesaji = (
          "Klinik Kritik Stok Raporu\n\nAcil sipariş verilmesi gereken"
          " malzemeler:\n"
          + "\n".join(kritik_malzemeler)
      )
      encoded_stok_mesaj = urllib.parse.quote(stok_mesaji)
      stok_whatsapp_link = (
          f"https://wa.me/{tedarikci_telefon}?text={encoded_stok_mesaj}"
      )

      webbrowser.open(stok_whatsapp_link)
      st.success("Tedarik listesi WhatsApp'a aktarıldı.")

with tab2:
  st.subheader("Bugünkü Hasta Listesi ve İşlem Notları")

  for index, randevu in enumerate(klinik_verisi["randevular"]):
    with st.expander(
        f"{randevu['Saat']} - {randevu['Hasta']} ({randevu['İşlem']})"
    ):
      st.write(f"**Kritik Not / Alerji:** {randevu['Not']}")

      hasta_telefon_input = st.text_input(
          f"Hasta Tel ({randevu['Hasta']})", "90", key=f"hasta_tel_{index}"
      )

      if st.button(
          f"📲 Randevu Hatırlatması Gönder ({randevu['Hasta']})",
          key=f"hasta_btn_{index}",
      ):
        if not hasta_telefon_input or len(hasta_telefon_input) < 10:
          st.warning("Lütfen geçerli bir hasta telefon numarası girin.")
        else:
          randevu_mesaji = (
              f"Sayın {randevu['Hasta']}, kliniğimizdeki"
              f" {randevu['Saat']} saatli randevunuz ({randevu['İşlem']})"
              " için sizi bekliyoruz. Sağlıklı günler dileriz."
          )
          encoded_randevu_mesaj = urllib.parse.quote(randevu_mesaji)
          randevu_whatsapp_link = (
              f"https://wa.me/{hasta_telefon_input}?text={encoded_randevu_mesaj}"
          )

          webbrowser.open(randevu_whatsapp_link)
          st.success(
              f"{randevu['Hasta']} için randevu hatırlatması hazırlandı."
          )

with tab3:
  st.subheader("Dış Laboratuvar ve Protez Durum Takibi")
  st.markdown(
      "Laboratuvara gönderilen işlerin durumunu takip edebilir, gerekirse"
      " laboratuvara WhatsApp ile bilgi sorabilirsin."
  )

  for lab_idx, lab_is in enumerate(klinik_verisi["laboratuvar"]):
    with st.expander(
        f"Hasta: {lab_is['Hasta']} — İşlem: {lab_is['Islem']} (Durum:"
        f" {lab_is['Durum']})"
    ):
      st.write(f"**Detay / Not:** {lab_is['Not']}")

      yeni_durum = st.selectbox(
          "Durumu Güncelle",
          ["Laboratuvarda", "Prova Bekliyor", "Kliniğe Geldi / Tamamlandı"],
          index=[
              "Laboratuvarda",
              "Prova Bekliyor",
              "Kliniğe Geldi / Tamamlandı",
          ].index(lab_is["Durum"])
          if lab_is["Durum"]
          in ["Laboratuvarda", "Prova Bekliyor", "Kliniğe Geldi / Tamamlandı"]
          else 0,
          key=f"durum_select_{lab_idx}",
      )

      if yeni_durum != lab_is["Durum"]:
        klinik_verisi["laboratuvar"][lab_idx]["Durum"] = yeni_durum
        veri_kaydet(klinik_verisi)
        st.rerun()

      lab_telefon = st.text_input(
          f"Laboratuvar WhatsApp Tel ({lab_is['Hasta']} için)",
          "90",
          key=f"lab_tel_{lab_idx}",
      )
      if st.button(
          f"📲 Laboratuvara Durum Sor ({lab_is['Hasta']})",
          key=f"lab_btn_{lab_idx}",
      ):
        if not lab_telefon or len(lab_telefon) < 10:
          st.warning("Lütfen geçerli bir laboratuvar telefon numarası girin.")
        else:
          lab_mesaji = (
              f"Merhaba, {lab_is['Hasta']} isimli hastamızın '{lab_is['Islem']}'"
              f" konulu protez işinin güncel durumunu öğrenebilir miyim?"
              f" (Mevcut Durum: {lab_is['Durum']})"
          )
          encoded_lab_mesaj = urllib.parse.quote(lab_mesaji)
          lab_whatsapp_link = (
              f"https://wa.me/{lab_telefon}?text={encoded_lab_mesaj}"
          )

          webbrowser.open(lab_whatsapp_link)
          st.success("Laboratuvar sorgu mesajı hazırlandı.")

with tab4:
  st.subheader("Hasta Tedavi Ücretleri ve Borç Takibi")
  st.markdown(
      "Hastaların toplam tedavi borçlarını, ödenen miktarları ve kalan"
      " bakiyelerini takip edebilirsin."
  )

  for fin_idx, finans_kayit in enumerate(klinik_verisi["finans"]):
    kalan_tutar = finans_kayit["ToplamBorc"] - finans_kayit["Odenen"]
    klinik_verisi["finans"][fin_idx]["Kalan"] = kalan_tutar

    with st.expander(
        f"Hasta: {finans_kayit['Hasta']} — Kalan Bakiye: {kalan_tutar} TL"
    ):
      col_f1, col_f2 = st.columns(2)
      col_f1.write(f"Toplam Borç: **{finans_kayit['ToplamBorc']} TL**")
      col_f2.write(f"Ödenen: **{finans_kayit['Odenen']} TL**")

      if kalan_tutar > 0:
        st.warning(f"Kalan Borç / Bakiye: {kalan_tutar} TL")
      else:
        st.success("Borç Kapandı (Bakiye Yok)")

      yeni_odenen = st.number_input(
          f"Alınan Yeni Ödeme Miktarı (TL) - {finans_kayit['Hasta']}",
          min_value=0,
          value=0,
          step=100,
          key=f"odeme_input_{fin_idx}",
      )

      if st.button(
          f"💳 Ödemeyi İşle ve Bakiyeyi Güncelle ({finans_kayit['Hasta']})",
          key=f"odeme_btn_{fin_idx}",
      ):
        if yeni_odenen > 0:
          klinik_verisi["finans"][fin_idx]["Odenen"] += yeni_odenen
          # Kasaya da otomatik nakit olarak ekleyelim
          klinik_verisi["kasa"]["nakit"] += yeni_odenen
          veri_kaydet(klinik_verisi)
          st.success(
              f"{yeni_odenen} TL tahsilat eklendi, bakiye düşüldü ve kasaya"
              " işlendi!"
          )
          st.rerun()

      borc_telefon = st.text_input(
          f"Hasta Tel ({finans_kayit['Hasta']} Ödeme Bildirimi)",
          "90",
          key=f"borc_tel_{fin_idx}",
      )
      if st.button(
          f"📲 Ödeme Hatırlatması Gönder ({finans_kayit['Hasta']})",
          key=f"borc_btn_{fin_idx}",
      ):
        if not borc_telefon or len(borc_telefon) < 10:
          st.warning("Lütfen geçerli bir hasta telefon numarası girin.")
        else:
          borc_mesaji = (
              f"Sayın {finans_kayit['Hasta']}, kliniğimizdeki tedaviniz"
              f" dolayısıyla kalan {kalan_tutar} TL bakiye bilginizi"
              " hatırlatmak isteriz. Sağlıklı günler dileriz."
          )
          encoded_borc_mesaj = urllib.parse.quote(borc_mesaji)
          borc_whatsapp_link = (
              f"https://wa.me/{borc_telefon}?text={encoded_borc_mesaj}"
          )

          webbrowser.open(borc_whatsapp_link)
          st.success("Ödeme hatırlatması WhatsApp'a aktarıldı.")

with tab5:
  st.subheader("Günlük Kasa ve Toplam Ciro Özeti")
  st.markdown(
      "Günün sonunda nakit ve kart gelirlerini takip edebilir, akşam raporunu"
      " tek tıkla kendi WhatsApp'ına bildirebilirsin."
  )

  nakit_kasa = klinik_verisi["kasa"]["nakit"]
  kart_kasa = klinik_verisi["kasa"]["kart"]
  toplam_ciro = nakit_kasa + kart_kasa

  col_k1, col_k2, col_k3 = st.columns(3)
  col_k1.metric("Nakit Kasa", f"{nakit_kasa} TL")
  col_k2.metric("Kredi Kartı", f"{kart_kasa} TL")
  col_k3.metric("Toplam Günlük Ciro", f"{toplam_ciro} TL")

  st.write("---")

  # Kasaya manuel gelir ekleme alanı
  st.markdown("### Ek Gelir / Kasa Girişi Yap")
  col_giris1, col_giris2 = st.columns(2)
  eklenen_nakit = col_giris1.number_input(
      "Eklenecek Nakit (TL)", min_value=0, value=0, step=50, key="ek_nakit"
  )
  eklenen_kart = col_giris2.number_input(
      "Eklenecek Kart (TL)", min_value=0, value=0, step=50, key="ek_kart"
  )

  if st.button("➕ Kasaya Gelir Ekle"):
    if eklenen_nakit > 0 or eklenen_kart > 0:
      klinik_verisi["kasa"]["nakit"] += eklenen_nakit
      klinik_verisi["kasa"]["kart"] += eklenen_kart
      veri_kaydet(klinik_verisi)
      st.success("Kasa başarıyla güncellendi!")
      st.rerun()

  st.write("---")

  # Günlük Raporu WhatsApp ile Gönderme
  yonetici_telefon = st.text_input(
      "Kendi WhatsApp Numaranız (Raporu Alacak Kişi)", "90", key="yonetici_tel"
  )

  if st.button("📲 Tek Tıkla Günlük Kasa Raporunu Gönder"):
    if not yonetici_telefon or len(yonetici_telefon) < 10:
      st.warning("Lütfen geçerli bir telefon numarası girin.")
    else:
      kasa_mesaji = (
          f"🦷 *Klinik Günlük Kasa ve Ciro Raporu*\n\n"
          f"💵 Nakit Kasa: {nakit_kasa} TL\n"
          f"💳 Kredi Kartı: {kart_kasa} TL\n"
          f"💰 *Toplam Ciro:* {toplam_ciro} TL\n\n"
          "İyi akşamalar dileriz!"
      )
      encoded_kasa_mesaj = urllib.parse.quote(kasa_mesaji)
      kasa_whatsapp_link = (
          f"https://wa.me/{yonetici_telefon}?text={encoded_kasa_mesaj}"
      )

      webbrowser.open(kasa_whatsapp_link)
      st.success("Günlük kasa raporu WhatsApp'a aktarıldı.")

verekaydet_kontrol = veri_kaydet(klinik_verisi)
