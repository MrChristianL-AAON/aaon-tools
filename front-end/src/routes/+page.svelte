<script lang="ts">

    import CommandTile from './home/components/command_tile.svelte';
    import UpdateBuilderTile from './home/components/update_builder_tile.svelte';
    let { children } = $props();

</script>

<main>
    <div class="flex flex-col min-h-screen relative">
        <div class="flex flex-col bg-light-background min-h-screen rounded-l-xl shadow-lg ml-16 md:ml-32 lg:ml-64 xl:ml-80 2xl:ml-96 pt-16 md:pt-20 lg:pt-32 transition-all duration-300 z-10 relative overflow-x-hidden">
            <div class="w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-12">
                <div class="mb-8">
                    <CommandTile />
                </div>
                <div class="mb-8">
                    <UpdateBuilderTile />
                </div>
            </div>
        </div>
    </div>
</main>

{@render children?.()}