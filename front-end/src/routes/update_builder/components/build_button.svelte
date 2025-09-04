<script lang="ts">
    import { debFiles } from '$lib/stores';
    import { toast } from 'svelte-sonner';

    interface UpdatePackage {
        name: string;
        updateFile: { name: string; path: string } | null;
        jsonFile: { name: string; path: string } | null;
        isReady: boolean;
        allFiles: string[];
    }

    let output_files = $state<UpdatePackage>({
        name: '',
        updateFile: null,
        jsonFile: null,
        isReady: false,
        allFiles: []
    });

    let isPreparing = $state(false);
    let canGenerate = $derived($debFiles.length > 0);

    let uploadProgress = 0; // 0–100

    function toggleDevView() {
        if (output_files.isReady) {
            // If the view is on, turn it off by resetting the state
            output_files.isReady = false;
            output_files.updateFile = null;
            output_files.jsonFile = null;
            output_files.allFiles = [];
        } else {
            // If the view is off, turn it on by populating with mock data
            output_files.isReady = true;
            output_files.updateFile = {
                name: 'stratus-update-package.update',
                path: 'mock/path/stratus-update-package.update'
            };
            output_files.jsonFile = {
                name: 'stratus-update-package.json',
                path: 'mock/path/stratus-update-package.json'
            };
            output_files.allFiles = [
                'mock/path/stratus-update-package.update',
                'mock/path/stratus-update-package.json'
            ];
            toast.info('Dev Mode Enabled', {
                description: 'Showing mock download section for UI editing.'
            });
        }
    }

    async function clearPreviousDebs() {
        try {
            console.log('Clearing previous DEB files...');
            const response = await fetch('/api/builder/clear_debs', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to clear previous debs');
                toast.error('Failed to clear previous files.');
                return false;
            }
            const data = await response.json();
            console.log('Clear response:', data);
            if (data.count > 0) {
                toast.info(`Cleared ${data.count} previous DEB files.`);
            }
            return true;
        } catch (err) {
            console.error('Error clearing previous DEB files:', err);
            toast.error('Error clearing previous files.');
            return false;
        }
    }

    async function upload_debs() {
        console.log('Uploading DEB files:', $debFiles);

        if (!$debFiles || $debFiles.length === 0) {
            toast.error('Cannot upload DEB files', {
                description: 'Please upload at least one DEB file to generate an update package.',
                duration: 1500
            });
            return false;
        }

        try {
            const BATCH_SIZE = 5;
            const totalBatches = Math.ceil($debFiles.length / BATCH_SIZE);
            let successCount = 0;

            for (let i = 0; i < totalBatches; i++) {
                const start = i * BATCH_SIZE;
                const end = start + BATCH_SIZE;
                const batch = $debFiles.slice(start, end);

                const formData = new FormData();
                batch.forEach((file) => formData.append('files', file));

                console.log(`Uploading batch ${i + 1}/${totalBatches} (${batch.length} files)...`);
                uploadProgress = Math.floor(((i + 1) / totalBatches) * 100);

                const response = await fetch('/api/builder/upload_debs', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error(`Upload failed for batch ${i + 1}:`, response.status, errorText);
                    throw new Error(`Upload failed: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`Batch ${i + 1} response:`, data);
                successCount += batch.length;
            }

            toast.success('DEB files uploaded successfully', {
                description: `All ${successCount} files uploaded!`,
                duration: 1500
            });

            uploadProgress = 100;
            return true;
        } catch (err) {
            console.error('Error uploading DEB files:', err);
            toast.error('Upload Error', {
                description: 'An error occurred while uploading DEB files. Please try again.',
                duration: 1500
            });
            return false;
        }
    }

    async function run_update_pipeline() {
        try {

            // Run update pipeline
            const res = await fetch('/api/builder/build_update', {
                method: 'POST'
            });

            if (!res.ok) {
                throw new Error(`Pipeline failed: ${res.statusText}`);
            }

            const result = await res.json();
            console.log('Pipeline result:', result);
            
            toast.success('Pipeline Started', {
                description: 'Update package build started in background. Please wait...',
                duration: 2000,
            });

            // Since the pipeline runs in background, we need to wait and poll for completion
            // Wait a reasonable amount of time for the pipeline to complete
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
            
            return true;
        } catch (err) {
            console.error('Error running update pipeline:', err);
            toast.error('Pipeline Error', {
                description: 'An error occurred while starting the update pipeline. Please try again.',
                duration: 1500,
            });
            return false;
        }
    }

    // Get list of output files and prepare download links
    async function prepareDownload() {
        try {
            
            // Prepare download
            console.log('Fetching output files list...');
            const res = await fetch('/api/builder/output_files', {
                method: 'GET',
                cache: 'no-cache' // Disable caching to ensure we get fresh data
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error('Output files fetch failed:', res.status, errorText);
                throw new Error(`Error fetching output files: ${res.statusText}`);
            }

            const data = await res.json();
            console.log('Output files response:', data);
            console.log('Files array:', data.files);

            if (!data.files || data.files.length <= 2) {
                console.warn(
                    `Pipeline not complete. Found ${data.files ? data.files.length : 0} files, waiting for more than 2.`
                );
                throw new Error('Pipeline still running.');
            }

            // Clear existing files
            output_files.allFiles = [];
            // Add new files
            output_files.allFiles = [...data.files];
            console.log('Set output_files.allFiles to:', output_files.allFiles);

            // Find .update and .json files
            const updateFile = data.files.find((f: string) => f.endsWith('.update'));
            const jsonFile = data.files.find((f: string) => f.endsWith('.json'));

            if (!updateFile || !jsonFile) {
                throw new Error('Missing .update or .json file in output directory');
            }

            if (updateFile) {
                output_files.updateFile = {
                    name: updateFile.split('/').pop() || updateFile,
                    path: updateFile
                };
            }
            
            if (jsonFile) {
                output_files.jsonFile = {
                    name: jsonFile.split('/').pop() || jsonFile,
                    path: jsonFile
                };
            }

            output_files.isReady = true;

            toast.success('Output files found', {
                description: `Found ${data.files.length} output files ready for download.`,
                duration: 1500,
            });

            return true;
        } catch (err) {
            console.error('Error preparing download:', err);
            return false;
        }
    }

    async function downloadFile(filePath: string, fileName: string) {
        try {
            
            // Download file
            console.log(`Attempting to download file: ${filePath}`);
            const res = await fetch(`/api/builder/download/${encodeURIComponent(filePath)}`, {
                method: 'GET'
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error(`Error downloading ${fileName}:`, res.status, errorText);
                throw new Error(`Error downloading ${fileName}: ${res.statusText}`);
            }

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            toast.success(`Downloaded ${fileName}`);
        } catch (err) {
            console.error(`Error downloading ${fileName}:`, err);
            toast.error('Download Error', {
                description: `Failed to download ${fileName}. Please try again.`,
                duration: 1500,
            });
        }
    }

    async function downloadAllFiles() {
        if (!output_files.isReady) {
            toast.error('Files Not Ready', {
                description: 'The output files are not ready for download yet.',
                duration: 1500,
            });
            return;
        }

        const downloads = [];
        
        if (output_files.updateFile) {
            downloads.push(downloadFile(output_files.updateFile.path, output_files.updateFile.name));
        }
        
        if (output_files.jsonFile) {
            downloads.push(downloadFile(output_files.jsonFile.path, output_files.jsonFile.name));
        }

        if (downloads.length > 0) {
            await Promise.all(downloads);
            toast.success('All files downloaded successfully');
        }
    }

    async function checkForFiles(pollInterval = 10000, maxWait = 3 * 60 * 1000) {
        // pollInterval: time between checks in ms (10s)
        // maxWait: max wait time in ms (3 min default - reduced from 8 min)
        const start = Date.now();

        console.log(`Starting polling for output files every ${pollInterval/1000}s, timeout after ${maxWait/60000} min`);

        // Try immediately first
        try {
            const success = await prepareDownload();
            if (success) {
                console.log("Files found immediately!");
                return true;
            }
        } catch (error) {
            console.log("First check failed:", error instanceof Error ? error.message : String(error));
            // Continue to polling loop
        }

        while (Date.now() - start < maxWait) {
            try {
                console.log(`Polling for files at ${new Date().toLocaleTimeString()}...`);
                const success = await prepareDownload();
                if (success) {
                    console.log("Files found during polling!");
                    return true;
                }
            } catch (error) {
                console.log(`Still waiting for files: ${error instanceof Error ? error.message : String(error)}`);
                // still running; continue polling
            }

            console.log(`No files yet, retrying in ${pollInterval / 1000} seconds...`);
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        toast.error('Pipeline Timeout', {
            description: `Pipeline did not produce output files within ${maxWait / 60000} minutes.`,
            duration: 5000
        });
        return false;
    }

    async function updatePipeline() {
        if (isPreparing) return; // Prevent multiple clicks

        try {
            isPreparing = true;
            output_files.isReady = false; // Reset state
            output_files.updateFile = null;
            output_files.jsonFile = null;
            output_files.allFiles = [];

            // 0. Clear previous DEB files
            toast.info('Step 1/4: Clearing previous files...');
            const clearSuccess = await clearPreviousDebs();
            if (!clearSuccess) {
                // Stop if clearing fails, as it might indicate a server problem
                toast.error('Could not clear previous files. Aborting pipeline.');
                return;
            }

            // 1. Upload DEB files to correct location
            toast.info('Step 2/4: Uploading DEB files...');
            const uploadSuccess = await upload_debs();
            if (!uploadSuccess) {
                toast.error('Upload failed, canceling pipeline');
                return;
            }

            // 2. Run the update pipeline (background process)
            toast.info('Step 3/4: Starting build pipeline...');
            const pipelineSuccess = await run_update_pipeline();
            if (!pipelineSuccess) {
                toast.error('Pipeline start failed, canceling');
                return;
            }
    
            // 3. Wait for pipeline to complete and prepare download links
            toast.info('Step 4/4: Waiting for build to complete...');
            
            // Check for files immediately in case they already exist
            console.log('Checking immediately for existing output files...');
            try {
                const immediateSuccess = await prepareDownload();
                if (immediateSuccess) {
                    toast.success('Files already available! 🎉', {
                        description: 'Update package is ready for download.',
                        duration: 3000,
                    });
                    return;
                }
            } catch (error) {
                console.log('Initial file check failed, will start polling:', error instanceof Error ? error.message : String(error));
            }
            
            // Start polling for files
            const prepareSuccess = await checkForFiles();
            if (!prepareSuccess) {
                toast.error('Failed to find output files');
                return;
            }

            toast.success('Pipeline Complete! 🎉', {
                description: 'Update package is ready for download.',
                duration: 3000,
            });
    
        } finally {
            isPreparing = false;
        }
    }

</script>

<style>
    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #e5e7eb;
        border-top: 2px solid #2563eb;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

</style>

<main>
    <div>
        <button
            onclick={toggleDevView}
            class="absolute top-2 right-2 bg-gray-200 text-gray-600 text-xs font-mono px-2 py-1 rounded hover:bg-gray-300"
            title="Toggle developer view to see download section for UI editing"
        >
            Toggle Dev View
        </button>

        {#if !output_files.isReady}
            <!-- Build button and loading button  -->
            <div class="mt-6 flex flex-col items-center justify-center space-y-4">
                <button 
                class="px-4 py-3 rounded-md font-base text-lg sm:text-xl transition-colors duration-200
                {$debFiles.length === 0 ? 'border border-light-text bg-input-background cursor-not-allowed text-light-text' : 'bg-aaon-blue hover:bg-gray-400 hover:cursor-pointer text-white'}"        
                disabled={!canGenerate || isPreparing}
                onclick={updatePipeline}        
                >
                    {#if isPreparing}
                        <span class="spinner mr-2"></span>
                        <span>Building Update Package...</span>
                    {:else}
                        <span>Generate Update Package</span>
                    {/if}
                </button>
            </div>
        {:else}
            <!-- Download Section - Only show when files are ready -->
            <div class="mt-6 p-4 bg-gray-50 rounded-lg border max-w-md w-full">
                <h3 class="text-lg font-semibold mb-3 text-gray-800">Download Files</h3>
                
                <div class="space-y-2 mb-4">
                    {#if output_files.updateFile}
                        <div class="flex items-center justify-between p-2 bg-white rounded border">
                            <div class="flex-1">
                                <div class="font-medium text-sm">{output_files.updateFile.name}</div>
                                <div class="text-xs text-gray-500">Update Package</div>
                            </div>
                            <button 
                                class="px-3 py-2 bg-aaon-blue-light hover:bg-aaon-blue text-white rounded-md text-sm transition-colors duration-200"
                                onclick={() => downloadFile(output_files.updateFile!.path, output_files.updateFile!.name)}
                            >
                                Download
                            </button>
                        </div>
                    {/if}
                    
                    {#if output_files.jsonFile}
                        <div class="flex items-center justify-between p-2 bg-white rounded border">
                            <div class="flex-1">
                                <div class="font-medium text-sm">{output_files.jsonFile.name}</div>
                                <div class="text-xs text-gray-500">Package Version Tracking JSON</div>
                            </div>
                            <button 
                                class="px-3 py-2 bg-aaon-blue-light hover:bg-aaon-blue text-white rounded-md text-sm transition-colors duration-200"
                                onclick={() => downloadFile(output_files.jsonFile!.path, output_files.jsonFile!.name)}
                            >
                                Download
                            </button>
                        </div>
                    {/if}
                </div>

                {#if output_files.updateFile && output_files.jsonFile}
                    <button 
                        class="w-full px-4 py-2 bg-aaon-blue-light hover:bg-aaon-blue text-white rounded-md font-medium transition-colors duration-200"
                        onclick={downloadAllFiles}
                    >
                        Download Files
                    </button>
                {/if}

            </div>
        {/if}
    </div>
</main>