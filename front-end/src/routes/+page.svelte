<script lang="ts">

    import CommandTile from './home/components/command_tile.svelte';
    import UpdateBuilderTile from './home/components/update_builder_tile.svelte';
    import UpdateArchiveTile from './home/components/update_archive_tile.svelte';
    
    

    let { children } = $props();

</script>

<main>
    <div class="flex flex-col min-h-screen relative">
        <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-64 xl:ml-80 2xl:ml-96 pt-16 md:pt-20 lg:pt-32 transition-all duration-300 z-10 relative overflow-x-hidden">
            <div class="text-center">
                <h1>
                    <span class="flex items-center justify-center text-3xl md:text-4xl lg:text-5xl font-semibold text-dark-text mb-4 md:mb-6 lg:mb-8 mt-4 md:mt-6 lg:mt-8">
                        AAON Tools Dashboard
                    </span>
                </h1>
                <p class="text-center text-sm md:text-base lg:text-lg text-dark-text mb-4 md:mb-6 lg:mb-8 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
                    Welcome to the AAON Tools Dashboard. Here you can access all the tools you need to manage and maintain your Stratus IoT devices. Select a tool below to get started.
                </p>
            </div>
            <div class="flex mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-12">
                <div class="mb-8 mr-4">
                    <CommandTile />
                </div>
                <div class="mb-8 mr-4">
                    <UpdateBuilderTile />
                </div>
                <div class="mb-8">
                    <UpdateArchiveTile />
                </div>
            </div>
        </div>
    </div>
</main>

{@render children?.()}