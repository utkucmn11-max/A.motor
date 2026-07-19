import streamlit as st

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Asenkron Motor Simülatörü", layout="wide")

st.title("⚙️ 3 Fazlı Asenkron Motor Montaj & Klemens Bağlantı Simülatörü")
st.write("Bu simülatör ile motor parçalarını söküp takabilir, klemens kutusunda Yıldız/Üçgen bağlantı yapabilir ve motoru test edebilirsiniz.")

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "Montaj / Demontaj"
if "motor_state" not in st.session_state:
    st.session_state.motor_state = {
        "fan_kapagi": True,
        "fan": True,
        "arka_kapak": True,
        "rotor": True,
        "on_kapak": True,
        "gövde_ve_stator": True
    }
if "klemens_kopruleri" not in st.session_state:
    st.session_state.klemens_kopruleri = "Yok"
if "enerji_verildi" not in st.session_state:
    st.session_state.enerji_verildi = False

# --- KENAR ÇUBUĞU (NAVİGASYON) ---
st.sidebar.header("📍 Simülasyon Adımları")
st.session_state.step = st.sidebar.radio(
    "Gitmek istediğiniz adımı seçin:",
    ["Montaj / Demontaj", "Klemens Kutusu Bağlantısı", "Motor Test & Çalıştırma"]
)

# --- ADIM 1: MONTAJ / DEMONTAJ ---
if st.session_state.step == "Montaj / Demontaj":
    st.header("🛠️ Motor Mekanik Montaj / Demontaj")
    st.write("Motoru sökmek için dıştan içe doğru parçaları kaldırın. Toplamak için tam tersi sırayı takip edin.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Parça Kontrol Paneli")
        # Sökme/Takma butonları (Mantıksal sıra kontrolü ile)
        # Fan Kapağı
        if st.session_state.motor_state["fan_kapagi"]:
            if st.button("❌ Fan Kapağını Sök"):
                st.session_state.motor_state["fan_kapagi"] = False
                st.rerun()
        else:
            if st.button("✅ Fan Kapağını Tak") and st.session_state.motor_state["fan"]:
                st.session_state.motor_state["fan_kapagi"] = True
                st.rerun()
                
        # Fan
        if st.session_state.motor_state["fan"]:
            if st.button("❌ Pervaneyi (Fan) Sök") and not st.session_state.motor_state["fan_kapagi"]:
                st.session_state.motor_state["fan"] = False
                st.rerun()
        else:
            if st.button("✅ Pervaneyi (Fan) Tak") and st.session_state.motor_state["arka_kapak"]:
                st.session_state.motor_state["fan"] = True
                st.rerun()
                
        # Arka Kapak
        if st.session_state.motor_state["arka_kapak"]:
            if st.button("❌ Arka Kapağı Sök") and not st.session_state.motor_state["fan"]:
                st.session_state.motor_state["arka_kapak"] = False
                st.rerun()
        else:
            if st.button("✅ Arka Kapağı Tak") and st.session_state.motor_state["rotor"]:
                st.session_state.motor_state["arka_kapak"] = True
                st.rerun()
                
        # Rotor ve Ön Kapak
        if st.session_state.motor_state["rotor"]:
            if st.button("❌ Rotoru (Mil dahil) Çıkar") and not st.session_state.motor_state["arka_kapak"]:
                st.session_state.motor_state["rotor"] = False
                st.rerun()
        else:
            if st.button("✅ Rotoru Statora Yerleştir"):
                st.session_state.motor_state["rotor"] = True
                st.rerun()

    with col2:
        st.subheader("Motorun Anlık Durumu (Görsel Model)")
        # Motorun iç/dış yapısını temsil eden dinamik text tabanlı şema
        st.code(f"""
        [ R E D Ü K S İ Y O N  /  M İ L ]
                       ||
        [Ön Kapak]    : {"MONTAJLI  🟢" if st.session_state.motor_state["on_kapak"] else "SÖKÜLMÜŞ 🔴"}
        [Stator/Gövde]: {"MONTAJLI  🟢" if st.session_state.motor_state["gövde_ve_stator"] else "SÖKÜLMÜŞ 🔴"}
        [Rotor (İç) ] : {"İÇERİDE   🟢" if st.session_state.motor_state["rotor"] else "ÇIKARILMIŞ 🔴"}
        [Arka Kapak]  : {"MONTAJLI  🟢" if st.session_state.motor_state["arka_kapak"] else "SÖKÜLMÜŞ 🔴"}
        [Pervane/Fan] : {"MONTAJLI  🟢" if st.session_state.motor_state["fan"] else "SÖKÜLMÜŞ 🔴"}
        [Fan Kapağı]  : {"MONTAJLI  🟢" if st.session_state.motor_state["fan_kapagi"] else "SÖKÜLMÜŞ 🔴"}
        """)
        
        # Tamamen sökülme veya toplanma durum kontrolü
        is_assembled = all(st.session_state.motor_state.values())
        if is_assembled:
            st.success("🎉 Motor tamamen monte edildi! Klemens kutusu bağlantısına geçebilirsiniz.")
        else:
            st.warning("⚠️ Motor şu an demonte durumda. Test etmeden önce tüm parçaları sırasıyla birleştirin.")

# --- ADIM 2: KLEMENS KUTUSU BAĞLANTISI ---
elif st.session_state.step == "Klemens Kutusu Bağlantısı":
    st.header("🔌 Klemens Kutusu ve Köprü Bağlantıları")
    st.write("3 fazlı motorun bobin uçları (U1, V1, W1 ve W2, U2, V2) klemens kutusuna çıkarılmıştır. Şebeke voltajına göre uygun köprülemeyi seçin.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Bağlantı Tipi Seçimi")
        kopru = st.radio(
            "Klemens köprülerini nasıl bağlamak istersiniz?",
            ["Yok (Bağlantısız)", "Yıldız Bağlantı (Köprü U2-V2-W2 arasında)", "Üçgen Bağlantı (Köprüler U1-W2, V1-U2, W1-V2 arasında)"]
        )
        
        if kopru == "Yok (Bağlantısız)":
            st.session_state.klemens_kopruleri = "Yok"
        elif "Yıldız" in kopru:
            st.session_state.klemens_kopruleri = "Yildiz"
        elif "Üçgen" in kopru:
            st.session_state.klemens_kopruleri = "Ucgen"

    with col2:
        st.subheader("Klemens Görünümü")
        
        if st.session_state.klemens_kopruleri == "Yok":
            st.code("""
            [W2]   [U2]   [V2]  <- Bobin Çıkışları
             |      |      |
            [U1]   [V1]   [W1]  <- Şebeke Girişleri (L1, L2, L3)
            """)
            st.info("ℹ️ Köprü bulunmuyor. Bu durumda motora enerji verilirse motor çalışmaz ve koruma atar.")
            
        elif st.session_state.klemens_kopruleri == "Yildiz":
            st.code("""
            [W2]===[U2]===[V2]  <- Üst uçlar kısa devre (KÖPRÜ)
             |      |      |
            [U1]   [V1]   [W1]  <- Şebeke Girişleri (L1, L2, L3)
            """)
            st.success("⭐ Yıldız bağlantı yapıldı. Yüksek voltaj şebekelerinde (örn. 380V/660V motorun 380V şebekede çalışması) tercih edilir.")
            
        elif st.session_state.klemens_kopruleri == "Ucgen":
            st.code("""
            [W2]   [U2]   [V2]
             ||     ||     ||   <- Karşılıklı dikey köprüler
            [U1]   [V1]   [W1]  <- Şebeke Girişleri (L1, L2, L3)
            """)
            st.success("🔺 Üçgen bağlantı yapıldı. Düşük voltaj şebekelerinde veya motor nominal geriliminin tam alındığı durumlarda tercih edilir.")

# --- ADIM 3: MOTOR TEST & ÇALIŞTIRMA ---
elif st.session_state.step == "Motor Test & Çalıştırma":
    st.header("⚡ Motor Test ve Enerji Paneli")
    
    # Mekanik ve elektriksel kontrollerin yapılması
    motor_toplu = all(st.session_state.motor_state.values())
    baglanti = st.session_state.klemens_kopruleri
    
    st.subheader("Durum Raporu")
    c1, c2 = st.columns(2)
    with c1:
        if motor_toplu:
            st.success("✅ Mekanik Durum: Motor tamamen toplandı.")
        else:
            st.error("❌ Mekanik Durum: Motor parçaları eksik! (Demontaj adımına dönüp motoru toplayın)")
            
    with c2:
        if baglanti != "Yok":
            st.success(f"✅ Elektriksel Durum: Klemens kutusunda '{baglanti}' köprüsü kurulu.")
        else:
            st.error("❌ Elektriksel Durum: Klemens kutusunda köprü yok!")

    st.write("---")
    st.subheader("Enerji Kontrolü")
    
    # Enerji verme butonu
    if not st.session_state.enerji_verildi:
        if st.button("🔌 Şebeke Şalterini Kaldır (Enerji Ver)"):
            st.session_state.enerji_verildi = True
            st.rerun()
    else:
        if st.button("🛑 Şalteri İndir (Enerjiyi Kes)"):
            st.session_state.enerji_verildi = False
            st.rerun()
            
    # Simülasyon Çıktısı Ekranı
    st.subheader("🖥️ Motor Çalışma Analizi")
    
    if st.session_state.enerji_verildi:
        if not motor_toplu:
            st.error("💥 GÜVENLİK ALARMI: Motor parçaları açıkta veya rotor tam yerleşmediği için mekanik sıkışma yaşandı. Sigortalar ATTI!")
        elif baglanti == "Yok":
            st.warning("🔇 Motor uğulduyor ama dönmüyor: Klemens kutusunda devre tamamlanmadı (bobin uçları açıkta). Akım çekilemiyor.")
        elif baglanti == "Yildiz":
            st.success("🔄 MOTOR DÖNÜYOR (Yıldız Modu): Motor kalkış akımını düşük tutarak sarsıntısız bir şekilde çalışmaya başladı. Nominal hızda stabil dönüyor.")
            st.metric(label="Motor Hızı (RPM)", value="1450 RPM", delta="Yıldız Bağlantı")
            st.balloons()
        elif baglanti == "Ucgen":
            st.success("⚡ MOTOR DÖNÜYOR (Üçgen Modu): Motor tam güç ve nominal tork ile çalışıyor. Yüksek kalkış akımı çekildi.")
            st.metric(label="Motor Hızı (RPM)", value="1480 RPM", delta="Üçgen Bağlantı - Tam Güç")
            st.balloons()
    else:
        st.info("💤 Şebekede enerji yok. Motor duruyor.")