<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from 'svelte-sonner';
	let { children } = $props();

	import NavBar from './navbar.svelte';
</script>

<Toaster position="top-center" richColors closeButton />

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<main class="bg-aaon-blue min-h-screen">
	<div class="flex min-h-full min-w-4/5 relative">
		<NavBar />
	</div>
	{@render children?.()}
</main>
