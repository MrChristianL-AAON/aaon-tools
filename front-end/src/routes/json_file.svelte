<script lang="ts">
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';
    import { jsonFileStore } from '$lib/stores';

    let json_file = $state({
        file: null as File | null,
    });

    // Update the store whenever local state changes
    $effect(() => {
        jsonFileStore.set(json_file);
    });

    let fileInput: HTMLInputElement;

    function handleFileChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            json_file.file = input.files[0];
        } else {
            json_file.file = null;
        }
    }

    function openFileBrowser() {
        fileInput.click();
    }

    let uploaded_image = $derived(json_file.file ? Uploaded : Upload);
    let upload_prompt = $derived(json_file.file ? `${json_file.file.name}` : "Click to upload JSON file");


</script>

<main class="box-border p-4 sm:p-5 w-full h-full bg-card-background rounded-2xl sm:rounded-3xl shadow-lg">

    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">JSON File</h1>
    <p class="pt-1 sm:pt-2 text-sm sm:text-base text-light-text">Upload your JSON file of MQTT commands to be encrypted and securely packaged, ready to be safely applied to a Stratus unit manager.</p>

    <div class="mt-4 sm:mt-6">
        <label for="json-upload" class="text-sm sm:text-base text-dark-text block mb-2">Upload your JSON file</label>
        <input 
            type="file" 
            id="json-upload" 
            accept="application/json" 
            onchange={handleFileChange} 
            bind:this={fileInput}
            class="hidden"
        />
        <button 
            onclick={openFileBrowser} 
            class="w-full h-24 sm:h-32 flex flex-col items-center justify-center bg-input-background border border-input-border hover:border-aaon-blue text-gray-700 rounded-md transition-colors duration-200 cursor-pointer"
        >
            <img 
                src={uploaded_image} 
                alt="Upload indicator" 
                class="w-8 h-8 sm:w-10 sm:h-10 mb-2"
            />
            <span class="text-sm sm:text-base text-gray-500 px-4 truncate max-w-full">{upload_prompt}</span>
        </button>
    </div>
</main>
