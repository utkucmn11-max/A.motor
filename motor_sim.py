import streamlit as st
import time
import pandas as pd
import numpy as np

st.set_page_config(page_title="Otomatik Yıldız-Üçgen Simülatörü", layout="wide")

st.title("⚡ Otomatik Yıldız-Üçgen Yol Verme & Kumanda Panosu Simülatörü")
st.write("Bu simülasyonda motor dönerken bağlantıların pano içerisindeki kontaktörler ve zaman rölesi ile nasıl otomatik değiştirildiğini inceleyebilirsiniz.")

# --- INITIALIZATION ---
if "pano_enerji" not in st.session_state:
    st.session_state.pano_enerji = False
if "sim_durum" not in st.session_state:
    st.session_state.sim_durum = "DURUYOR" # DURUYOR, YILDIZ, GECIS, UCGEN
if "gecen_sure" not in st.session_state:
    st.session_state.gecen_sure = 0.0

# --- PARAMETRE AYARLARI (SOL PANEL) ---
col_sol, col_orta, col_sag = st.columns([1, 1.2, 1.3])

with col_sol:
    st.subheader("🎛️ Pano Ayarları")
    zaman_ayari = st.slider("Zaman Rölesi Süresi (Saniye)", 2, 8, 5)
    motor_yuku = st.slider("Motor Mekanik Yükü (Nm)", 0, 40, 15)
    
    st.markdown("---")
    st.subheader("🧱 Pano İçi Cihazlar")
    
    # Kontaktörlerin durumuna göre renkli gösterge
    def kontaktor_isigi(durum):
        return "🟢 ÇEKTİ (KAPALI)" if durum else "🔴 BIRAKTI (AÇIK)"
    
    k_ana = st.session_state.sim_durum in ["YILDIZ", "GECIS", "UCGEN"]
    k_yildiz = st.session_state.sim_durum == "YILDIZ"
    k_ucgen = st.session_state.sim_durum == "UCGEN"
    
    st.write(f"**[M] Ana Kontaktör:** {kontaktor_isigi(k_ana)}")
    st.write(f"**[Y] Yıldız Kontaktörü:** {kontaktor_isigi(k_yildiz)}")
    st.write(f"**[D] Üçgen Kontaktörü:** {kontaktor_isigi(k_ucgen)}")

# --- ANLIK KUMANDA ŞEMASI VE BUTONLAR (ORTA PANEL) ---
with col_orta:
    st.subheader("🕹️ Operatör Kumanda Paneli")
    
    c_btn1, c_btn2 = st.columns(2)
    start_basildi = c_btn1.button("🟢 START (Başlat)", type="primary", use_container_width=True)
    stop_basildi = c_btn2.button("🔴 STOP (Durdur)", type="secondary", use_container_width=True)
    
    if start_basildi and st.session_state.sim_durum == "DURUYOR":
        st.session_state.pano_enerji = True
        st.session_state.sim_durum = "YILDIZ"
        st.session_state.gecen_sure = 0.0
        st.rerun()
        
    if stop_basildi:
        st.session_state.pano_enerji = False
        st.session_state.sim_durum = "DURUYOR"
        st.session_state.gecen_sure = 0.0
        st.rerun()

    st.markdown("---")
    st.subheader("🖥️ Akış Şeması Görünümü")
    
    # Simülasyon durumuna göre dinamik ASCII şema
    if st.session_state.sim_durum == "DURUYOR":
        st.code("""
        [ŞEBEKE] ──X── [Ana Kontaktör] ────> [Motor Sargı Girişleri: U1, V1, W1]
                                                    
        [KÖPRÜ YOK] ──X── [Yıldız Kont.] ──> [Motor Çıkışları: W2, U2, V2]
        [KÖPRÜ YOK] ──X── [Üçgen Kont.]  ──> [Motor Çıkışları: W2, U2, V2]
         STATUS: MOTOR DURUYOR - GÜVENLİ DURUM
        """, language="text")
    elif st.session_state.sim_durum == "YILDIZ":
        st.code(f"""
        [ŞEBEKE] ═════ [Ana Kontaktör] ════> [Motor Sargı Girişleri: U1, V1, W1]
                                                    
        [YILDIZ] ═════ [Yıldız Kont.] ════> [W2 + U2 + V2 KISA DEVRE EDİLDİ] ⭐
        [AÇIK  ] ──X── [Üçgen Kont.]
         STATUS: YILDIZ KALKIŞ YAPILIYOR... ZAMAN RÖLESİ: {zaman_ayari - int(st.session_state.gecen_sure)} sn kaldı!
        """, language="text")
    elif st.session_state.sim_durum == "UCGEN":
        st.code("""
        [ŞEBEKE] ═════ [Ana Kontaktör] ════> [Motor Sargı Girişleri: U1, V1, W1]
                                                    
        [AÇIK  ] ──X── [Yıldız Kont.]
        [ÜÇGEN ] ═════ [Üçgen Kont.]  ════> [U1-W2 // V1-U2 // W1-V2 BAĞLANDI] 🔺
         STATUS: MOTOR TAM GÜÇ ÜÇGEN MODUNDA ÇALIŞIYOR!
        """, language="text")

# --- GERÇEK ZAMANLI TELEMETRİ VE GRAFİK (SAĞ PANEL) ---
with col_sag:
    st.subheader("📈 Gerçek Zamanlı Akım ve Hız Analizi")
    
    if st.session_state.pano_enerji:
        # Zaman simülasyonunu tetiklemek için Streamlit bileşeni boşluğu
        placeholder = st.empty()
        
        # Grafik için boş listeler
        zaman_serisi = []
        akim_serisi = []
        hiz_serisi = []
        
        # 40 adımlık bir zaman simülasyonu döngüsü (Toplamda zaman rölesi süresi + 3 saniye üçgen izleme)
        toplam_adim = (zaman_ayari + 3) * 4
        
        for adim in range(toplam_adim):
            t = adim * 0.25
            zaman_serisi.append(t)
            st.session_state.gecen_sure = t
            
            if t < zaman_ayari:
                st.session_state.sim_durum = "YILDIZ"
                # Yıldız modu fiziği: Akım 3-4 Amperle başlar, hızlandıkça düşer
                anlik_hiz = 1440 * (1 - np.exp(-t/1.2))
                anlik_akim = 15.0 * np.exp(-t/1.0) + 4.5 + (motor_yuku * 0.1)
            else:
                st.session_state.sim_durum = "UCGEN"
                # Üçgen modu fiziği: Geçiş anında ani akım sıçraması (Pik akımı)
                gecis_t = t - zaman_ayari
                anlik_hiz = 1480 - (motor_yuku * 0.5) * (1 - np.exp(-gecis_t))
                # İlk salisede akım fırlar, sonra nominal üçgen akımına oturur
                anlik_akim = 28.0 * np.exp(-gecis_t/0.3) + 8.0 + (motor_yuku * 0.2)
                
            akim_serisi.append(anlik_akim)
            hiz_serisi.append(anlik_hiz)
            
            # Canlı Metrik Güncelleme
            with placeholder.container():
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("Anlık Hat Akımı", f"{round(anlik_akim, 1)} Amper")
                c_m2.metric("Motor Devri", f"{int(anlik_hiz)} RPM")
                
                # Dinamik Grafik
                df_grafik = pd.DataFrame({
                    "Zaman (sn)": zaman_serisi,
                    "Şebekeden Çekilen Akım (A)": akim_serisi,
                    "Rotor Hızı (RPM)": hiz_serisi
                }).set_index("Zaman (sn)")
                
                st.line_chart(df_grafik[["Şebekeden Çekilen Akım (A)"]])
            
            time.sleep(0.08) # Görsel akış için hafif gecikme
            
        st.success("🎉 Geçiş Başarıyla Tamamlandı! Akım grafiğindeki ani zıplamaya (pik) dikkat edin. İşte endüstrideki yıldız-üçgen geçişinin tam elektriksel karakteristiği budur.")
        st.session_state.gecen_sure = zaman_ayari
    else:
        st.info("Pano kapalı. Motorun kalkışını ve Yıldız'dan Üçgen'e geçiş anındaki akım grafiğini görmek için sol taraftan START butonuna basın.")
