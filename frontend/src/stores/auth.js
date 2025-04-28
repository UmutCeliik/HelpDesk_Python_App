// frontend/src/stores/auth.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router' // Yönlendirme için (action içinde)
import { jwtDecode } from 'jwt-decode' // Token içeriğini çözmek için

// Auth Service URL'si
const AUTH_SERVICE_URL = 'http://127.0.0.1:8002';

// 'auth' isimli store'u tanımla
export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  // Token'ı ve kullanıcı bilgilerini tutacak reaktif referanslar
  const token = ref(null) // Başlangıçta token yok
  const user = ref(null)  // Başlangıçta kullanıcı bilgisi yok

  // --- Getters ---
  // Kullanıcının login olup olmadığını kontrol eden computed property
  const isAuthenticated = computed(() => !!token.value)
  // Kullanıcı rolünü döndüren computed property (varsa)
  const userRole = computed(() => user.value?.role || null)
  // Kullanıcı ID'sini döndüren computed property (varsa)
  const userId = computed(() => user.value?.user_id || null)

  // --- Actions ---

  /**
   * Verilen token'ı çözer ve kullanıcı bilgilerini state'e kaydeder.
   */
  function decodeAndStoreUser(accessToken) {
      try {
          const decoded = jwtDecode(accessToken);
          console.log('Decoded Token:', decoded);
          // user state'ini güncelle (ihtiyaç duyulan alanları al)
          user.value = {
              email: decoded.sub, // 'sub' genellikle e-postayı içerir
              user_id: decoded.user_id,
              role: decoded.role
          };
          token.value = accessToken; // Token'ı state'e kaydet
      } catch (error) {
          console.error("Token decode edilemedi:", error);
          // Hatalı token durumunda state'i temizle
          token.value = null;
          user.value = null;
      }
  }

  /**
   * API'ye login isteği gönderir, başarılı olursa token'ı ve kullanıcıyı saklar.
   */
  async function login(email, password) {
    // Form verisini hazırla
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    try {
      const response = await axios.post(
        `${AUTH_SERVICE_URL}/auth/token`,
        params,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );

      const accessToken = response.data.access_token;
      if (accessToken) {
        // Token'ı decode et ve state'i güncelle
        decodeAndStoreUser(accessToken);
        console.log('Login başarılı, state güncellendi.');
        return true; // Başarı durumunu döndür
      }
      return false; // Token gelmediyse başarısız
    } catch (error) {
      console.error('Store login action hatası:', error.response || error.message);
      // Başarısız login sonrası state'i temizle
      token.value = null;
      user.value = null;
      throw error; // Hatanın bileşen tarafından yakalanabilmesi için tekrar fırlat
    }
  }

  /**
   * Kullanıcıyı logout yapar, state'i temizler.
   */
  function logout() {
    console.log('Logout yapılıyor, state temizleniyor.');
    token.value = null;
    user.value = null;
    // localStorage'dan da temizleyelim (eğer önceki adımdan kaldıysa)
    localStorage.removeItem('accessToken');
    // Login sayfasına yönlendirme burada veya bileşen içinde yapılabilir
    // const router = useRouter(); // Action içinde router kullanmak biraz tartışmalı olabilir
    // router.push('/login');
  }

  // Store'dan dışarıya açılacak state, getters ve actions
  return {
      token,
      user,
      isAuthenticated,
      userRole,
      userId,
      login,
      logout,
      decodeAndStoreUser // Belki dışarıdan decode gerekirse diye açılabilir
    }
})