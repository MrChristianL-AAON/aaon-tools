<script lang="ts">
    import Logo from '$lib/assets/aaon-white-logo.svg';
    import Box from '$lib/assets/box.svg';
    import Cloud from '$lib/assets/cloud.svg';
    import Wrench from '$lib/assets/wrench.svg';
    import Home from '$lib/assets/home.svg';

    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    
    let username = $state("User");
    
    // Reactively determine the active section from the current URL path
    const activeSection = $derived.by(() => {
        const pathname = $page.url.pathname;
        if (pathname.startsWith('/commands')) return 'commands';
        if (pathname.startsWith('/update_builder')) return 'updates';
        if (pathname.startsWith('/update_archives')) return 'archive';
        return 'dashboard'; // Default to dashboard for '/' or any other route
    });
    
    // Determine if a section is active
    function isActive(section: string) {
        return activeSection === section;
    }
</script>

<main>
    <div class="fixed left-0 top-0 h-full bg-aaon-blue shadow-md z-50 w-16 md:w-32 lg:w-64 xl:w-80 2xl:w-96 transition-width duration-300 overflow-hidden">
        <nav class="flex flex-col pt-8 w-full h-full">
            <!-- Logo - scaled appropriately -->
            <div class="px-2 md:px-4 lg:px-6">
                <button
                    class="cursor-pointer focus:outline-none"
                    onclick={() => goto('/')}>
                    <img 
                        src={Logo} 
                        alt="AAON Logo" 
                        class="h-8 md:h-10 w-auto object-contain" 
                    />
                </button>

            </div>
            
            <!-- Welcome text - hidden on small screens -->
            <div class="mt-8 md:mt-10 px-4 lg:px-6 hidden md:block">
                <h1 class="text-navbar-text text-xl lg:text-3xl xl:text-4xl font-light truncate">
                    Welcome Back,
                </h1>
                <h1 class="text-navbar-text text-xl lg:text-3xl xl:text-4xl font-semibold truncate"> 
                    {username}
                </h1>
            </div>
            
            <!-- Navigation buttons -->
            <div class="flex flex-col ml-8 mt-6 md:mt-12 pr-20 lg:mt-16 w-full text-navbar-text text-sm md:text-base lg:text-lg font-base">
                <!-- Dashboard/Home Button -->
                <button 
                    class="{isActive('dashboard') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => goto('/')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Home} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Tools Dashboard</span>
                    </div>
                </button>

                <!-- Commands Button -->
                <button 
                    class="{isActive('commands') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => goto('/commands')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Box} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Commands Packaging</span>
                    </div>
                </button>

                <!-- Updater Builder Button -->
                <button 
                    class="{isActive('updates') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => goto('/update_builder')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Wrench} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Update Builder</span>
                    </div>
                </button>  

                <!-- Update Archive Button -->
                <button 
                    class="{isActive('archive') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => goto('/update_archives')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Cloud} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Update Archives</span>
                    </div>
                </button>  


            </div>
        </nav>
    </div>
    
</main>