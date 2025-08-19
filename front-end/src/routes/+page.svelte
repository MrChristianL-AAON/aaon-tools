<script>
    import SerialNumber from './serial_number.svelte';
    import JsonCard from './json_file.svelte';

    import Build from './build_button.svelte';

    import NavBar from './navbar.svelte';

    let { children } = $props();
</script>


<main>
    <div class="flex flex-col h-screen relative">
        <NavBar />
        <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-96 pt-16 md:pt-24 lg:pt-32 transition-all duration-300 z-10 relative">
            <div class="w-full max-w-7xl mx-auto px-6 md:px-8 lg:px-40">
                <h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold text-dark-text mb-6 md:mb-10 transition-all duration-300">Commands Packaging</h1>
                <div class="flex flex-col md:flex-row items-center justify-center gap-6 py-4">
                    <JsonCard />
                    <SerialNumber />
                </div>
                <div class="flex justify-center mt-8">
                    <Build />                
                </div>
            </div>
        </div>
    </div>
</main>

{@render children?.()}