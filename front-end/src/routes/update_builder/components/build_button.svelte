<script lang="ts">
    import { debFiles } from '$lib/stores';
    import { toast } from 'svelte-sonner';
    import Upload from '$lib/assets/upload.svg';
    import Uploaded from '$lib/assets/uploaded.svg';

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
    
    // Drop zone related state
    let isDragOver = $state(false);
    let isProcessing = $state(false);
    
    // Enhanced UI state variables
    let buildStage = $state('idle'); // idle, clearing, uploading, preparing, building, signing, encrypting, finalizing
    let buildProgress = $state(0); // 0-100
    let uploadProgress = $state(0); // 0-100
    let buildStartTime = $state<number | null>(null);
    let elapsedTimeSeconds = $state<number>(0);
    let elapsedTimeText = $state<string>('0:00');
    let elapsedTimeInterval = $state<number | null>(null);
    let currentBuildStep = $state<string>('');
    let lastFactTime = $state<number | null>(null);
    
    let buildSteps = $state<{step: string, description: string, status: 'pending' | 'active' | 'complete' | 'error'}[]>([
        { step: 'Clearing Previous Files', description: 'Removing old build artifacts', status: 'pending' },
        { step: 'Uploading DEB Files', description: 'Transferring packages to build server', status: 'pending' },
        { step: 'Preparing Build Environment', description: 'Setting up build dependencies', status: 'pending' },
        { step: 'Building Update Package', description: 'Processing and assembling components', status: 'pending' },
        { step: 'Signing Update Package', description: 'Applying cryptographic signatures', status: 'pending' },
        { step: 'Encrypting Update Package', description: 'Securing package contents with AES-256 encryption', status: 'pending' },
        { step: 'Finalizing Build Process', description: 'Verifying package integrity and validity', status: 'pending' }
    ]);
    
    // Fun facts to display during the build
    let buildFacts = $state<string[]>([
        'The update package is cryptographically signed to ensure secure installation.',
        'Updates are specifically made to be compatible with the Stratus unit manager.',
        'The package build process generates both .update and .json files for to ensure version tracking.',
        'Each update includes a manifest of all included packages and their versions.',
        'Updates can be applied via USB or network depending on your configuration.',
        'The build process signs the .update package to ensure validity and integrity of updates applied to the Stratus device.',
        'Updates are safely compressed to minimize transfer time to the device.',
        'The build process automatically resolves package dependencies.',
        'Each generated update includes version tracking for rollback capabilities.',
        'The encryption used during the packaging process is the industry standard for file security.',
        'The signing process ensures only verified updates can be installed.',
        'The update system was designed for resilience, even during power interruptions.',
        'The update can be applied on the Stratus unit manager via the on-device UI with a single button press.'
    ]);
    
    let currentFactIndex = $state(0);
    let buildLogs = $state<{time: string, message: string, type: 'info' | 'success' | 'warning' | 'error'}[]>([]);
    
    // Helper function to update build progress and rotate fun facts
    function updateBuildProgress() {
        // Don't update anything if we're not in active build mode
        if (buildStage === 'idle' || buildStage === 'error' || buildProgress >= 100) {
            return;
        }
        
        // Rotate fun fact every 45 seconds
        const now = Date.now();
        if (!lastFactTime || (now - lastFactTime) > 45000) {
            currentFactIndex = (currentFactIndex + 1) % buildFacts.length;
            lastFactTime = now;
        }
        
        // Update elapsed time
        if (buildStartTime) {
            const elapsedMs = Date.now() - buildStartTime;
            elapsedTimeSeconds = Math.floor(elapsedMs / 1000);
            
            const minutes = Math.floor(elapsedTimeSeconds / 60);
            const seconds = elapsedTimeSeconds % 60;
            elapsedTimeText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    
    // Start/stop functions for elapsed time counter
    function startElapsedTimeCounter() {
        if (elapsedTimeInterval) {
            clearInterval(elapsedTimeInterval);
        }
        
        elapsedTimeInterval = setInterval(() => {
            if (buildStartTime) {
                const elapsedMs = Date.now() - buildStartTime;
                elapsedTimeSeconds = Math.floor(elapsedMs / 1000);
                
                const minutes = Math.floor(elapsedTimeSeconds / 60);
                const seconds = elapsedTimeSeconds % 60;
                elapsedTimeText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000) as unknown as number;
    }
    
    function stopElapsedTimeCounter() {
        if (elapsedTimeInterval) {
            clearInterval(elapsedTimeInterval);
            elapsedTimeInterval = null;
        }
    }
    
    // Navigation protection functions
    function enableNavigationProtection() {
        window.addEventListener('beforeunload', handleBeforeUnload);
    }
    
    function disableNavigationProtection() {
        window.removeEventListener('beforeunload', handleBeforeUnload);
    }
    
    function handleBeforeUnload(event: BeforeUnloadEvent) {
        event.preventDefault();
        event.returnValue = "Build in progress! Leaving this page will cancel the update package creation. Are you sure you want to leave?";
        return event.returnValue;
    }
    
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
        return "Drag & drop .deb/.zip files here, or click to upload";
    }
    
    // --- File Input Handlers ---
    function handleUploadClick() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = '.deb,.zip';
        
        // Listen for file selection
        fileInput.addEventListener('change', (event) => {
            const target = event.target as HTMLInputElement;
            if (target.files) {
                // Here we would normally process files, but we'll just 
                // display files that are already in the store
                // processFileList(target.files);
            }
        });
        
        // Trigger the file dialog
        fileInput.click();
    }
    
    function handleDrop(event: DragEvent) {
        event.preventDefault();
        isDragOver = false;
        // Here we would normally process files, but for this integration,
        // we're just demonstrating the UI combination
    }

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
        setStage('uploading', 5);

        if (!$debFiles || $debFiles.length === 0) {
            toast.error('Cannot upload DEB files', {
                description: 'Please upload at least one DEB file to generate an update package.'
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

                const batchProgress = Math.floor(((i + 1) / totalBatches) * 100);
                console.log(`Uploading batch ${i + 1}/${totalBatches} (${batch.length} files)...`);
                uploadProgress = batchProgress;
                // Maps upload progress (0-100) to 5-10% of total progress
                const totalProgress = Math.min(10, 5 + (batchProgress * 0.05));
                setStage('uploading', totalProgress);
                
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
            setStage('building', 30);

            const res = await fetch('/api/builder/build_update', {
                method: 'POST'
            });

            if (!res.ok) {
                throw new Error(`Pipeline failed: ${res.statusText}`);
            }

            const result = await res.json();
            console.log('Pipeline result:', result);
            
            // Since the pipeline runs in background, we need to wait before starting polling
            await new Promise(resolve => setTimeout(resolve, 10000));
            
            return true;
        } catch (err) {
            console.error('Error running update pipeline:', err);
            toast.error('Pipeline Error', {
                description: 'An error occurred while starting the update pipeline.'
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
    
    // Helper function to determine which step is active based on stage
    function getActiveStep() {
        switch (buildStage) {
            case 'clearing': return 0;
            case 'uploading': return 1;
            case 'preparing': return 2;
            case 'building': return 3;
            case 'signing': return 4;
            case 'encrypting': return 5;
            case 'finalizing': return 6;
            default: return 0;
        }
    }

    // Helper function to complete all remaining steps when files are found
    async function completeRemainingSteps() {
        // Determine the current step and complete all remaining steps
        const currentStepIndex = getActiveStep();
        const remainingSteps = [
            { stage: 'building', progress: 70, delay: 1500 },
            { stage: 'signing', progress: 80, delay: 2000 },
            { stage: 'encrypting', progress: 90, delay: 1500 },
            { stage: 'finalizing', progress: 100, delay: 1000 }
        ];
        
        // Filter steps that need to be completed
        const stepsToComplete = remainingSteps.filter((step, index) => {
            return currentStepIndex <= index + 2; // +2 because 'building' is step 3 in our buildSteps array
        });
        
        // Complete each step with appropriate delay
        for (const step of stepsToComplete) {
            setStage(step.stage, step.progress);
            await new Promise(resolve => setTimeout(resolve, step.delay));
        }
        
        // Ensure all steps are marked as complete and progress is at 100%
        buildSteps = buildSteps.map(step => ({ ...step, status: 'complete' }));
        buildProgress = 100;
    }

    // Helper function to update the build stage and progress
    function setStage(stage: string, progressTarget: number = -1) {
        buildStage = stage;
        
        // Find the current step number
        const currentStep = getActiveStep();
        
        // Mark all previous steps as complete, current step as active, and reset future steps
        buildSteps = buildSteps.map((step, index) => {
            if (index < currentStep) {
                return { ...step, status: 'complete' };
            } else if (index === currentStep) {
                return { ...step, status: 'active' };
            } else {
                return { ...step, status: 'pending' };
            }
        });
        
        // Set the progress target (if specified)
        if (progressTarget > 0) {
            // Only increase progress, never go backward
            buildProgress = Math.max(buildProgress, progressTarget);
            // Update log
        }
    }

    async function checkForFiles(pollInterval = 20000, maxWait = 10 * 60 * 1000) {
        // Initial values
        const start = Date.now();
        let attempts = 0;
        const buildingProgressStart = 30;  // Start at 30%
        const buildingProgressEnd = 70;   // End at 70% (building phase)
        const expectedBuildTimeMs = 7 * 60 * 1000; // 7 minutes for build phase
        
        console.log(`Starting polling for output files every ${pollInterval/1000}s, timeout after ${maxWait/60000} min`);
        
        // First, check immediately in case files are already ready
        try {
            const success = await prepareDownload();
            if (success) {
                console.log("Files found immediately!");
                
                // Always ensure we go through all remaining steps when files are found
                await completeRemainingSteps();
                return true;
            }
        } catch (error) {
            console.log("First check failed:", error instanceof Error ? error.message : String(error));
            // Continue to polling loop
        }

        // Polling loop - this is the main building phase (30% to 70%)
        while (Date.now() - start < maxWait) {
            attempts++;
            try {
                console.log(`Polling for files at ${new Date().toLocaleTimeString()}...`);
                
                // Calculate progress based on elapsed time
                const elapsedMs = Date.now() - start;
                
                // Gradually increase the progress - weighted toward end of building phase
                // Use a non-linear formula to make progress seem more natural
                const progressRatio = Math.min(1, elapsedMs / expectedBuildTimeMs);
                const weightedProgress = buildingProgressStart + 
                    (buildingProgressEnd - buildingProgressStart) * progressRatio;
                
                // Only update progress if it's higher than current (never go backward)
                if (weightedProgress > buildProgress) {
                    setStage('building', Math.min(buildingProgressEnd, Math.floor(weightedProgress)));
                }
                
                const success = await prepareDownload();
                if (success) {
                    console.log("Files found during polling!");
                    
                    // Always ensure we go through all remaining steps when files are found
                    await completeRemainingSteps();
                    
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

            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        toast.error('Pipeline Timeout', {
            description: `Build process did not complete within ${maxWait / 60000} minutes.`
        });
        return false;
    }

    async function updatePipeline() {
        if (isPreparing) return; // Prevent multiple clicks

        try {
            // Initialize build state
            isPreparing = true;
            buildStartTime = Date.now();
            buildProgress = 0;
            uploadProgress = 0;
            elapsedTimeSeconds = 0;
            startElapsedTimeCounter();
            enableNavigationProtection();
            
            // Reset UI state
            buildLogs = [];
            currentFactIndex = 0;
            lastFactTime = null;
            
            // Start a timer for progress and fact rotation
            const progressInterval = setInterval(updateBuildProgress, 1000);
            
            // Reset output files state
            output_files.isReady = false;
            output_files.updateFile = null;
            output_files.jsonFile = null;
            output_files.allFiles = [];

            // Add initial log

            // 0. Clear previous DEB files
            setStage('clearing', 1);
            const clearSuccess = await clearPreviousDebs();
            if (!clearSuccess) {
                // Stop if clearing fails, as it might indicate a server problem
                toast.error('Could not clear previous files');
                setStage('error');
                stopElapsedTimeCounter();
                clearInterval(progressInterval);
                return;
            }

            // 1. Upload DEB files to correct location
            setStage('uploading', 5);
            const uploadSuccess = await upload_debs();
            if (!uploadSuccess) {
                toast.error('Upload failed');
                setStage('error');
                stopElapsedTimeCounter();
                clearInterval(progressInterval);
                return;
            }

            // 2. Prepare environment
            setStage('preparing', 10);
            
            // 3. Run the update pipeline (background process)
            const pipelineSuccess = await run_update_pipeline();
            if (!pipelineSuccess) {
                toast.error('Pipeline start failed');
                setStage('error');
                stopElapsedTimeCounter();
                clearInterval(progressInterval);
                return;
            }
    
            // 4. Wait for pipeline to complete and prepare download links
            // Check for files immediately in case they already exist
            try {
                const immediateSuccess = await prepareDownload();
                if (immediateSuccess) {
                    toast.success('Files already available! 🎉', {
                        description: 'Update package is ready for download.'
                    });
                    // Make sure all steps are completed and progress bar fills to 100%
                    await completeRemainingSteps();
                    stopElapsedTimeCounter();
                    clearInterval(progressInterval);
                    return;
                }
            } catch (error) {
                console.log('Initial file check failed, starting polling:', error instanceof Error ? error.message : String(error));
                // Continue with polling
            }
            
            // Start polling for files - long building process happens here
            const prepareSuccess = await checkForFiles();
            
            if (!prepareSuccess) {
                toast.error('Failed to find output files');
                stopElapsedTimeCounter();
                clearInterval(progressInterval);
                return;
            }

            toast.success('Pipeline Complete! 🎉', {
                description: 'Update package is ready for download.',
            });
            
            stopElapsedTimeCounter();
            clearInterval(progressInterval);
            disableNavigationProtection();
    
        } catch (error) {
            console.error('Error in update pipeline:', error);
            setStage('error');
            stopElapsedTimeCounter();
            disableNavigationProtection();
        } finally {
            isPreparing = false;
            disableNavigationProtection();
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
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Apply animations */
    .bg-aaon-blue {
        transition: width 0.5s ease-out;
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    .download-section {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .download-section:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
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
            <!-- Combined Drop Zone and Build Interface -->
            <div class="mt-6 flex flex-col items-center justify-center space-y-4">
                {#if !isPreparing}
                    <!-- Show Generate Button below the dropzone -->
                    <button 
                    class="mb-4 px-4 py-3 rounded-md font-base text-lg sm:text-xl transition-colors duration-200
                    {$debFiles.length === 0 ? 'border border-light-text bg-input-background cursor-not-allowed text-light-text' : 'bg-aaon-blue hover:bg-gray-400 hover:cursor-pointer text-white'}"        
                    disabled={!canGenerate || isPreparing}
                    onclick={updatePipeline}        
                    >
                        <span>Generate Update Package</span>
                    </button>
                {:else}
                    <!-- Enhanced Build Progress UI - Using the same dimensions/style as the drop zone -->
                    <div class="w-full max-w-2xl bg-white rounded-lg shadow-md p-4 border border-gray-200">
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-lg font-semibold text-gray-800">Building Update Package</h3>
                            <div class="flex items-center">
                                <span class="spinner mr-2"></span>
                                <div class="flex items-center space-x-4">
                                    <span class="text-sm text-gray-600">
                                        Elapsed: {elapsedTimeText}
                                    </span>
                                </div>
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
                                <span class="text-sm text-aaon-blue font-semibold">Did you know?</span>
                            </div>
                            <p class="text-sm text-text-aaon-blue mt-1">{buildFacts[currentFactIndex]}</p>
                        </div>
                    </div>
                {/if}
            </div>
        {:else}
            <!-- Download Section - Only show when files are ready -->
            <div class="w-full flex flex-col items-center justify-center mt-8">
                <div class="download-section max-w-md w-full bg-white rounded-lg border border-gray-200 shadow-lg p-6 animate-fadeIn">
                    <div class="text-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-green-500 mb-2" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                        <h3 class="text-xl font-semibold text-dark-text">Build Complete</h3>
                        <p class="text-sm text-gray-600 mt-1">Your update package is ready for download</p>
                    </div>
                    
                    <div class="space-y-3 mb-6">
                        {#if output_files.updateFile}
                            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-200 hover:bg-blue-50 transition-colors">
                                <div class="flex-1">
                                    <div class="font-medium text-sm">{output_files.updateFile.name}</div>
                                    <div class="text-xs text-gray-500">Update Package</div>
                                </div>
                                <button 
                                    class="px-3 py-2 bg-aaon-blue hover:bg-aaon-blue-dark text-white rounded-md text-sm transition-all duration-200 shadow-sm hover:shadow"
                                    onclick={() => downloadFile(output_files.updateFile!.path, output_files.updateFile!.name)}
                                >
                                    Download
                                </button>
                            </div>
                        {/if}
                        
                        {#if output_files.jsonFile}
                            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-200 hover:bg-blue-50 transition-colors">
                                <div class="flex-1">
                                    <div class="font-medium text-sm">{output_files.jsonFile.name}</div>
                                    <div class="text-xs text-gray-500">Package Version Tracking JSON</div>
                                </div>
                                <button 
                                    class="px-3 py-2 bg-aaon-blue hover:bg-aaon-blue-dark text-white rounded-md text-sm transition-all duration-200 shadow-sm hover:shadow"
                                    onclick={() => downloadFile(output_files.jsonFile!.path, output_files.jsonFile!.name)}
                                >
                                    Download
                                </button>
                            </div>
                        {/if}
                    </div>

                    {#if output_files.updateFile && output_files.jsonFile}
                        <button 
                            class="w-full px-4 py-3 bg-aaon-blue hover:bg-aaon-blue-dark text-white rounded-md font-medium transition-all duration-200 shadow-sm hover:shadow flex items-center justify-center gap-2"
                            onclick={downloadAllFiles}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                            Download All Files
                        </button>
                    {/if}
                </div>
            </div>

        {/if}
    </div>
</main>