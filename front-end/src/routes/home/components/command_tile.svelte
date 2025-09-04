<script lang="ts">
    import Box from '$lib/assets/box.svg';

    function redirectToCommands() {
        // Redirect to the /commands page
        window.location.href = '/commands';
    }
</script>

<main>
    <div class="w-120 h-80 flex flex-col items-center justify-center bg-light-background border-2 rounded-lg shadow-lg hover:bg-aaon-blue-light p-4 cursor-pointer">
        <div class="px-2 md:px-4 lg:px-6">
            <img 
                src={Box} 
                alt="Commands Packaging Icon" 
                class="h-8 md:h-10 w-auto object-contain" 
            />
        </div>
        
        <div class="text-2xl font-semibold text-dark-text hover:text-light-text mt-4">
            Commands Packaging
        </div>
        <div class="mt-2 text-center text-sm text-dark-text hover:text-light-text">
            <p>
                Click here to package commands into a deployable format.
            </p>
        </div>
    </div>
</main>