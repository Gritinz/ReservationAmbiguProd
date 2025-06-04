import { fileURLToPath, URL } from 'node:url'
import { defineConfig, UserConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/ 
export default defineConfig(({ command, mode }): UserConfig => {
  // Config commune à tous les environnements
  const config: UserConfig = {
    plugins: [
      vue(),
      // Désactiver Vue DevTools en production pour des raisons de sécurité/perf
      mode !== 'production' ? vueDevTools() : { name: 'vue-devtools-disabled' },
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: 5173,
    },
    build: {
      outDir: 'dist', // dossier de sortie du build
      emptyOutDir: true,
      sourcemap: false, // désactiver les sourcemaps en prod
    },
  }

  // Config spécifique au mode build (prod)
  if (command === 'build') {
    Object.assign(config, {
      // Options supplémentaires pour le build
      base: '/', // chemin relatif pour les assets
    })
  }

  return config
})