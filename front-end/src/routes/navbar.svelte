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
    <div class="absolute left-0 top-0 h-full bg-aaon-blue shadow-md flex pt-4 px-2 md:px-6 lg:px-10 z-0 w-16 md:w-32 lg:w-96">
        <nav class="flex flex-col pt-8 w-full mx-auto ">
            <img 
                src={Logo} 
                alt="AAON Logo" 
                class="h-10 w-32 scale-125 ml-2" 
            />
            <h1 class="text-navbar-text text-4xl font-light mt-12 mb-2">
                Welcome Back,
            </h1>
            <h1 class="text-navbar-text text-4xl font-semibold mb-20"> 
                {username}
            </h1>
            <div class="flex flex-col w-full text-navbar-text text-lg font-base">
                <button 
                    class="{isActive('commands') ? 'bg-aaon-blue-light font-semibold' : ''} mb-4 transition-colors duration-300 rounded-lg px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('commands')}>
                    <div class="flex items-center gap-4">
                        <img src={Box} alt=""> Commands Packaging
                    </div>
                </button>
                
                <button 
                    class="{isActive('updates') ? 'bg-aaon-blue-light font-semibold' : ''} mb-4 transition-colors duration-300 rounded-lg px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('updates')}>
                    <div class="flex items-center gap-4">
                        <img src={Cloud} alt=""> Update Archives
                    </div>
                </button>  

                <button 
                    class="{isActive('admin') ? 'bg-aaon-blue-light font-semibold' : ''} mb-4 transition-colors duration-300 rounded-lg px-4 py-2 cursor-pointer hover:bg-aaon-blue-light hover:font-semibold"
                    onclick={() => setActive('admin')}>
                    <div class="flex items-center gap-4">
                        <img src={Wrench} alt=""> Admin Tools
                    </div>
                </button>  
            </div>
        </nav>
    </div>
    
</main>