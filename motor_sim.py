
import streamlit as st
import time
import pandas as pd
import numpy as np

st.set_page_config(page_title="Endüstriyel Motor Montaj Masası", layout="wide")

# --- ATÖLYE SES/UYANIKLIK EFEKTLERİ VEYA GÖRSEL BAŞLIK ---
st.title("👨‍🔧 Atölye Masası: 3-Fazlı Asenkron Motor Manuel Bağlantı İstasyonu")
st.write("**İş Emri:** Önündeki 5.5 kW'lık döküm gövde sincap kafesli asenkron motoru mekanik olarak topla, klemens kutusunu şebekeye hazırla ve test panosundan enerjilendir.")

# --- INITIALIZATION ---
if "vida_secimleri" not in st.session_state:
    st.session_state.vida_secimleri = []
if "aktif_vida" not in st.session_state:
    st.session_state.aktif_vida = None
if "takimlar" not in st.session_state:
    st.session_state.takimlar = {"Rotor": False, "Kapaklar": False, "Fan Pervanesi": False, "Muhafaza": False}
if "loto_kilidi" not in st.session_state:
    st.session_state.loto_kilidi = True # İş güvenliği kilidi aktif başlar
if "ana_salter" not in st.session_state:
    st.session_state.ana_salter = False

# --- SOL BÖLÜM: MEKANİK MONTAJ MASASI (TEZGAH) ---
col_sol, col_orta, col_sag = st.columns([1.1, 1.2, 1.2])

with col_sol:
    st.subheader("🔧 1. Mekanik Montaj Tezgahı")
    st.write("_Parçaları sırasıyla motora çakmalı veya vidalamalısın. Sıralama hatası rulmanları dağıtır!_")
    
    # Gerçekçi montaj sırası kontrolü
    def parca_aksiyon(parca, tak):
        if tak:
            # Mantıksal montaj sırası kontrolleri
            if parca == "Kapaklar" and not st.session_state.takimlar["Rotor"]:
                st.error("❌ İçine Rotoru (Mili) yerleştirmeden motor kapaklarını kapatamazsın!")
                return
            if parca == "Fan Pervanesi" and not st.session_state.takimlar["Kapaklar"]:
                st.error("❌ Arka kapağı takmadan fan pervanesini mile çakamazsın!")
                return
            if parca == "Muhafaza" and not st.session_state.takimlar["Fan Pervanesi"]:
                st.error("❌ Pervaneyi takmadan dış sac muhafaza kapağını vidalayamazsın!")
                return
            st.session_state.takimlar[parca] = True
        else:
            # Sökme sırası kontrolleri
            if parca == "Fan Pervanesi" and st.session_state.takimlar["Muhafaza"]:
                st.error("❌ Dış koruma muhafaza sacını sökmeden pervaneye ulaşamazsın!")
                return
            if parca == "Kapaklar" and st.session_state.takimlar["Fan Pervanesi"]:
                st.error("❌ Önce pervaneyi milden çekmen gerekiyor!")
                return
            if parca == "Rotor" and st.session_state.takimlar["Kapaklar"]:
                st.error("❌ Rulman kapakları cıvatalarla sıkılıyken rotoru çekip çıkaramazsın!")
                return
            st.session_state.takimlar[parca] = False
        st.rerun()

    for p, durum in st.session_state.takimlar.items():
        cc1, cc2 = st.columns([2, 1])
        cc1.write(f"▪️ **{p}** " + ("(📦 Yatakta/Takılı)" if durum else "(🛠️ Tezgahta Boşta)"))
        if durum:
            if cc2.button("Sök", key=f"sok_{p}", use_container_width=True):
                parca_aksiyon(p, False)
        else:
            if cc2.button("Monte Et", key=f"tak_{p}", use_container_width=True):
                parca_aksiyon(p, True)

    st.markdown("---")
    st.subheader("🚨 2. İş Güvenliği (LOTO)")
    st.write("_Elektrik panosunda çalışırken birinin yanlışlıkla şalteri kaldırmaması için asma kilidini tak/çıkar._")
    if st.session_state.loto_kilidi:
        if st.button("🔓 Kilidi Sök (Çalışmayı Bitirdim)", type="secondary", use_container_width=True):
            st.session_state.loto_kilidi = False
            st.rerun()
    else:
        if st.button("🔒 Panoyu Kilitle (Güvenli Çalışma)", type="primary", use_container_width=True):
            st.session_state.loto_kilidi = True
            st.session_state.ana_salter = False
            st.rerun()

# --- ORTA BÖLÜM: GERÇEKÇİ KLEMENS KUTUSU ---
with col_orta:
    st.subheader("🔌 3. Klemens Kutusu İç Görünümü")
    st.write("_Uçlara dokunarak köprü lamalarını tornavida ile sıkıştır. Şebeke uçları (L1, L2, L3) direkt alt sıraya bağlıdır._")
    
    # Mevcut Bağlantı Durumu
    if st.session_state.vida_secimleri:
        st.write("**Klemense Çakılan Lamalar/Kablolar:**")
        for v1, v2 in st.session_state.vida_secimleri:
            st.code(f"🔩 [{v1}]  <=========>  🔩 [{v2}]", language="text")
        if st.button("🛠️ Penseyle Tüm Köprüleri Sök", use_container_width=True):
            st.session_state.vida_secimleri = []
            st.session_state.aktif_vida = None
            st.rerun()
    else:
        st.info("Klemens kutusu bomboş. Bobin uçları açıkta duruyor.")

    if st.session_state.aktif_vida:
        st.warning(f"🔧 Penseyle **{st.session_state.aktif_vida}** ucunu tuttun. Köprünün diğer ucunu sıkmak için bir vida seç.")

    st.markdown("### `[ MOTOR KLEMENS BLOĞU ]`")
    
    def baglanti_yap(vida_adi):
        if st.session_state.loto_kilidi == False and st.session_state.ana_salter == True:
            st.error("⚡ Dur! Enerji altındaki klemense çıplak elle dokunamazsın! Çarpılırsın!")
            return
        if st.session_state.aktif_vida is None:
            st.session_state.aktif_vida = vida_adi
        else:
            if st.session_state.aktif_vida != vida_adi:
                st.session_state.vida_secimleri.append(tuple(sorted((st.session_state.aktif_vida, vida_adi))))
            st.session_state.aktif_vida = None
        st.rerun()

    # Klemens Görsel Arayüz Matrisi
    st.caption("**Üst Sıra (Sargı Çıkışları - Çapraz Etiketli)**")
    c_w2, c_u2, c_v2 = st.columns(3)
    if c_w2.button("W2 🔩", key="W2"): baglanti_yap("W2")
    if c_u2.button("U2 🔩", key="U2"): baglanti_yap("U2")
    if c_v2.button("V2 🔩", key="V2"): baglanti_yap("V2")

    # İç Sargı Gösterimi (Gerçekçi Akı Hatları)
    st.code("""
      │   │   │   (İç Bobin Sargıları)
      ├───┼───┤   U1-U2  /  V1-V2  /  W1-W2
      │   │   │   [Döküm Gövde İzolasyonu]
    """, language="text")

    st.caption("**Alt Sıra (Giriş Fazları L1 - L2 - L3 Bağlı)**")
    c_u1, c_v1, c_w1 = st.columns(3)
    if c_u1.button("U1 🔩", key="U1"): baglanti_yap("U1")
    if c_v1.button("V1 🔩", key="V1"): baglanti_yap("V1")
    if c_w1.button("W1 🔩", key="W1"): baglanti_yap("W1")

# --- SAĞ BÖLÜM: DIŞ TEST PANOSU VE ANALİZ ---
with col_sag:
    st.subheader("🖥️ 4. Güç Dağıtım ve Test Panosu")
    
    # Şalter ve Enerji Durumu
    if st.session_state.loto_kilidi:
        st.error("🔒 PANO KİLİTLİ: LOTO asma kilidi şalter mekanizmasını fiziksel olarak engelliyor! Enerji veremezsin.")
    else:
        if not st.session_state.ana_salter:
            if st.button("⚡ ANA ŞALTERİ YUKARI KALDIR", type="primary", use_container_width=True):
                st.session_state.ana_salter = True
                st.rerun()
        else:
            if st.button("🛑 ŞALTERİ AŞAĞI İNDİR (ACİL)", type="secondary", use_container_width=True):
                st.session_state.ana_salter = False
                st.rerun()

    st.markdown("---")
    st.subheader("📊 Motor Davranış Analizi")

    if st.session_state.ana_salter and not st.session_state.loto_kilidi:
        # Durum Değişkenleri
        mekanik_durum = all(st.session_state.takimlar.values())
        kablolar = set(st.session_state.vida_secimleri)
        
        # Yıldız ve Üçgen mantık setleri
        yildiz_mod_1 = {("U2", "W2"), ("U2", "V2")}.issubset(kablolar)
        yildiz_mod_2 = {("W2", "V2"), ("U2", "V2")}.issubset(kablolar)
        yildiz_ok = yildiz_mod_1 or yildiz_mod_2
        
        ucgen_ok = {("U1", "W2"), ("U2", "V1"), ("V2", "W1")}.issubset(kablolar)
        faz_faz_kisa_devre = any(kd in kablolar for kd in [("U1", "V1"), ("V1", "W1"), ("U1", "W1")])

        # Senaryo 1: Mekanik Eksiklik Arızaları
        if not st.session_state.takimlar["Rotor"]:
            st.error("💥 **BOŞTA ÇALIŞMA PATLAMASI!** Gövdenin içinde dönecek bir rotor yok! Stator sargıları saniyeler içinde aşırı indüklenerek yandı, atölyeyi duman kapladı.")
        elif not st.session_state.takimlar["Kapaklar"]:
            st.error("⚠️ **RULMAN YATAKSIZLIK ARIZASI:** Kapaklar takılmadığı için rotor yerinden fırladı ve statora çarparak sıkıştı. Aşırı akımdan sigorta attı!")
        
        # Senaryo 2: Elektriksel Bağlantı Hataları
        elif faz_faz_kisa_devre:
            st.error("🔥 **BÜYÜK PATLAMA:** Ana hat fazlarını (L1-L2-L3) klemens üzerinde birbirine köprülediniz! Atölyedeki ana dağıtım panosunun TMŞ şalteri gürültüyle düştü.")
        
        elif ucgen_ok:
            st.success("🔄 **MÜKEMMEL ÇALIŞMA (ÜÇGEN BAĞLANTI):** Motor nominal 380V gerilim altında tam tork ve güçle dönmeye başladı!")
            if not st.session_state.takimlar["Fan Pervanesi"]:
                st.warning("🚨 **DİKKAT:** Fan pervanesi takılı değil! Motor soğuyamıyor. Sargı sıcaklığı lineer yükseliyor, motor 5 dakika içinde yanacak!")
            st.metric(label="Rotor Devri", value="1475 RPM", delta="Nominal Hız")
            st.metric(label="Çekilen Akım ($I$)", value="11.4 Amper")
            
        elif yildiz_ok:
            st.success("⭐ **BAŞARILI KALKIŞ (YILDIZ BAĞLANTI):** Motor sarsıntısız ve düşük akımla kalkış yaptı, stabil bir şekilde dönüyor.")
            st.metric(label="Rotor Devri", value="1440 RPM", delta="-35 RPM Kayma")
            st.metric(label="Çekilen Akım ($I$)", value="6.5 Amper", delta="-4.9 A (Ekonomi)")
            
        elif len(kablolar) == 0:
            st.warning("🔇 **AKIM SIFIR:** Klemensler boşta olduğu için devreden akım geçmiyor. Motorda tık yok.")
        
        else:
            st.error("⚡ **FAZ DENGESİZLİĞİ / AŞIRI UĞULTU:** Köprüleri rastgele veya eksik bağladınız. Motor dönmüyor, yüksek sesle uğulduyor ve şebekeden 40 Amper bloke rotor akımı çekiyor!")
            st.metric(label="Çekilen Akım", value="42.0 A", delta="TEHLİKELİ SEVİYE")

    else:
        st.info("Tezgâhta elektrik yok. İş emri adımlarını takip ederek mekanik parçaları birleştirin ve klemens kutusunu hazır hale getirin.")
