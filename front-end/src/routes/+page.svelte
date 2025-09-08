<script lang="ts">

    import CommandTile from './home/components/command_tile.svelte';
    import UpdateBuilderTile from './home/components/update_builder_tile.svelte';
    import UpdateArchiveTile from './home/components/update_archive_tile.svelte';
    
    

    let { children } = $props();

</script>

<main>
    <div class="flex flex-col min-h-screen relative">
        <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-64 xl:ml-80 2xl:ml-96 pt-16 md:pt-20 lg:pt-32 transition-all duration-300 z-10 relative overflow-x-hidden">
            <div class="text-center mb-4 sm:mb-6 md:mb-8">
                <h1>
                    <span class="flex items-center justify-center text-3xl md:text-4xl lg:text-5xl font-semibold text-dark-text mb-3 md:mb-4 lg:mb-6 mt-4 md:mt-6 lg:mt-8">
                        AAON Tools Dashboard
                    </span>
                </h1>
                <p class="text-center text-sm md:text-base lg:text-lg text-dark-text mx-auto max-w-4xl px-4 sm:px-6 md:px-8 lg:px-12">
                    Welcome to the AAON Tools Dashboard. Here you can access all the tools you need to manage and maintain your Stratus IoT devices. Select a tool below to get started.
                </p>
            </div>
            <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-12">
                <!-- Responsive grid layout with consistent spacing -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 md:gap-10 lg:gap-12">
                    <!-- Each tile in a container with consistent height -->
                    <div class="w-full h-full flex">
                        <CommandTile 
                            path="/commands" 
                            title="Command Packaging" 
                            description="Click here to build secure MQTT command packages." 
                        />
                    </div>
                    <div class="w-full h-full flex">
                        <UpdateBuilderTile 
                            path="/update_builder" 
                            title="Update Builder" 
                            description="Click here to build update packages for the Stratus unit manager." 
                        />
                    </div>
                    <div class="w-full h-full flex">
                        <UpdateArchiveTile 
                            path="/update_archives" 
                            title="Update Archives" 
                            description="Click here to access previous releases of update packages for the Stratus Unit Manager." 
                        />
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>

{@render children?.()}