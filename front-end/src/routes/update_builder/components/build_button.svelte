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
    
    // Enhanced UI state variables
    let buildStage = $state('idle'); // idle, uploading, preparing, building, packaging, signing, finishing
    let buildProgress = $state(0); // 0-100
    let uploadProgress = $state(0); // 0-100
    let buildStartTime = $state<number | null>(null);
    let estimatedTimeRemaining = $state<string | null>(null);
    let currentBuildStep = $state<string>('');
    let buildSteps = $state<{step: string, description: string, status: 'pending' | 'active' | 'complete' | 'error'}[]>([
        { step: 'Uploading Files', description: 'Transferring DEB packages to the build server', status: 'pending' },
        { step: 'Preparing Build Environment', description: 'Setting up the repository structure', status: 'pending' },
        { step: 'Building Package', description: 'Generating the update package structure', status: 'pending' },
        { step: 'Signing Package', description: 'Cryptographically signing the update files', status: 'pending' },
        { step: 'Finishing Up', description: 'Final verification and cleanup', status: 'pending' }
    ]);
    
    // Fun facts to display during the build
    let buildFacts = $state<string[]>([
        'The update package is cryptographically signed to ensure secure installation.',
        'Package verification happens automatically during the update process.',
        'Updates are compatible with all Stratus hardware configurations.',
        'The package build process generates both .update and .json files for tracking.',
        'Each update includes a manifest of all included packages and their versions.',
        'Updates can be applied via USB or network depending on your configuration.',
        'The build process includes multiple verification steps for reliability.',
        'Updates are compressed to minimize transfer time to the device.',
        'The build system automatically resolves package dependencies.',
        'Each generated update includes version tracking for rollback capabilities.'
    ]);
    
    let currentFactIndex = $state(0);
    let buildLogs = $state<{time: string, message: string, type: 'info' | 'success' | 'warning' | 'error'}[]>([]);

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
        updateBuildStage('uploading', 5);
        addBuildLog(`Starting upload of ${$debFiles.length} DEB files`);

        if (!$debFiles || $debFiles.length === 0) {
            toast.error('Cannot upload DEB files', {
                description: 'Please upload at least one DEB file to generate an update package.',
                duration: 1500
            });
            addBuildLog('No DEB files to upload', 'error');
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

                const batchProgress = Math.floor(((i + 1) / totalBatches) * 100);
                console.log(`Uploading batch ${i + 1}/${totalBatches} (${batch.length} files)...`);
                uploadProgress = batchProgress;
                updateBuildStage('uploading', 5 + (batchProgress * 0.15)); // Maps 0-100 to 5-20% of total progress
                
                addBuildLog(`Uploading batch ${i + 1}/${totalBatches} (${batch.length} files)`);

                const response = await fetch('/api/builder/upload_debs', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error(`Upload failed for batch ${i + 1}:`, response.status, errorText);
                    addBuildLog(`Upload failed for batch ${i + 1}: ${response.statusText}`, 'error');
                    throw new Error(`Upload failed: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`Batch ${i + 1} response:`, data);
                addBuildLog(`Successfully uploaded batch ${i + 1}/${totalBatches}`, 'success');
                successCount += batch.length;
            }

            toast.success('DEB files uploaded successfully', {
                description: `All ${successCount} files uploaded!`,
                duration: 1500
            });

            uploadProgress = 100;
            addBuildLog(`Upload complete: ${successCount} files uploaded`, 'success');
            return true;
        } catch (err) {
            console.error('Error uploading DEB files:', err);
            toast.error('Upload Error', {
                description: 'An error occurred while uploading DEB files. Please try again.',
                duration: 1500
            });
            addBuildLog(`Upload error: ${err instanceof Error ? err.message : String(err)}`, 'error');
            return false;
        }
    }

    async function run_update_pipeline() {
        try {
            updateBuildStage('preparing', 20);
            addBuildLog('Starting update package build pipeline');

            // Run update pipeline
            const res = await fetch('/api/builder/build_update', {
                method: 'POST'
            });

            if (!res.ok) {
                addBuildLog(`Pipeline failed: ${res.statusText}`, 'error');
                throw new Error(`Pipeline failed: ${res.statusText}`);
            }

            const result = await res.json();
            console.log('Pipeline result:', result);
            addBuildLog('Build pipeline started successfully');
            
            toast.success('Pipeline Started', {
                description: 'Update package build started in background. Please wait...',
                duration: 2000,
            });
            
            // Move to building stage
            updateBuildStage('building', 25);
            
            // Simulate progress updates for the longer building process
            // We'll update from 25% to 75% during this phase
            const progressUpdates = [
                { stage: 'building', progress: 35, message: 'Preparing package structure', delay: 30000 },
                { stage: 'building', progress: 45, message: 'Assembling package components', delay: 45000 },
                { stage: 'building', progress: 55, message: 'Processing manifest files', delay: 60000 },
                { stage: 'signing', progress: 65, message: 'Applying cryptographic signatures', delay: 75000 },
                { stage: 'signing', progress: 75, message: 'Verifying package integrity', delay: 90000 },
                { stage: 'finishing', progress: 85, message: 'Finalizing package assembly', delay: 105000 }
            ];
            
            // Schedule these updates
            progressUpdates.forEach(update => {
                setTimeout(() => {
                    updateBuildStage(update.stage, update.progress);
                    addBuildLog(update.message);
                }, update.delay);
            });

            // Since the pipeline runs in background, we need to wait before starting polling
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
            
            return true;
        } catch (err) {
            console.error('Error running update pipeline:', err);
            toast.error('Pipeline Error', {
                description: 'An error occurred while starting the update pipeline. Please try again.',
                duration: 1500,
            });
            addBuildLog(`Pipeline error: ${err instanceof Error ? err.message : String(err)}`, 'error');
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
    
    // Helper functions for build UI
    function addBuildLog(message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        buildLogs = [...buildLogs, { time: timeStr, message, type }];
        
        // Keep the log at a reasonable size
        if (buildLogs.length > 50) {
            buildLogs = buildLogs.slice(-50);
        }
    }
    
    function updateBuildStage(stage: string, progress: number) {
        buildStage = stage;
        buildProgress = progress;
        
        // Update the build steps based on the stage
        let updatedSteps = [...buildSteps];
        
        switch(stage) {
            case 'uploading':
                updatedSteps[0].status = 'active';
                currentBuildStep = 'Uploading files to build server';
                break;
            case 'preparing':
                updatedSteps[0].status = 'complete';
                updatedSteps[1].status = 'active';
                currentBuildStep = 'Preparing build environment';
                break;
            case 'building':
                updatedSteps[0].status = 'complete';
                updatedSteps[1].status = 'complete';
                updatedSteps[2].status = 'active';
                currentBuildStep = 'Building update package';
                break;
            case 'signing':
                updatedSteps[0].status = 'complete';
                updatedSteps[1].status = 'complete';
                updatedSteps[2].status = 'complete';
                updatedSteps[3].status = 'active';
                currentBuildStep = 'Signing update package';
                break;
            case 'finishing':
                updatedSteps[0].status = 'complete';
                updatedSteps[1].status = 'complete';
                updatedSteps[2].status = 'complete';
                updatedSteps[3].status = 'complete';
                updatedSteps[4].status = 'active';
                currentBuildStep = 'Finalizing build';
                break;
            case 'complete':
                updatedSteps = updatedSteps.map(step => ({...step, status: 'complete'}));
                currentBuildStep = 'Build complete';
                break;
        }
        
        buildSteps = updatedSteps;
        
        // Rotate through facts every 15 seconds during the build
        const factRotateInterval = setInterval(() => {
            currentFactIndex = (currentFactIndex + 1) % buildFacts.length;
        }, 15000);
        
        // Calculate estimated time remaining
        if (buildStartTime && progress > 0) {
            const elapsedMs = Date.now() - buildStartTime;
            const estimatedTotalMs = elapsedMs / (progress / 100);
            const remainingMs = estimatedTotalMs - elapsedMs;
            
            if (remainingMs > 0) {
                const remainingMins = Math.floor(remainingMs / 60000);
                const remainingSecs = Math.floor((remainingMs % 60000) / 1000);
                estimatedTimeRemaining = `${remainingMins}:${remainingSecs.toString().padStart(2, '0')}`;
            } else {
                estimatedTimeRemaining = "Almost done";
            }
        }
        
        // Clear interval when build is complete
        if (stage === 'complete') {
            clearInterval(factRotateInterval);
        }
    }

    async function checkForFiles(pollInterval = 20000, maxWait = 10 * 60 * 1000) {
        // pollInterval: time between checks in ms (20s)
        // maxWait: max wait time in ms (10 min default)
        const start = Date.now();

        console.log(`Starting polling for output files every ${pollInterval/1000}s, timeout after ${maxWait/60000} min`);
        addBuildLog(`Checking for output files (polling every ${pollInterval/1000}s)`);

        // Try immediately first
        try {
            const success = await prepareDownload();
            if (success) {
                console.log("Files found immediately!");
                addBuildLog("Files found immediately!", 'success');
                updateBuildStage('complete', 100);
                return true;
            }
        } catch (error) {
            console.log("First check failed:", error instanceof Error ? error.message : String(error));
            addBuildLog("First check for files - still building");
            // Continue to polling loop
        }

        let pollCount = 0;
        while (Date.now() - start < maxWait) {
            pollCount++;
            try {
                console.log(`Polling for files at ${new Date().toLocaleTimeString()}...`);
                
                // Update the progress based on time elapsed
                const elapsedMs = Date.now() - start;
                const expectedBuildTimeMs = 7 * 60 * 1000; // 7 minutes (avg of 6-8 minutes)
                const timeBasedProgress = Math.min(95, 85 + ((elapsedMs / expectedBuildTimeMs) * 15));
                
                if (pollCount % 3 === 0) { // Don't add too many log entries
                    addBuildLog(`Checking for build completion (${Math.round((elapsedMs/60000) * 10) / 10} minutes elapsed)`);
                }
                
                updateBuildStage('finishing', timeBasedProgress);
                
                const success = await prepareDownload();
                if (success) {
                    console.log("Files found during polling!");
                    addBuildLog("Build complete! Output files found.", 'success');
                    updateBuildStage('complete', 100);
                    
                    // Try to use desktop notifications if available
                    try {
                        if ('Notification' in window && Notification.permission === 'granted') {
                            new Notification('Update Package Ready', {
                                body: 'Your update package build has completed and is ready for download.',
                                icon: '/favicon.ico'
                            });
                        } else if ('Notification' in window && Notification.permission !== 'denied') {
                            await Notification.requestPermission();
                        }
                    } catch (notificationError) {
                        console.error("Notification error:", notificationError);
                    }
                    
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
        addBuildLog(`Build timed out after ${maxWait/60000} minutes`, 'error');
        return false;
    }

    async function updatePipeline() {
        if (isPreparing) return; // Prevent multiple clicks

        try {
            // Initialize build UI
            isPreparing = true;
            buildStartTime = Date.now();
            buildProgress = 0;
            uploadProgress = 0;
            currentBuildStep = 'Starting build process';
            estimatedTimeRemaining = null;
            buildLogs = [];
            buildSteps = buildSteps.map(step => ({...step, status: 'pending'}));
            currentFactIndex = 0;
            
            // Reset output files state
            output_files.isReady = false;
            output_files.updateFile = null;
            output_files.jsonFile = null;
            output_files.allFiles = [];

            // Add initial log
            addBuildLog('Starting update package build process', 'info');

            // 0. Clear previous DEB files
            updateBuildStage('uploading', 0);
            toast.info('Step 1/4: Clearing previous files...');
            addBuildLog('Clearing previous build files');
            const clearSuccess = await clearPreviousDebs();
            if (!clearSuccess) {
                // Stop if clearing fails, as it might indicate a server problem
                toast.error('Could not clear previous files. Aborting pipeline.');
                addBuildLog('Failed to clear previous files', 'error');
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
                updateBuildStage('idle', 0);
                return;
            }
    
            // 3. Wait for pipeline to complete and prepare download links
            toast.info('Step 4/4: Waiting for build to complete...');
            
            // Check for files immediately in case they already exist
            console.log('Checking immediately for existing output files...');
            addBuildLog('Checking for existing output files');
            try {
                const immediateSuccess = await prepareDownload();
                if (immediateSuccess) {
                    toast.success('Files already available! 🎉', {
                        description: 'Update package is ready for download.',
                        duration: 3000,
                    });
                    updateBuildStage('complete', 100);
                    addBuildLog('Build complete! Files ready for download', 'success');
                    return;
                }
            } catch (error) {
                console.log('Initial file check failed, will start polling:', error instanceof Error ? error.message : String(error));
                addBuildLog('Build in progress, waiting for completion');
            }
            
            // Start polling for files
            const prepareSuccess = await checkForFiles();
            if (!prepareSuccess) {
                toast.error('Failed to find output files');
                addBuildLog('Build failed - no output files found', 'error');
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
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes slideIn {
        0% { transform: translateX(-10px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    /* Apply animations */
    .bg-aaon-blue {
        transition: width 0.5s ease-out;
    }
    
    details[open] summary ~ * {
        animation: fadeIn 0.3s ease-out;
    }
    
    .build-step {
        animation: slideIn 0.3s ease-out;
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
            <!-- Build button and loading interface -->
            <div class="mt-6 flex flex-col items-center justify-center space-y-4">
                {#if !isPreparing}
                    <button 
                    class="px-4 py-3 rounded-md font-base text-lg sm:text-xl transition-colors duration-200
                    {$debFiles.length === 0 ? 'border border-light-text bg-input-background cursor-not-allowed text-light-text' : 'bg-aaon-blue hover:bg-gray-400 hover:cursor-pointer text-white'}"        
                    disabled={!canGenerate || isPreparing}
                    onclick={updatePipeline}        
                    >
                        <span>Generate Update Package</span>
                    </button>
                {:else}
                    <!-- Enhanced Build Progress UI -->
                    <div class="w-full max-w-2xl bg-white rounded-lg shadow-md p-4 border border-gray-200">
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-lg font-semibold text-gray-800">Building Update Package</h3>
                            <div class="flex items-center">
                                <span class="spinner mr-2"></span>
                                <span class="text-sm text-gray-600">
                                    {#if estimatedTimeRemaining}
                                        Est. remaining: {estimatedTimeRemaining}
                                    {:else}
                                        Processing...
                                    {/if}
                                </span>
                            </div>
                        </div>
                        
                        <!-- Overall progress bar -->
                        <div class="w-full bg-gray-200 rounded-full h-4 mb-4">
                            <div class="bg-aaon-blue h-4 rounded-full transition-all duration-300 ease-out" style="width: {buildProgress}%"></div>
                        </div>
                        
                        <div class="text-sm text-gray-700 font-medium mb-2">
                            {currentBuildStep}
                        </div>
                        
                        <!-- Build Steps -->
                        <div class="space-y-3 mb-4">
                            {#each buildSteps as step, i}
                                <div class="flex items-center">
                                    <div class="w-6 h-6 flex items-center justify-center rounded-full mr-2 
                                        {step.status === 'complete' ? 'bg-green-100 text-green-600' : 
                                          step.status === 'active' ? 'bg-blue-100 text-blue-600' :
                                          step.status === 'error' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-400'}">
                                        {#if step.status === 'complete'}
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                            </svg>
                                        {:else if step.status === 'active'}
                                            <div class="h-2 w-2 bg-blue-600 rounded-full"></div>
                                        {:else if step.status === 'error'}
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                            </svg>
                                        {:else}
                                            <span class="text-xs">{i+1}</span>
                                        {/if}
                                    </div>
                                    <div>
                                        <div class="text-sm font-medium 
                                            {step.status === 'active' ? 'text-blue-600' : 
                                             step.status === 'complete' ? 'text-green-600' : 
                                             step.status === 'error' ? 'text-red-600' : 'text-gray-500'}">
                                            {step.step}
                                        </div>
                                        <div class="text-xs text-gray-500">{step.description}</div>
                                    </div>
                                </div>
                            {/each}
                        </div>
                        
                        <!-- Fun fact -->
                        <div class="bg-blue-50 border border-blue-100 rounded-md p-3 mb-4">
                            <div class="flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                                </svg>
                                <span class="text-sm text-blue-800">Did you know?</span>
                            </div>
                            <p class="text-sm text-blue-700 mt-1">{buildFacts[currentFactIndex]}</p>
                        </div>
                        
                        <!-- Collapsible build log -->
                        <details class="rounded-md border border-gray-200">
                            <summary class="px-3 py-2 bg-gray-50 text-sm font-medium cursor-pointer hover:bg-gray-100">
                                Build Log ({buildLogs.length} entries)
                            </summary>
                            <div class="p-2 max-h-40 overflow-y-auto font-mono text-xs">
                                {#each buildLogs as log}
                                    <div class="py-1 border-b border-gray-100 last:border-0 
                                        {log.type === 'error' ? 'text-red-600' : 
                                         log.type === 'success' ? 'text-green-600' :
                                         log.type === 'warning' ? 'text-yellow-600' : 'text-gray-700'}">
                                        <span class="text-gray-500">[{log.time}]</span> {log.message}
                                    </div>
                                {/each}
                            </div>
                        </details>
                    </div>
                {/if}
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