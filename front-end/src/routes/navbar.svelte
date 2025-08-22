<script lang="ts">
    import Logo from '$lib/assets/aaon-white-logo.svg';
    import Box from '$lib/assets/box.svg';
    import Cloud from '$lib/assets/cloud.svg';
    import Wrench from '$lib/assets/wrench.svg';


    let username = $state("User");
    
    // Track the active page/section
    let activeSection = $state("commands"); // Default active section
    
    // Function to set active section
    function setActive(section: string) {
        activeSection = section;
    }
    
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
                <img 
                    src={Logo} 
                    alt="AAON Logo" 
                    class="h-8 md:h-10 w-auto object-contain" 
                />
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
            <div class="flex flex-col mt-6 md:mt-12 lg:mt-16 w-full text-navbar-text text-sm md:text-base lg:text-lg font-base">
                <!-- Commands Button -->
                <button 
                    class="{isActive('commands') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('commands')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Box} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Commands Packaging</span>
                    </div>
                </button>
                
                <!-- Updates Button -->
                <button 
                    class="{isActive('updates') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('updates')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Cloud} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Update Archives</span>
                    </div>
                </button>  

                <!-- Admin Button -->
                <button 
                    class="{isActive('admin') ? 'bg-aaon-blue-light font-semibold' : ''} mb-2 md:mb-3 lg:mb-4 transition-colors duration-300 rounded-lg px-2 md:px-3 lg:px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('admin')}>
                    <div class="flex items-center gap-2 md:gap-3 lg:gap-4">
                        <img src={Wrench} alt="" class="w-6 h-6" />
                        <span class="hidden md:inline-block truncate">Admin Tools</span>
                    </div>
                </button>  
            </div>
        </nav>
    </div>
    
</main>