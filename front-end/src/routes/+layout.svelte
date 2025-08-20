<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from 'svelte-sonner';
	let { children } = $props();


</script>

<Toaster position="top-center" richColors closeButton />

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<main class="bg-aaon-blue min-h-screen">
	{@render children?.()}
</main>
