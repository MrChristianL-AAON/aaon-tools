<script lang="ts">
    import { debFiles } from '$lib/stores';
    import { toast } from 'svelte-sonner';
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';
    import JSZip from 'jszip';

    import {
        Dialog,
        DialogTrigger,
        DialogContent,
        DialogHeader,
        DialogTitle,
        DialogDescription,
        DialogFooter,
        DialogClose
    } from '$lib/components/ui/dialog';

    // --- Component State ---
    let isDragOver = $state(false);
    let isProcessing = $state(false);
    let showList = $state(false);
    let dialogOpen = $state(false);

    // Format file size function
    function formatFileSize(size: number): string {
        if (size === 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(size) / Math.log(1024));
        return `${(size / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
    }
    
    // Calculate total size
    function getTotalSize(): number {
        return $debFiles.reduce((total, file) => total + file.size, 0);
    }
    
    // Get formatted total size
    function getFormattedTotalSize(): string {
        return formatFileSize(getTotalSize());
    }

    // Upload prompt text
    function getUploadPrompt() {
        if (isProcessing) return "Processing files...";
        if ($debFiles.length > 0) return `${$debFiles.length} files selected`;
        return "Click to browse or drop files, folders, or ZIP archives here";
    }

    // --- File Input Handlers (Click & Drop) ---
    function handleUploadClick() {
        // Modern browsers don't support both file and directory selection in the same input
        // So we need to try to detect folder support first
        
        // Try directory selection first - this is more reliable across browsers
        try {
            const directoryInput = document.createElement('input');
            directoryInput.type = 'file';
            directoryInput.multiple = true;
            directoryInput.accept = '.deb,.zip';
            directoryInput.setAttribute('webkitdirectory', '');
            directoryInput.setAttribute('directory', ''); // Firefox
            directoryInput.setAttribute('mozdirectory', ''); // Old Firefox
            
            // Listen for folder selection
            directoryInput.addEventListener('change', (event) => {
                const target = event.target as HTMLInputElement;
                if (target.files && target.files.length > 0) {
                    processFileList(target.files);
                } else {
                    // If no files selected with directory input, fall back to file input
                    showFileUploadDialog();
                }
            });
            
            // Trigger the directory dialog
            directoryInput.click();
        } catch (err) {
            // Fallback to regular file input if directory selection fails
            showFileUploadDialog();
        }
    }
    
    function showFileUploadDialog() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = '.deb,.zip';
        
        // Listen for file selection
        fileInput.addEventListener('change', (event) => {
            const target = event.target as HTMLInputElement;
            if (target.files) {
                processFileList(target.files);
            }
        });
        
        // Trigger the file dialog
        fileInput.click();
    }
    
    function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files) {
            processFileList(target.files);
            // Reset the input so the same file/folder can be selected again
            target.value = '';
        }
    }

    async function handleDrop(event: DragEvent) {
        event.preventDefault();
        isDragOver = false;
        if (event.dataTransfer?.items) {
            await processDataTransferItems(Array.from(event.dataTransfer.items));
        } else if (event.dataTransfer?.files) {
            await processFileList(event.dataTransfer.files);
        }
    }

    // --- Core Processing Logic ---
    async function processFileList(files: FileList) {
        isProcessing = true;
        let processedFiles: File[] = [];
        for (const file of Array.from(files)) {
            if (file.name.endsWith('.zip')) {
                processedFiles.push(...(await extractDebsFromZip(file)));
            } else if (file.name.endsWith('.deb')) {
                processedFiles.push(file);
            } else {
                toast.warning(`Skipping unsupported file: ${file.name}`);
            }
        }
        addFilesToStore(processedFiles);
        isProcessing = false;
    }

    async function processDataTransferItems(items: DataTransferItem[]) {
        isProcessing = true;
        let allFiles: File[] = [];
        const treePromises = items.map(item => {
            const entry = item.webkitGetAsEntry();
            if (entry) {
                return traverseFileTree(entry);
            }
            return Promise.resolve([]);
        });
        const fileArrays = await Promise.all(treePromises);
        allFiles = fileArrays.flat();
        
        addFilesToStore(allFiles);
        isProcessing = false;
    }

    // --- File/Directory Traversers & ZIP Extractor ---
    async function traverseFileTree(entry: FileSystemEntry): Promise<File[]> {
        let files: File[] = [];
        if (entry.isFile) {
            const file = await new Promise<File>((resolve, reject) => (entry as FileSystemFileEntry).file(resolve, reject));
            if (file.name.endsWith('.zip')) {
                files.push(...(await extractDebsFromZip(file)));
            } else if (file.name.endsWith('.deb')) {
                files.push(file);
            }
        } else if (entry.isDirectory) {
            const reader = (entry as FileSystemDirectoryEntry).createReader();
            const entries = await new Promise<FileSystemEntry[]>((resolve) => reader.readEntries(resolve));
            const filePromises = entries.map(childEntry => traverseFileTree(childEntry));
            files = (await Promise.all(filePromises)).flat();
        }
        return files;
    }

    async function extractDebsFromZip(zipFile: File): Promise<File[]> {
        try {
            const zip = await JSZip.loadAsync(zipFile);
            const debFilePromises: Promise<File>[] = [];
            zip.forEach((relativePath, zipEntry) => {
                if (!zipEntry.dir && relativePath.endsWith('.deb')) {
                    const promise = zipEntry.async('blob').then(blob => {
                        const fileName = zipEntry.name.split('/').pop() || zipEntry.name;
                        return new File([blob], fileName, { type: blob.type });
                    });
                    debFilePromises.push(promise);
                }
            });
            const debFilesFromZip = await Promise.all(debFilePromises);

            if (debFilesFromZip.length > 0) {
                toast.info(`Extracted ${debFilesFromZip.length} .deb file(s) from ${zipFile.name}`);
            } else {
                toast.warning(`No .deb files found in ${zipFile.name}`);
            }
            return debFilesFromZip;
        } catch (error) {
            console.error(`Error processing zip file ${zipFile.name}:`, error);
            toast.error(`Could not read zip file: ${zipFile.name}`);
            return [];
        }
    }

    // --- Store Management ---
    function addFilesToStore(newFiles: File[]) {
        const uniqueNewFiles = newFiles.filter(file => 
            !$debFiles.some(stored => stored.name === file.name && stored.size === file.size)
        );

        if (uniqueNewFiles.length > 0) {
            $debFiles = [...$debFiles, ...uniqueNewFiles].sort((a, b) => a.name.localeCompare(b.name));
            toast.success(`${uniqueNewFiles.length} new file(s) added.`);
        } else if (newFiles.length > 0) {
            toast.info('All selected files are already in the list.');
        }
    }

    function toggleFileList() {
        showList = !showList;
    }

    function clearFiles() {
        $debFiles = [];
        toast.info('Files cleared.');
    }
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
        
        <!-- Hidden file input that handles all upload types -->
        <input
            type="file"
            id="deb-upload"
            multiple
            accept=".deb,.zip"
            onchange={handleFileSelect}
            class="hidden"
        />

        <div
            ondragenter={(e) => { e.preventDefault(); isDragOver = true; }}
            ondragover={(e) => { e.preventDefault(); isDragOver = true; }}
            ondragleave={(e) => { e.preventDefault(); isDragOver = false; }}
            ondrop={handleDrop}
            onkeydown={(e) => { if(e.key === 'Enter' || e.key === ' ') handleUploadClick(); }}
            role="button"
            tabindex="0"
            aria-label="Drop zone for .deb/.zip file upload"
            class="flex flex-col justify-center sm:h-42 border-2 border-dashed rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-aaon-blue focus:border-aaon-blue {isDragOver ? 'border-aaon-blue bg-blue-50' : 'border-input-border bg-input-background'}"
        >
            <button
                onclick={() => handleUploadClick()}
                class="w-full h-full flex flex-col items-center justify-center text-gray-700 cursor-pointer"
            >
                <img
                    src={$debFiles.length > 0 ? Uploaded : Upload}
                    alt="Upload indicator"
                    class="w-8 h-8 sm:w-10 sm:h-10 mb-2 scale-75"
                />
                <span class="text-sm sm:text-base text-gray-500 px-4 truncate max-w-full">{getUploadPrompt()}</span>
                {#if $debFiles.length > 0}
                    <span class="text-xs text-gray-500 mt-1">Total: {getFormattedTotalSize()}</span>
                {/if}
            </button>
        </div>

        <div class="flex justify-between items-center mt-2">
            {#if $debFiles.length > 0}
                <div class="mt-2 px-3 py-2 w-24 bg-aaon-blue text-white rounded-md hover:bg-aaon-blue-light">
                    <Dialog onOpenChange={(open) => dialogOpen = open}>
                        <DialogTrigger 
                            class="hover:underline hover:cursor-pointer"
                        >{showList ? "Hide files" : "Show files"}</DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Uploaded Files ({$debFiles.length}, {getFormattedTotalSize()})</DialogTitle>
                                <DialogDescription>
                                    <ul class="mt-2 text-sm text-dark-text border p-2 rounded-md max-h-60 overflow-y-auto">
                                        {#each $debFiles as f}
                                            <li class="py-1 border-b last:border-none flex justify-between">
                                                <span>{f.name}</span>
                                                <span class="text-gray-500 text-xs">
                                                    {formatFileSize(f.size)}
                                                </span>
                                            </li>
                                        {/each}
                                    </ul>
                                </DialogDescription>
                            </DialogHeader>
                        </DialogContent>
                    </Dialog>
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