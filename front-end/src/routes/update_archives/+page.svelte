<script lang="ts">

    import Table from './components/table.svelte';

</script>

<main>
    <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-64 xl:ml-80 2xl:ml-96 pt-16 md:pt-20 lg:pt-32 transition-all duration-300 z-10 relative overflow-x-hidden">
        <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-4 pt-6 md:pt-8 lg:pt-10">
            <h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold text-dark-text mb-6 md:mb-8 lg:mb-10 transition-all duration-300">Update Package</h1>
                <p class="text-sm md:text-base lg:text-lg text-dark-text mb-6 md:mb-8 lg:mb-10">
                    Here you can view and download all previously built update packages.
                </p>
        </div>
        <div>
            <Table />
        </div>
    </div>
</main>
