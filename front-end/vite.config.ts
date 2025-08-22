import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	optimizeDeps: {
		include: ['svelte-sonner'],
	},
	resolve: {
		extensions: ['.js', '.ts', '.svelte'],
		dedupe: ['svelte']
	},
	ssr: {
		noExternal: ['svelte-sonner']
	},
	server: {
		proxy: {
			'/api': 'http://localhost:8000' // FastAPI backend proxy
		}
	}
});
