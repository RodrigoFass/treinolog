import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import 'bulma/css/bulma.min.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
import '@fontsource/space-grotesk/500.css'
import '@fontsource/space-grotesk/700.css'
import './style.css'
import { applyTheme } from './utils/theme'

applyTheme()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
