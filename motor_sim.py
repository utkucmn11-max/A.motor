import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Sayfa yapılandırması
st.set_page_config(page_title="Manuel Asenkron Motor Simülatörü", layout="wide")

st.title("⚙️ Manuel Asenkron Motor Montaj & Klemens Bağlantı Simülatörü")
st.write("Bu simülatörde kararları ve bağlantıları tamamen **manuel** olarak siz yaparsınız. Yanlış bağlantı motoru yakabilir!")

# --- GÖRSEL KAYNAKLARI (Gerçekçi Şemalar ve Fotoğraflar) ---
# Gerçekçi motor görseli ve klemens kutusu altyapısı için telifsiz/açık kaynaklı eğitim görselleri
MOTOR_IMG_URL = "https://images.unsplash.com/photo-1617791160505-6f006e121980?q=80&w=600&auto=format&fit=crop" # Temsili Endüstriyel Motor
KLEMENS_BG_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Terminal_bloks_01.jpg/640px-Terminal_bloks_01.jpg" # Gerçek Klemens Bloğu

@st.cache_data
def load_image(url):
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except:
        # İnternet olmaması durumunda yedek boş görsel
        return Image.new('RGB', (400, 300), color = '#7F8C8D')

motor_img = load_image(MOTOR_IMG_URL)

# --- SESSION STATE (DURUM YÖNETİMİ) ---
if "mekanik_parcalar" not in st.session_state:
    st.session_state.mekanik_parcalar = {
        "Gövde ve Stator": True,
        "Rotor (Mil)": False,
        "Ön ve Arka Kapaklar": False,
        "Soğutma Fanı (Pervane)": False,
        "Fan Muhafaza Kapağı": False
    }

if "kablolar" not in st.session_state:
    st.session_state.kablolar = []  # Kullanıcının manuel yaptığı bağlantıları tutar: Örn: [("W2", "U2"), ("U2", "V2")]

if "secili_vida" not in st.session_state:
    st.session_state.secili_vida = None

if "salter" not in st.session_state:
    st.session_state.salter = False

# --- SOL PANEL: MEKANİK MONTAJ (MANUEL) ---
col_mekanik, col_klemens, col_kontrol = st.columns([1, 1.5, 1])

with col_mekanik:
    st.header("🛠️ 1. Mekanik Montaj")
    st.image(motor_img, caption="Endüstriyel Asenkron Motor", use_container_width=True)
    
    st.subheader("Parçaları Manuel Tak/Sök")
    st.info("Motorun dönmesi için mekanik parçaların sırasıyla doğru takılması gerekir.")
    
    # Manuel olarak sırayla takılması için butonlar
    for parca, takili mi in st.session_state.mekanik_parcalar.items():
        durum_rengi = "🟢 Takılı" if takili mi else "🔴 Sökük"
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            st.write(f"**{parca}** ({durum_rengi})")
        with col_btn2:
            if takili mi:
                if st.button("Sök", key=f"sok_{parca}"):
                    st.session_state.mekanik_parcalar[parca] = False
                    st.rerun()
            else:
                if st.button("Tak", key=f"tak_{parca}"):
                    st.session_state.mekanik_parcalar[parca] = True
                    st.rerun()

# --- ORTA PANEL: MANUEL KLEMENS BAĞLANTISI ---
with col_klemens:
    st.header("🔌 2. Manuel Klemens Bağlantısı")
    st.write("Köprü atmak veya kablo bağlamak için önce **1. vidayı**, sonra bağlamak istediğiniz **2. vidayı** seçin.")
    
    # Vidaların listesi
    ust_siralar = ["W2", "U2", "V2"]
    alt_siralar = ["U1", "V1", "W1"]
    
    # Mevcut bağlantıları listeleme ve temizleme
    st.subheader("Yapılan Bağlantılar (Köprüler):")
    if not st.session_state.kablolar:
        st.write("_Henüz bir köprü bağlantısı yapmadınız._")
    else:
        for idx, (v1, v2) in enumerate(st.session_state.kablolar):
            st.code(f"🔗 Köprü: {v1}  <--->  {v2}")
        if st.button("🧹 Tüm Bağlantıları Sök / Temizle"):
            st.session_state.kablolar = []
            st.session_state.secili_vida = None
            st.rerun()

    # Manuel Seçim Arayüzü
    st.markdown("---")
    st.write("**Bağlantı Kurma Paneli:**")
    
    if st.session_state.secili_vida:
        st.warning(f"Bağlantı Başlangıcı Seçildi: **{st.session_state.secili_vida}**. Şimdi bağlanacak ikinci vidayı seçin.")
    else:
        st.info("Lütfen bağlantı kurmak için bir vidaya tıklayın.")

    # Klemens Kutusu Matrisi (Görsel Butonlar)
    st.write("**[ KLEMENS KUTUSU VİDALARI ]**")
    
    # Üst Sıra Vidalar (W2, U2, V2)
    c_w2, c_u2, c_v2 = st.columns(3)
    with c_w2: 
        if st.button("🔩 W2", use_container_width=True): 
            st.session_state.secili_vida = "W2" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "W2")) or None)
            st.rerun()
    with c_u2: 
        if st.button("🔩 U2", use_container_width=True): 
            st.session_state.secili_vida = "U2" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "U2")) or None)
            st.rerun()
    with c_v2: 
        if st.button("🔩 V2", use_container_width=True): 
            st.session_state.secili_vida = "V2" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "V2")) or None)
            st.rerun()

    st.write(" \n ") # Boşluk (Bobinleri simüle etmek için dikey mesafe)
    
    # Alt Sıra Vidalar (U1, V1, W1)
    c_u1, c_v1, c_w1 = st.columns(3)
    with c_u1: 
        if st.button("🔩 U1", use_container_width=True): 
            st.session_state.secili_vida = "U1" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "U1")) or None)
            st.rerun()
    with c_v1: 
        if st.button("🔩 V1", use_container_width=True): 
            st.session_state.secili_vida = "V1" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "V1")) or None)
            st.rerun()
    with c_w1: 
        if st.button("🔩 W1", use_container_width=True): 
            st.session_state.secili_vida = "W1" if not st.session_state.secili_vida else (st.session_state.kablolar.append((st.session_state.secili_vida, "W1")) or None)
            st.rerun()

# --- SAĞ PANEL: KONTROL PANELİ VE ANALİZ ---
with col_kontrol:
    st.header("⚡ 3. Enerji & Test")
    
    # Şalter Kontrolü
    st.write("Bağlantılarınız bittiyse şalteri manuel olarak kaldırın:")
    if not st.session_state.salter:
        if st.button("🛑 ŞALTER KAPALI (Açmak için Tıkla)", type="primary", use_container_width=True):
            st.session_state.salter = True
            st.rerun()
    else:
        if st.button("🟢 ŞALTER AÇIK (Kapatmak için Tıkla)", type="secondary", use_container_width=True):
            st.session_state.salter = False
            st.rerun()

    st.subheader("📋 Simülasyon Sonucu")
    
    if st.session_state.salter:
        # 1. Kontrol: Mekanik Durum
        mekanik_tam = all(st.session_state.mekanik_parcalar.values())
        
        # 2. Kontrol: Elektriksel Bağlantı Analizi (Kullanıcının yaptığı manuel kombinasyonlar)
        baglantilar = st.session_state.kablolar
        
        # Set mantığı ile çift yönlü eşleşmeleri kontrol etmek için normalize ediyoruz
        norm_baglanti = set(tuple(sorted(p)) for p in baglantilar)
        
        # Yıldız Bağlantı Kontrolü (W2-U2 ve U2-V2 veya W2-V2 köprülenmiş olmalı)
        yildiz_kopruleri = {("U2", "W2"), ("U2", "V2")}
        is_yildiz = yildiz_kopruleri.issubset(norm_baglanti) or {("W2", "V2"), ("U2", "V2")}.issubset(norm_baglanti)
        
        # Üçgen Bağlantı Kontrolü (W2-U1, U2-V1, V2-W1 dikey köprüleri)
        ucgen_kopruleri = {("U1", "W2"), ("U2", "V1"), ("V2", "W1")}
        is_ucgen = ucgen_kopruleri.issubset(norm_baglanti)

        # Kapsamlı Hata/Kısa Devre Senaryoları (Örn: Giriş fazlarını kendi arasında kısa devre etmek)
        kisa_devre_giris = {("U1", "V1"), ("V1", "W1"), ("U1", "W1")}
        is_kisa_devre = any(kd in norm_baglanti for kd in kisa_devre_giris)

        if not mekanik_tam:
            st.error("💥 **MEKANİK ARIZA!** Motorun parçaları (Rotor, kapaklar veya fan) tam takılmadan enerji verdiniz! Motor yüksek gürültü çıkardı, rulmanlar dağıldı ve kilitlendi.")
        elif is_kisa_devre:
            st.error("🔥 **PATLAMA / KISA DEVRE!** Ana şebeke girişlerini (U1-V1-W1) birbirine bağladınız. Panoda büyük bir patlama gerçekleşti ve ana sigortalar attı!")
        elif is_ucgen:
            st.success("🔄 **BAŞARILI: MOTOR DÖNÜYOR (ÜÇGEN BAĞLANTI)**")
            st.info("Motor nominal geriliminde tam tork ile dönüyor. Manuel yaptığınız dikey köprüler doğru!")
            st.metric(label="Rotor Devri", value="1480 RPM")
        elif is_yildiz:
            st.success("🔄 **BAŞARILI: MOTOR DÖNÜYOR (YILDIZ BAĞLANTI)**")
            st.info("Motor düşük akım çekerek yumuşak bir kalkış yaptı ve güvenle dönüyor. Üst yatay köprünüz doğru!")
            st.metric(label="Rotor Devri", value="1440 RPM")
        elif len(norm_baglanti) == 0:
            st.warning("🔇 **AKIM YOK:** Klemens kutusunda hiçbir köprü yok. Motor sargılarından akım geçmediği için hiçbir tepki vermiyor.")
        else:
            st.error("⚠️ **HATA: YANLIŞ BAĞLANTI!** Klemense rastgele köprüler attınız. Sargılardan dengesiz akım geçti, motor aşırı ısındı ve dumanlar çıkarmaya başladı (Motor Yanması Riski!).")
            
    else:
        st.info("Sistemde elektrik yok. Güvenle montaj yapabilir ve vidaları köprüleyebilirsiniz.")
