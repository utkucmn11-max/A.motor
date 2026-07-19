import streamlit as st
import time
import pandas as pd
import numpy as np

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Endüstriyel Asenkron Motor Laboratuvarı", layout="wide")

st.title("🏭 Profesyonel Asenkron Motor Test ve Simülasyon Laboratuvarı")
st.write("Bu simülatör, endüstriyel standartlarda elektriksel ve mekanik analiz yapar. Yaptığınız bağlantılar anlık olarak termal ve elektriksel yüklere dönüşür.")

# --- SESSION STATE INITIALIZATION ---
if "mekanik_durum" not in st.session_state:
    st.session_state.mekanik_durum = {"Stator Gövde": True, "Rotor/Mil": False, "Kapaklar/Rulmanlar": False, "Soğutma Fanı": False}
if "baglantilar" not in st.session_state:
    st.session_state.baglantilar = []
if "secili_vida" not in st.session_state:
    st.session_state.secili_vida = None
if "salter" not in st.session_state:
    st.session_state.salter = False
if "voltaj" not in st.session_state:
    st.session_state.voltaj = 380
if "yuk" not in st.session_state:
    st.session_state.yuk = 0.0

# --- YARATICI ARAYÜZ MİMARİSİ (3 BÖLÜM) ---
sol_panel, orta_panel, sag_panel = st.columns([1, 1.2, 1.3])

# --- 1. MEKANİK MONTAJ LAB ---
with sol_panel:
    st.markdown("### 🛠️ 1. Mekanik Montaj Hattı")
    st.caption("Motor bileşenlerini doğru sıra ile monte edin.")
    
    # Şematik ASCII Görselleştirme
    st.code("""
     ┌──────────────────────┐
     │   [KLEMENS KUTUSU]   │
    ┌┴──────────────────────┴┐
    │  [Ön]   [STATOR]   [Arka]│===[FAN]
    └┬──────────────────────┬┘
     │        [ROTOR]       │===> (Mil)
     └──────────────────────┘
    """, language="text")

    for parca, takili in st.session_state.mekanik_durum.items():
        c1, c2 = st.columns([2, 1])
        c1.write(f"**{parca}** " + ("(🟢 Takılı)" if takili else "(🔴 Sökük)"))
        if takili:
            if c2.button("Sök", key=f"s_{parca}"):
                st.session_state.mekanik_durum[parca] = False
                st.rerun()
        else:
            if c2.button("Tak", key=f"t_{parca}"):
                st.session_state.mekanik_durum[parca] = True
                st.rerun()

    st.markdown("---")
    st.markdown("### 🔌 Şebeke Parametreleri")
    st.session_state.voltaj = st.selectbox("Giriş Faz-Faz Gerilimi ($V_L$)", [380, 220], index=0)
    st.session_state.yuk = st.slider("Motora Uygulanan Mekanik Yük (Nm)", 0.0, 50.0, 0.0, step=2.5)

# --- 2. MANUEL ELEKTRİKSEL KLEMENS LAB ---
with orta_panel:
    st.markdown("### ⚡ 2. Manuel Klemens Köprüleme")
    st.caption("Klemens vidalarına sırayla dokunarak kendi köprü lamalarınızı oluşturun.")

    # Mevcut Köprüler
    if st.session_state.baglantilar:
        st.write("**Aktif Köprüleriniz:**")
        for v1, v2 in st.session_state.baglantilar:
            st.code(f"🔗 Lama: {v1} ─── {v2}")
        if st.button("🗑️ Tüm Köprüleri Sök"):
            st.session_state.baglantilar = []
            st.session_state.secili_vida = None
            st.rerun()
    else:
        st.info("Klemens açık devre. Köprü oluşturmak için aşağıdaki vidaları kullanın.")

    if st.session_state.secili_vida:
        st.warning(f"👉 **{st.session_state.secili_vida}** seçildi. Şimdi köprünün bağlanacağı 2. vidayı seçin.")
    
    # Klemens Buton Matrisi
    st.write("**[ U - V - W Sargı Uçları ]**")
    
    def vida_tikla(isim):
        if st.session_state.secili_vida is None:
            st.session_state.secili_vida = isim
        else:
            if st.session_state.secili_vida != isim:
                st.session_state.baglantilar.append(tuple(sorted((st.session_state.secili_vida, isim))))
            st.session_state.secili_vida = None
        st.rerun()

    c_w2, c_u2, c_v2 = st.columns(3)
    if c_w2.button("🔩 W2", use_container_width=True): vida_tikla("W2")
    if c_u2.button("🔩 U2", use_container_width=True): vida_tikla("U2")
    if c_v2.button("🔩 V2", use_container_width=True): vida_tikla("V2")

    st.write("") # Dikey boşluk (Bobin gövde alanı)
    st.code("   [U1-U2 Bobini]     [V1-V2 Bobini]     [W1-W2 Bobini]", language="text")
    st.write("")

    c_u1, c_v1, c_w1 = st.columns(3)
    if c_u1.button("🔩 U1", use_container_width=True): vida_tikla("U1")
    if c_v1.button("🔩 V1", use_container_width=True): vida_tikla("V1")
    if c_w1.button("🔩 W1", use_container_width=True): vida_tikla("W1")

# --- 3. Gelişmiş Test, Simülasyon ve Analiz Motoru ---
with sag_panel:
    st.markdown("### 🖥️ 3. Dijital İkiz ve Analiz Ekranı")
    
    # Şalter Arayüzü
    if not st.session_state.salter:
        if st.button("🚀 LABORATUVAR ŞALTERİNİ AÇ", type="primary", use_container_width=True):
            st.session_state.salter = True
            st.rerun()
    else:
        if st.button("🛑 ŞALTERİ KES (ACİL DURDURMA)", type="secondary", use_container_width=True):
            st.session_state.salter = False
            st.rerun()

    st.markdown("---")
    
    if st.session_state.salter:
        # Analiz Mantığı
        mekanik_tam = all(st.session_state.mekanik_durum.values())
        fan_eksik = not st.session_state.mekanik_durum["Soğutma Fanı"]
        norm_b = set(st.session_state.baglantilar)

        # Eşleşme Mantığı Kontrolleri
        is_yildiz = {("U2", "W2"), ("U2", "V2")}.issubset(norm_b) or {("W2", "V2"), ("U2", "V2")}.issubset(norm_b)
        is_ucgen = {("U1", "W2"), ("U2", "V1"), ("V2", "W1")}.issubset(norm_b)
        is_kisa_devre = any(kd in norm_b for kd in [("U1", "V1"), ("V1", "W1"), ("U1", "W1")])

        # Başlangıç Fiziksel Değerleri
        rpm = 0
        akim = 0.0
        sicaklik = 25.0
        durum = "Bilinmiyor"

        if not mekanik_tam:
            if not st.session_state.mekanik_durum["Rotor/Mil"]:
                st.error("💥 **KRİTİK HATA [ERR_NO_ROTOR]:** Stator içinde rotor yok! Döner manyetik alan boşlukta salınım yapıyor, yüksek endüktif akım çekiliyor! Sigortalar attı.")
                st.metric("Çekilen Akım", "120 A", "Aşırı Akım")
            else:
                st.error("⚠️ **MEKANİK KİLİTLENME [ERR_MECH]:** Kapaklar gevşek veya rulman eksenleri kaçık. Motor dönemiyor, rotor statora sürtünüyor!")
                st.metric("Sargı Sıcaklığı", "140 °C", "+115 °C Tehlike")
        
        elif is_kisa_devre:
            st.error("🔥 **KATASTROFİK ARIZA [ERR_SHORT_CIRCUIT]:** Şebeke fazlarını klemens üzerinde direkt kısa devre ettiniz! Koruma şalterleri patladı.")
            st.audio("https://www.soundjay.com/buttons/sounds/button-4.mp3") # Temsili uyarı sesi gerekirse
            
        elif is_yildiz:
            durum = "Yıldız Stabil"
            base_rpm = 1450 if st.session_state.voltaj == 380 else 1100
            rpm = int(base_rpm - (st.session_state.yuk * 5))
            akim = round(4.5 + (st.session_state.yuk * 0.3), 1)
            sicaklik = round(45 + (st.session_state.yuk * 1.2) + (25 if fan_eksik else 0), 1)
            
            st.success(f"🟢 Motor Yıldız Bağlantıda Stabil Çalışıyor ({st.session_state.voltaj}V)")
            if fan_eksik: st.warning("⚠️ Soğutma fanı takılı olmadığı için motor gövdesi aşırı ısınıyor!")

        elif is_ucgen:
            if st.session_state.voltaj == 380:
                durum = "Üçgen Aşırı Gerilim"
                st.error("🔥 **AŞIRI GERİLİM AŞIRI AKIM:** 380V şebekede direkt üçgen kalkış sargıları zorluyor. Motor sargı izolasyonu eriyor!")
                akim = 28.0 + (st.session_state.yuk * 0.8)
                sicaklik = 135.0
                rpm = 1480
            else:
                durum = "Üçgen Stabil"
                rpm = int(1480 - (st.session_state.yuk * 3))
                akim = round(7.8 + (st.session_state.yuk * 0.4), 1)
                sicaklik = round(50 + (st.session_state.yuk * 0.9) + (30 if fan_eksik else 0), 1)
                st.success("🟢 Motor Üçgen Bağlantıda Tam Güç Çalışıyor (220V Şebeke)")
        
        elif len(norm_b) == 0:
            st.info("🔇 Motor Açık Devre: Akım geçişi yok, sargılar enerjisiz.")
            sicaklik = 25.0
        else:
            st.error("⚠️ **FAZ DENGESİZLİĞİ / YANLIŞ BAĞLANTI:** Motor sargı yönleri çakışıyor. Rotor titriyor ama dönemiyor (Tek faza kalma veya ters moment).")
            akim = 18.5
            sicaklik = 95.0

        # Canlı Göstergeler (Metrics)
        if durum != "Bilinmiyor" and mekanik_tam and not is_kisa_devre:
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Motor Hızı", f"{rpm} RPM", delta=f"{rpm - 1500} RPM (Senkron)")
            c_m2.metric("Hat Akımı ($I_L$)", f"{akim} A", delta=f"{round(akim-4.5, 1)} A Sapma")
            c_m3.metric("Sargı Isısı", f"{sicaklik} °C", delta="TEHLİKE" if sicaklik > 90 else "Normal")
            
            # Gerçek Zamanlı Telemetri Grafik Simülasyonu
            st.write("**📈 Dinamik Kararlılık Grafiği (Zaman İçi Değişim)**")
            t_steps = np.linspace(0, 10, 50)
            # Yük ve akıma bağlı sahte gürültülü veri üretimi
            noise = np.random.normal(0, 0.1, 50)
            chart_data = pd.DataFrame({
                "Zaman (sn)": t_steps,
                "Anlık Akım (A)": akim + noise + np.sin(t_steps)*0.2,
                "Sıcaklık Grafiği (°C)": np.minimum(sicaklik, 25 + (sicaklik - 25) * (1 - np.exp(-t_steps/3)))
            }).set_index("Zaman (sn)")
            st.line_chart(chart_data)
            
    else:
        st.info("⚡ Test tezgahında enerji yok. Güvenle mekanik parçaları değiştirebilir ve klemens köprülerini bağlayabilirsiniz.")
