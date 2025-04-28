<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// E-posta ve şifre için reaktif değişkenler
const email = ref('');
const password = ref('');
const errorMessage = ref(''); // Hata mesajı için
const isLoading = ref(false); // Yüklenme durumu için

const router = useRouter();
const authStore = useAuthStore();

// Login işlemini yapacak asenkron fonksiyon
async function handleLogin() {
  errorMessage.value = ''; // Önceki hatayı temizle
  isLoading.value = true; // Yükleniyor durumunu başlat

  try {
    // Store'daki login action'ını çağır
    const loginSuccess = await authStore.login(email.value, password.value);

    if (loginSuccess) {
      // *** Başarılı login sonrası yönlendirme BURADA DEĞİŞTİRİLDİ ***
      router.push('/'); // Ana panele (Dashboard) yönlendir
    } else {
      // Bu durum genellikle token dönmezse oluşur (beklenmedik)
      errorMessage.value = 'Giriş sırasında token alınamadı.';
    }
  } catch (error) {
    // Store action'ı hata fırlattığında burası çalışır
    console.error('LoginView handleLogin hatası:', error);
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'E-posta veya şifre hatalı.';
    } else if (error.message && error.message.includes('Oturum sonlandı')) {
        errorMessage.value = error.message; // Interceptor'dan gelen mesajı göster
    }
    else {
      errorMessage.value = 'Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.';
      if (!error.response) {
          console.error("LoginView: Ağ hatası veya CORS sorunu olabilir.");
          errorMessage.value += " Ağ bağlantısını veya CORS ayarlarını kontrol edin.";
      }
    }
  } finally {
    isLoading.value = false; // Yükleniyor durumunu bitir
  }
}
</script>

<template>
  <v-container fluid class="fill-height grey-lighten-5">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-4 pa-md-8" elevation="4">
          <v-card-title class="text-center text-h5 mb-6">
             <v-icon icon="mdi-lifebuoy" color="primary" class="mr-2"></v-icon>
             Firma Helpdesk Giriş
          </v-card-title>

          <v-form @submit.prevent="handleLogin">
            <v-text-field
              v-model="email"
              label="E-posta Adresi"
              type="email"
              variant="outlined"
              prepend-inner-icon="mdi-email-outline"
              required
              class="mb-4"
              :disabled="isLoading"
            ></v-text-field>

            <v-text-field
              v-model="password"
              label="Şifre"
              type="password"
              variant="outlined"
              prepend-inner-icon="mdi-lock-outline"
              required
              class="mb-4"
              :disabled="isLoading"
            ></v-text-field>

            <v-alert
                v-if="errorMessage"
                type="error"
                density="compact"
                variant="tonal"
                class="mb-4"
            >
                {{ errorMessage }}
            </v-alert>

            <v-btn
              :loading="isLoading"
              :disabled="isLoading"
              type="submit"
              color="primary"
              block
              size="large"
            >
              Giriş Yap
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* Vuetify genellikle kendi stillerini getirdiği için özel stillere
   çok fazla ihtiyaç duyulmayabilir. Gerekirse buraya ekleyebilirsiniz. */
.fill-height {
  min-height: 100vh; /* Sayfanın tamamını kaplamasını sağla */
}
</style>
