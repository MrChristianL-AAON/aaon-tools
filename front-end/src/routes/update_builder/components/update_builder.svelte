<script lang="ts">
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';
    import { toast } from 'svelte-sonner';
    import * as Dialog from "$lib/components/ui/dialog/index.js";

    // Store multiple files
    import { debFiles } from '$lib/stores';

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
                debFiles.set(validFiles);
                
                toast.success('Files Uploaded', {
                    description: `${validFiles.length} valid file(s) uploaded.`,
                    duration: 1500,
                });
            } else {
                showFileTypeError();
                debFiles.set([]);
            }
        } else {
            debFiles.set([]);
        }
    }

    function handleFileFromDrop(file: File) {
        if (isValidFile(file)) {
            debFiles.update(files => [...files, file]);
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
            description: 'Please upload .deb files only.',
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

    // Recursively collect files from dropped folders
    async function getAllFilesFromDataTransferItems(items: DataTransferItemList): Promise<File[]> {
        const files: File[] = [];
        const traverse = async (entry: any) => {
            if (entry.isFile) {
                await new Promise<void>(resolve => {
                    entry.file((file: File) => {
                        if (isValidFile(file)) files.push(file);
                        resolve();
                    });
                });
            } else if (entry.isDirectory) {
                const reader = entry.createReader();
                await new Promise<void>(resolve => {
                    reader.readEntries(async (entries: any[]) => {
                        for (const e of entries) await traverse(e);
                        resolve();
                    });
                });
            }
        };
        for (let i = 0; i < items.length; i++) {
            const entry = items[i].webkitGetAsEntry?.();
            if (entry) await traverse(entry);
        }
        return files;
    }

    async function handleDrop(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        isDragging = false;

        if (event.dataTransfer && event.dataTransfer.items && event.dataTransfer.items.length > 0) {
            const files = await getAllFilesFromDataTransferItems(event.dataTransfer.items);
            if (files.length > 0) {
                debFiles.update(existingFiles => [...existingFiles, ...files]);
                toast.success('Files Uploaded', {
                    description: `${files.length} valid file(s) added from folder(s).`,
                    duration: 1500,
                });
            } else {
                showFileTypeError();
            }
        } else if (event.dataTransfer && event.dataTransfer.files.length > 0) {
            // fallback for browsers that don't support webkitGetAsEntry
            const files = Array.from(event.dataTransfer.files);
            const validFiles = files.filter(isValidFile);
            if (validFiles.length > 0) {
                debFiles.update(existingFiles => [...existingFiles, ...validFiles]);
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
        debFiles.set([]);
        fileInput.value = '';
        isDragging = false;
        toast.info('Files Cleared', {
            description: 'All uploaded files have been cleared.',
            duration: 1500,
        });
    }

    // Fixed: Use $debFiles instead of get(debFiles) to make it reactive
    let uploaded_image = $derived($debFiles.length > 0 ? Uploaded : Upload);
    
    // Calculate total size and format it
    let totalSize = $derived($debFiles.reduce((total, file) => total + file.size, 0));
    
    let formattedSize = $derived(
        totalSize === 0 ? '0 B' : (() => {
            const units = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(totalSize) / Math.log(1024));
            return `${(totalSize / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
        })()
    );
    
    let upload_prompt = $derived(
        $debFiles.length > 0
            ? `${$debFiles.length} file${$debFiles.length === 1 ? '' : 's'} selected, ${formattedSize} in size`
            : isDragging
                ? "Drop your .deb files here..."
                : "Drag 'n' drop your .deb files or folder here, or click to browse"
    );

    // Toggle list of files
    let showList = $state(false);

</script>

<main class="flex flex-col justify-center box-border p-4 sm:p-5 w-full h-full bg-card-background rounded-2xl sm:rounded-3xl shadow-lg">
    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">.deb Packages</h1>
    <p class="pt-1 sm:pt-2 text-sm sm:text-base text-light-text">
        Upload a folder of .deb files to be packaged into the update package. The resulting update package will be automatically arranged into the correct repository format, signed, and encrypted that is ready to be placed onto a USB and applied to a Stratus unit manager device.
    </p>

    <div class="mt-4 sm:mt-6">
        <label for="deb-upload" class="text-sm sm:text-base text-dark-text block mb-2">
            Upload your .deb files
        </label>
        <input
            type="file"
            id="deb-upload"
            multiple
            accept=".deb,.zip"
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

        <div class="flex justify-between items-center mt-2">
            {#if $debFiles.length > 0}
                <div class="mt-2 px-3 py-2 w-24 bg-aaon-blue text-white rounded-md hover:bg-aaon-blue-light">
                    <Dialog.Root>
                        <Dialog.Trigger
                        class="hover:underline hover:cursor-pointer"
                            >{showList ? "Hide files" : "Show files"}</Dialog.Trigger>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>Uploaded Debs ({$debFiles.length} files, {formattedSize})</Dialog.Title>
                                <Dialog.Description>
                                    <ul class="mt-2 text-sm text-dark-text border p-2 rounded-md max-h-60 overflow-y-auto">
                                        {#each $debFiles as f}
                                            <li class="py-1 border-b last:border-none flex justify-between">
                                                <span>{f.name}</span>
                                                <span class="text-gray-500 text-xs">
                                                    {(() => {
                                                        if (f.size === 0) return '0 B';
                                                        const units = ['B', 'KB', 'MB', 'GB'];
                                                        const i = Math.floor(Math.log(f.size) / Math.log(1024));
                                                        return `${(f.size / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
                                                    })()}
                                                </span>
                                            </li>
                                        {/each}
                                    </ul>
                                </Dialog.Description>
                            </Dialog.Header>
                        </Dialog.Content>
                    </Dialog.Root>
                </div>
            {:else}
                <p class="text-xs sm:text-sm text-red-500 mt-2">
                    Please ensure you've provided valid .deb files to proceed with the update packaging process.
                </p>
            {/if}

            <div class="flex ml-4">
                {#if showList && $debFiles.length > 0}
                    <ul class="mt-2 text-sm text-dark-text border p-2 rounded-md">
                        {#each $debFiles as f}
                            <li class="py-1 border-b last:border-none">{f.name}</li>
                        {/each}
                    </ul>
                {/if}
            </div>
            
            <div>
                {#if $debFiles.length > 0}
                    <button
                        onclick={clearFiles}
                        class="mt-2 w-full text-aaon-blue px-3 py-2 bg-aaon-blue hover:bg-aaon-blue-light hover:underline hover:cursor-pointer text-white rounded-md"
>
                        Clear
                    </button>
                {/if}
            </div>        
        </div>
    </div>
</main>