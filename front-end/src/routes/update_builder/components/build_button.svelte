<script lang="ts">
    import { debFiles } from '$lib/stores';
</script>

<main>
    <div class="mt-6 items-center flex justify-center">
        <!-- Disable button if no files are selected -->       
        <button class="px-4 py-3 rounded-md font-base text-lg sm:text-xl text-light-background {$debFiles.length === 0 ? 'border border-light-text bg-input-background cursor-not-allowed text-light-text' : 'bg-aaon-blue hover:bg-aaon-blue-light text-white'} rounded-md transition-colors duration-200">
            Generate Update Package
        </button>
    </div>

</main>