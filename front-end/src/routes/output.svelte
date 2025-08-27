<script lang="ts">
    import { serialFormStore, jsonFileStore } from '$lib/stores';
    // Remove the Progress import since we're using Spinner instead
    // import Progress from '$lib/components/ui/progress/progress.svelte';

    import { toast } from 'svelte-sonner';

    interface OutputFile {
        name: string;
        url: string | null;
        isReady: boolean;
    }

    // State for the output file
    let output_file = $state<OutputFile>({
        name: "",
        url: null,
        isReady: false
    });
    
    // States for UI
    let isPreparing = $state(false);
    // Remove progress state since we're not using progress bar anymore
    // let progress = $state(0);
    let errorMessage = $state("");
    
    // Use auto-subscribed store values with $state to track them
    let serialFormValue = $state<{
        serial_number: string,
        second_serial_number: string,
        match: boolean
    }>({
        serial_number: "",
        second_serial_number: "",
        match: false
    });
    
    let jsonFileValue = $state<{
        file: File | null
    }>({
        file: null
    });
    
    // Set up subscriptions to update our local state when stores change
    serialFormStore.subscribe(value => {
        serialFormValue = value;
    });
    
    jsonFileStore.subscribe(value => {
        jsonFileValue = value;
    });
    
    // Derived value to check if we can generate an output
    let canGenerate = $derived(serialFormValue?.match === true && jsonFileValue?.file !== null);
    
    // Function to prepare & fetch file from backend
    async function prepareDownload() {
        if (!canGenerate) return;

        try {
            // Remove the fake progress loop since we're using a spinner instead
            // Just add a small delay for better UX
            await new Promise(resolve => setTimeout(resolve, 500));

            // 1. Ask backend which files exist
            const date = new Date();
            const yyyymmdd = date.toISOString().slice(0, 10).replace(/-/g, '');
            console.log("Fetching files for date:", yyyymmdd);
            const filename = `Stratus_${yyyymmdd}.command`;

            // 2. Fetch the file
            const fileRes = await fetch(`/api/command/${filename}`);
            if (!fileRes.ok) {
                throw new Error(`Failed to fetch file: ${filename}`);
            }

            const blob = await fileRes.blob();
            const url = window.URL.createObjectURL(blob);

            // 3. Save state for download button
            output_file = {
                name: filename,
                url: url,
                isReady: true
            };

            toast.success("File Prepared", {
                description: `Your encrypted command package (${filename}) is ready.`,
                duration: 2000,
            });

        } catch (error) {
            errorMessage = "An error occurred while preparing your file. Please try again.";
            console.error("Error fetching file:", error);
            toast.error("File Preparation Error", {
                description: errorMessage,
                duration: 3000,
            });
            throw error; // Re-throw so the parent function can handle it
        }
    }

    // Function to trigger download
    function downloadFile() {
        if (!output_file.isReady || !output_file.url) return;

        const a = document.createElement("a");
        a.href = output_file.url;
        a.download = output_file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function resetOutput() {
        output_file = {
            name: "",
            url: null,
            isReady: false
        };
        isPreparing = false;
        // Remove progress reset since we're not using it anymore
        // progress = 0;
        errorMessage = "";
        jsonFileValue.file = null; // Reset the JSON file state
        serialFormValue.serial_number = "";
        serialFormValue.second_serial_number = "";
        serialFormValue.match = false;
        // Reset the file input element
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) fileInput.value = ''; // Clear the file input
    }
    
    // API ---

    async function save_serial_numbers() {
        let message = "";
        if (!serialFormValue.match) {
            toast.error("Serial numbers do not match", {
                description: "Please ensure both serial numbers are entered correctly.",
                duration: 2000,
            });
            throw new Error("Serial numbers do not match");
        }

        try {
            const bodyText = `${serialFormValue.serial_number}\n${serialFormValue.second_serial_number}`;
            const response = await fetch('/api/inputs/serial-numbers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    serial1: serialFormValue.serial_number,
                    serial2: serialFormValue.second_serial_number
                })
            });
            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }
            const data = await response.json();
            console.log('Serial numbers saved successfully:', data);

        } catch (error) {
            console.error('Error:', error);
            message = "Failed to save serial number";
            toast.error(message, {
                description: message,
                duration: 2000,
            });
        }
    }

    async function save_input_file() {
        if (!jsonFileValue.file) {
            return toast.error("No file selected", {
                description: "Please upload a JSON file before proceeding.",
                duration: 2000,
            });
        }

        try {
            const formData = new FormData();
            formData.append('file', jsonFileValue.file);

            const response = await fetch('/api/inputs/json-file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('JSON file saved successfully:', data);
        } catch (error) {
            console.error('Error uploading file:', error);
            toast.error('File upload failed', {
                description: "An error occurred while uploading the file.",
                duration: 2000,
            });
        }
        
    }

    async function run_pipeline() {
        if (!canGenerate) {
            return toast.error("Cannot run pipeline", {
                description: "Please ensure all inputs are valid before running the pipeline.",
                duration: 2000,
            });
        }

        try {
            const res = await fetch("/api/pipeline/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });

            const data = await res.json();

            if (!res.ok || data.success === false) {
                return toast.error("Pipeline Error", {
                    description: data.stderr || data.message || "An error occurred while starting the pipeline.",
                    duration: 4000,
                });
            }

            // Print everything to console for now
            console.log("Pipeline Success:", data);

            toast.success("Pipeline started", {
                description: data.message || "Your command package is being processed.",
                duration: 1500,
            });

        } catch (err) {
            console.error("Pipeline run error:", err);
            toast.error("Pipeline Failed", {
                description: "Unexpected error",
                duration: 3000,
            });
        }
    }

    // This function combines the download preparation and saving serial numbers
    async function prepareDownloadAndSave() {
        if (isPreparing) return;
        
        try {
            isPreparing = true;
            errorMessage = "";
            
            // Save serial numbers to serianl_number.txt
            await save_serial_numbers();
            
            // Save the JSON file as commands.json
            await save_input_file();
            
            // Package the .command file
            await run_pipeline();
            
            // Serve the .command file for download
            await prepareDownload();
        
        } catch (error) {
            console.error("Error in prepareDownloadAndSave:", error);
            toast.error("Error preparing download", {
                description: "An error occurred while preparing your download.",
                duration: 3000,
            });
        } finally {
            isPreparing = false;
        }

    }

</script>

<style>
    .spinner {
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

<main class="p-4 sm:p-5 w-full bg-card-background rounded-2xl shadow-lg">
    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">Output File</h1>
    <p class="pt-1 sm:pt-2 text-sm sm:text-base text-light-text">
        Once your serial number is verified and JSON file uploaded, your encrypted command package will be ready for download.
    </p>
    
    <div class="mt-4 sm:mt-6">
        {#if !output_file.isReady}
            <button 
                onclick={prepareDownloadAndSave}
                disabled={!canGenerate || isPreparing} 
                class="w-full py-2 sm:py-3 px-3 sm:px-4 flex items-center justify-center text-sm sm:text-base {!canGenerate || isPreparing ? 'bg-gray-300 cursor-not-allowed' : 'bg-aaon-blue hover:bg-aaon-blue-light text-white'} rounded-md transition-colors duration-200"
            >
                {#if isPreparing}
                    <div class="spinner mr-2"></div>
                    <span class="text-aaon-blue">Preparing...</span>
                {:else}
                    <span class="text-white">Generate Encrypted Command Package</span>
                {/if}
            </button>
            
            {#if !canGenerate && !isPreparing}
                <p class="text-xs sm:text-sm text-red-500 mt-2">
                    Please ensure you've provided matching serial numbers and uploaded a JSON file.
                </p>
            {/if}
            
            {#if errorMessage}
                <p class="text-xs sm:text-sm text-red-500 mt-2">{errorMessage}</p>
            {/if}
        {:else}
            <div class="border border-gray-200 rounded-md p-3 sm:p-4 mb-3 sm:mb-4 bg-gray-50">
                <p class="font-medium mb-1 text-sm sm:text-base">Your file is ready for download</p>
                <p class="text-xs sm:text-sm text-gray-600 mb-2 sm:mb-3 break-all">{output_file.name}</p>
                <button 
                    onclick={downloadFile}
                    class="flex items-center space-x-2 bg-aaon-blue hover:bg-aaon-blue-light text-white py-1.5 sm:py-2 px-3 sm:px-4 text-sm sm:text-base rounded-md transition-colors duration-200"
                >
                    <span>Download File</span>
                </button>
            </div>
            
            <button 
                onclick={() => { resetOutput(); }}
                class="w-full py-1.5 sm:py-2 px-3 sm:px-4 border border-aaon-blue text-aaon-blue text-sm sm:text-base hover:bg-gray-100 rounded-md transition-colors duration-200"
            >
                Generate New Package
            </button>
        {/if}
    </div>
</main>