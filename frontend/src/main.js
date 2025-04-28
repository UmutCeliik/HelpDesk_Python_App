// Temel Vue ve Stil dosyaları
import './assets/main.css'; // Genel stilleriniz
import { createApp } from 'vue';

// Pinia State Management
import { createPinia } from 'pinia';
import { useAuthStore } from './stores/auth'; // Auth store'unuz

// Vue Router
import App from './App.vue';
import router from './router';

// Axios API İstemcisi
import apiClient from './api/axios';

// Vuetify Kurulumu
import 'vuetify/styles'; // Vuetify temel stilleri
import { createVuetify } from 'vuetify'; // Vuetify oluşturucu
import * as components from 'vuetify/components'; // Tüm Vuetify bileşenleri
import * as directives from 'vuetify/directives'; // Tüm Vuetify direktifleri
import '@mdi/font/css/materialdesignicons.css'; // Material Design İkonları (Gerekli)

// Vuetify instance'ını oluştur
const vuetify = createVuetify({
  components, // Bileşenleri ekle
  directives, // Direktifleri ekle
  icons: {
    defaultSet: 'mdi', // Varsayılan ikon seti olarak mdi kullan
  },
  theme: {
    defaultTheme: 'light', // veya 'dark'
    themes: {
      light: {
        colors: {
          primary: '#1976D2', // Örnek primary renk
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
    },
  },
});

// Vue uygulamasını oluştur
const app = createApp(App);

// Pinia'yı oluştur ve kullan
const pinia = createPinia();
app.use(pinia);

// ÖNEMLİ: Pinia store'u, interceptor'larda kullanılabilmesi için
// app.use(pinia) çağrısından SONRA tanımlanmalı.
// Ancak, interceptor'lar app mount edilmeden ÖNCE tanımlanmalı.
// Bu yüzden authStore'u burada tekrar tanımlamaya gerek yok,
// interceptor içindeki import yeterli olacaktır.
// const authStore = useAuthStore(); // Bu satıra burada GEREK YOK

// Vue Router'ı kullan
app.use(router);

// Vuetify'ı kullan
app.use(vuetify);

// --- Axios Interceptor'lar (Değişiklik Yok) ---
// İstek (Request) Interceptor'ı
apiClient.interceptors.request.use(
  (config) => {
    // Pinia store'u interceptor içinde import ederek kullanın
    const authStoreForInterceptor = useAuthStore();
    const token = authStoreForInterceptor.token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('Interceptor: Authorization header eklendi.');
    } else {
      console.log('Interceptor: Token bulunamadı, header eklenmedi.');
    }
    return config;
  },
  (error) => {
    console.error('Axios request interceptor hatası:', error);
    return Promise.reject(error);
  }
);

// Yanıt (Response) Interceptor'ı
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    console.error('Axios response interceptor hatası:', error.response);

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      console.log('Interceptor: 401 hatası alındı, logout yapılıyor.');

      // Pinia store'u interceptor içinde import ederek kullanın
      const authStoreForInterceptor = useAuthStore();
      authStoreForInterceptor.logout();

      // Yönlendirme için navigation guard kullanmak daha iyi bir pratik olacaktır.
      // Şimdilik sadece logout yapıyoruz. Gerekirse router'ı import edip
      // burada yönlendirme de yapılabilir ama tavsiye edilmez.
      // import router from './router'; // Gerekirse import edin
      // router.push('/login');

      return Promise.reject(new Error('Oturum sonlandı veya geçersiz. Lütfen tekrar giriş yapın.'));
    }

    return Promise.reject(error);
  }
);
// --- Axios Interceptor'lar Sonu ---

// Uygulamayı mount et
app.mount('#app');
