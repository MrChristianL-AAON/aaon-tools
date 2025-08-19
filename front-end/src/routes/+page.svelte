<script>
    import SerialNumber from './serial_number.svelte';
    import JsonCard from './json_file.svelte';

    // import Build from './build_button.svelte';
    import NavBar from './navbar.svelte';
    import Output from './output.svelte';

    let { children } = $props();
</script>


<main>
    <div class="flex flex-col min-h-screen relative">
        <NavBar />
        <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-64 xl:ml-80 2xl:ml-96 pt-16 md:pt-20 lg:pt-24 transition-all duration-300 z-10 relative overflow-x-hidden">
            <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-12">
                <h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold text-dark-text mb-6 md:mb-8 lg:mb-10 transition-all duration-300">Commands Packaging</h1>
                
                <!-- Cards container with improved responsiveness -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
                    <div class="w-full">
                        <JsonCard />
                    </div>
                    <div class="w-full">
                        <SerialNumber />
                    </div>
                </div>
                
                <!-- Output section with consistent width -->
                <div class="mt-6 sm:mt-8 lg:mt-10">
                    <Output />
                </div>
            </div>
        </div>
    </div>
</main>

{@render children?.()}