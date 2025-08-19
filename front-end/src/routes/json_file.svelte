<script lang="ts">
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';

    let json_file = $state({
        file: null as File | null,
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

<main class="box-border p-5 w-full h-88 max-w-115 bg-card-background rounded-3xl shadow-lg">

    <h1 class="text-2xl font-bold mb-1 text-dark-text">JSON File</h1>
    <p class="pt-2 text-base text-light-text">Upload your JSON file of MQTT commands to be encrypted and securely packaged, ready to be safely applied to a Stratus unit manager.</p>

    <div class="pt-8">
        <label for="json-upload text-dark-text">Upload your JSON file</label>
        <input 
            type="file" 
            id="json-upload" 
            accept="application/json" 
            onchange={handleFileChange} 
            bind:this={fileInput}
            class="hidden"
        />
    </div>
    <button onclick={openFileBrowser} 
    class="w-105 h-36 flex flex-col items-center justify-center bg-input-background border border-input-border hover:input-border hover:border-aaon-blue text-gray-700 rounded-md transition-colors duration-200 cursor-pointer">
        <img 
            src={uploaded_image} 
            alt="" 
            class="inline-block center-align mr-2 pb-1 scale-90"
        />
        <span class="text-gray-500">{upload_prompt}</span>
    </button>
</main>
