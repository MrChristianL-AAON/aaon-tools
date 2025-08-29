<script lang="ts">
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';
    import { toast } from 'svelte-sonner';

    // Store multiple files
    let debFiles = $state<File[]>([]);

    let fileInput: HTMLInputElement;
    let isDragging = $state(false);
    let dropZone: HTMLDivElement;

    function isValidFile(file: File) {
        const validExtensions = ['.deb', '.zip'];
        return validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }

    function handleFileChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            const validFiles = Array.from(input.files).filter(isValidFile);

            if (validFiles.length > 0) {
                debFiles = validFiles;
                toast.success('Files Uploaded', {
                    description: `${validFiles.length} valid file(s) uploaded.`,
                    duration: 1500,
                });
            } else {
                showFileTypeError();
                debFiles = [];
            }
        } else {
            debFiles = [];
        }
    }

    function handleFileFromDrop(file: File) {
        if (isValidFile(file)) {
            debFiles = [...debFiles, file];
            toast.success('File Uploaded', {
                description: `${file.name} uploaded.`,
                duration: 1500,
            });
        } else {
            showFileTypeError();
        }
    }

    function showFileTypeError() {
        toast.error('File Type Error', {
            description: 'Please upload .deb or .zip files only.',
            duration: 1500,
        });
    }

    function openFileBrowser() {
        fileInput.click();
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            openFileBrowser();
        }
    }

    // Drag-and-drop
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
        isDragging = false;
    }
    function handleDrop(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        isDragging = false;

        if (event.dataTransfer && event.dataTransfer.files.length > 0) {
            const files = Array.from(event.dataTransfer.files);
            const validFiles = files.filter(isValidFile);

            if (validFiles.length > 0) {
                debFiles = [...debFiles, ...validFiles];
                toast.success('Files Uploaded', {
                    description: `${validFiles.length} valid file(s) added.`,
                    duration: 1500,
                });
            } else {
                showFileTypeError();
            }
        }
    }

    function clearFiles() {
        debFiles = [];
        fileInput.value = '';
        isDragging = false;
        toast.info('Files Cleared', {
            description: 'All uploaded files have been cleared.',
            duration: 1500,
        });
    }

    let uploaded_image = $derived(debFiles.length > 0 ? Uploaded : Upload);
    let upload_prompt = $derived(
        debFiles.length > 0
            ? `${debFiles.length} file(s) selected`
            : isDragging
                ? "Drop your .deb or .zip files here..."
                : "Drag 'n' drop your .deb/.zip files or folder here, or click to browse"
    );
</script>

<main class="flex flex-col justify-center box-border p-4 sm:p-5 w-full h-full bg-card-background rounded-2xl sm:rounded-3xl shadow-lg">
    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">.deb Packages</h1>
    <p class="pt-1 sm:pt-2 text-sm sm:text-base text-light-text">
        Upload one or more .deb or .zip files, or drag in a folder of .deb files.
        These will be automatically arranged into the correct repository format, signed, and encrypted.
    </p>

    <div class="mt-4 sm:mt-6">
        <label for="deb-upload" class="text-sm sm:text-base text-dark-text block mb-2">
            Upload your .deb or .zip files
        </label>
        <input
            type="file"
            id="deb-upload"
            multiple
            webkitdirectory
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
            aria-label="Drop zone for .deb/.zip file upload"
            class="flex flex-col justify-center sm:h-42 border-2 border-dashed rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-aaon-blue focus:border-aaon-blue {isDragging ? 'border-aaon-blue bg-blue-50' : 'border-input-border bg-input-background'}"
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

        {#if debFiles.length > 0}
            <ul class="mt-2 text-sm text-dark-text">
                {#each debFiles as f}
                    <li>{f.name}</li>
                {/each}
            </ul>
        {/if}

        <div>
            <button
                onclick={clearFiles}
                class="mt-2 w-full text-aaon-blue hover:underline"
            >
                clear
            </button>
        </div>
    </div>
</main>
