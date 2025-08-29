<script lang="ts">
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';
    import { jsonFileStore } from '$lib/stores';

    // Import toast directly from the Toaster component
    import { toast } from 'svelte-sonner';

    let json_file = $state({
        file: null as File | null,
    });

    $effect(() => {
        jsonFileStore.set(json_file);
    });

    let fileInput: HTMLInputElement;
    let isDragging = $state(false);
    let dropZone: HTMLDivElement;

    function handleFileChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            const file = input.files[0];
            if (file.type === 'application/json') {
                json_file.file = file;
                // Show success toast
                toast.success('File Uploaded', {
                    description: `${file.name} has been successfully uploaded.`,
                    duration: 1500,
                });
            } else {
                // Show error for invalid file type
                showFileTypeError();
                json_file.file = null;
            }
        } else {
            json_file.file = null;
        }
    }

    function showFileTypeError() {
        // Use toast notification instead of alert
        toast.error('File Type Error', {
            description: 'Please upload a valid JSON file.',
            duration: 1500,
        });
    }

    function handleFileFromDrop(file: File) {
        if (file && file.type === 'application/json') {
            json_file.file = file;
            // Show success toast
            toast.success('File Uploaded', {
                description: `${file.name} has been successfully uploaded.`,
                duration: 1500,
            });
        } else {
            // Show an error for invalid file type
            showFileTypeError();
        }
    }

    function openFileBrowser() {
        fileInput.click();
    }
    
    // Handle keyboard events for accessibility
    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            openFileBrowser();
        }
    }
    
    // Drag and drop handlers
    function handleDragEnter(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        isDragging = true;
    }
    
    function handleDragOver(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        isDragging = true;
    }
    
    function handleDragLeave(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        // Simply set dragging to false when cursor leaves the drop zone
        isDragging = false;
    }
    
    function handleDrop(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        isDragging = false;
        
        if (event.dataTransfer && event.dataTransfer.files.length > 0) {
            const file = event.dataTransfer.files[0];
            handleFileFromDrop(file);
        }
    }

    function clearFile() {
        json_file.file = null;
        fileInput.value = '';
        isDragging = false;
        toast.info('File Cleared', {
            description: 'The uploaded JSON file has been cleared.',
            duration: 1500,
        });
    }

    let uploaded_image = $derived(json_file.file ? Uploaded : Upload);
    let upload_prompt = $derived(
        json_file.file 
            ? `${json_file.file.name}` 
            : isDragging 
                ? "Drop your JSON file here..." 
                : "Drag 'n' drop your JSON file here or click to browse"
    );
</script>

<main class="flex flex-col justify-center box-border p-4 sm:p-5 w-full h-full bg-card-background rounded-2xl sm:rounded-3xl shadow-lg">

    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">JSON File</h1>
    <p class="pt-1 sm:pt-2 text-sm sm:text-base text-light-text">Upload your JSON file of MQTT commands to be encrypted and securely packaged, ready to be safely applied to a Stratus unit manager.</p>

        <div class="mt-4 sm:mt-6">
        <label for="json-upload" class="text-sm sm:text-base text-dark-text block mb-2">Attach your JSON file</label>
        <input
            type="file" 
            id="json-upload" 
            accept="application/json" 
            onchange={handleFileChange} 
            bind:this={fileInput}
            class="hidden"
        />
        <div 
            bind:this={dropZone}
            ondragenter={handleDragEnter}
            ondragover={handleDragOver}
            ondragleave={handleDragLeave}
            ondrop={handleDrop}
            onkeydown={handleKeyDown}
            role="button"
            tabindex="0"
            aria-label="Drop zone for JSON file upload"
            class="flex flex-col justify-center sm:h-32 border-2 border-dashed rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-aaon-blue focus:border-aaon-blue {isDragging ? 'border-aaon-blue bg-blue-50' : 'border-input-border bg-input-background'}"
        >
            <button 
                onclick={openFileBrowser} 
                class="w-full h-full flex flex-col items-center justify-center text-gray-700 cursor-pointer"
            >
                <img 
                    src={uploaded_image} 
                    alt="Upload indicator" 
                    class="w-8 h-8 sm:w-10 sm:h-10 mb-2 scale-75"
                />
                <span class="text-sm sm:text-base text-gray-500 px-4 truncate max-w-full">{upload_prompt}</span>
            </button>
        </div>
        <div>
            <button
                onclick={clearFile}
                class="mt-2 w-full text-aaon-blue hover:underline">
                clear
            </button>
        </div>
    </div>
</main>
