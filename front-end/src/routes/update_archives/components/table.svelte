<script lang="ts">
    import { onMount } from 'svelte';
    import Entry from "./entry.svelte";
    
    // State variables
    type FileEntry = {
        fileName: string;
        filePath: string;
        fileSize: string;
        createdDate: string;
        version?: string;
        releaseType?: string;
        parentDir?: string;
    };

    let files: FileEntry[] = [];
    let loading: boolean = true;
    let error: string | null = null;
    let selectedFiles: string[] = [];
    let searchTerm: string = '';
    let filteredFiles: FileEntry[] = [];
    
    // Pagination state
    let currentPage = 1;
    let itemsPerPage = 10; // Show 10 items per page
    let paginatedFiles: FileEntry[] = [];
    
    // Derived state for filtered files
    $: filteredFiles = files.filter((file: FileEntry) => 
        file.fileName.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // Reset to first page when filter changes
    $: {
        if (searchTerm) {
            currentPage = 1;
        }
    }
    
    // Calculate total number of pages
    $: totalPages = Math.max(1, Math.ceil(filteredFiles.length / itemsPerPage));
    
    // Ensure current page is valid
    $: {
        if (currentPage > totalPages) {
            currentPage = totalPages;
        }
    }
    
    // Get current page's files
    $: paginatedFiles = filteredFiles.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );
    
    // Check if all filtered files on current page are selected
    $: allSelected = paginatedFiles.length > 0 && 
                     paginatedFiles.every((file: FileEntry) => selectedFiles.includes(file.filePath));
    
    // Function to load files from the API
    async function loadFiles() {
        loading = true;
        error = null;
        
        try {
            const response = await fetch('/api/archives/list?filter_ext=update');
            
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Transform the file data
            if (Array.isArray(data.items)) {
                files = data.items
                    .filter((item: any) => !item.is_directory)
                    .map((item: any): FileEntry => {
                        const fileName = item.name;
                        const filePath = item.path;
                        
                        // Use the enhanced metadata from our API
                        let createdDate = '';
                        
                        // 1. Try to use build_date_formatted from API (our preferred format)
                        if (item.build_date_formatted) {
                            createdDate = item.build_date_formatted;
                        }
                        // 2. Or try to use build_date and format it
                        else if (item.build_date) {
                            try {
                                const date = new Date(item.build_date);
                                createdDate = new Intl.DateTimeFormat('en-US', { 
                                    year: 'numeric', 
                                    month: 'short', 
                                    day: 'numeric' 
                                }).format(date);
                            } catch (e) {
                                console.warn(`Failed to format build date: ${item.build_date}`, e);
                            }
                        }
                        // 3. Fallback to modified date
                        else if (item.modified) {
                            try {
                                const date = new Date(item.modified);
                                createdDate = new Intl.DateTimeFormat('en-US', { 
                                    year: 'numeric', 
                                    month: 'short', 
                                    day: 'numeric' 
                                }).format(date);
                            } catch (e) {
                                console.warn(`Failed to format modified date: ${item.modified}`, e);
                            }
                        }
                        
                        return {
                            fileName,
                            filePath, // Use the path from API
                            fileSize: item.size_human || "Unknown",
                            createdDate,
                            version: item.version || '', // Get version from API
                            releaseType: item.release_type || 'unknown', // Get release type from API
                            parentDir: item.parent_dir || '' // Get parent directory from API
                        };
                    });
            } else {
                files = [];
                error = "Invalid response format: expected items array";
            }
        } catch (err) {
            console.error("Error loading files:", err);
            if (err instanceof Error) {
                error = `Failed to load files: ${err.message}`;
            } else {
                error = "Failed to load files: Unknown error";
            }
            files = [];
        } finally {
            loading = false;
        }
    }
    
    function handleSelect(event: CustomEvent<{ filePath: string; isSelected: boolean }>) {
        const { filePath, isSelected } = event.detail;
        
        if (isSelected) {
            if (!selectedFiles.includes(filePath)) {
                selectedFiles = [...selectedFiles, filePath];
            }
        } else {
            selectedFiles = selectedFiles.filter((path: string) => path !== filePath);
        }
    }
    
    // Handle download of a single file
    async function handleDownload(event: CustomEvent<{ filePath: string }>) {
        const { filePath } = event.detail;
        window.location.href = `/api/archives/download/${encodeURIComponent(filePath)}`;
    }
    
    // Handle batch download of selected files
    function downloadSelected() {
        // For now, just download them one by one
        // This could be enhanced to create a zip file on the server
        selectedFiles.forEach((filePath: string) => {
            window.open(`/api/archives/download/${encodeURIComponent(filePath)}`, '_blank');
        });
    }
    
    // Toggle selection of all visible files on the current page
    function selectAll(event: Event) {
        const isChecked = (event.target as HTMLInputElement).checked;
        
        if (isChecked) {
            // Add all current page files to selection
            const newPaths = paginatedFiles.map((file: FileEntry) => file.filePath);
            const uniqueSelectedFiles = new Set([...selectedFiles]);
            
            // Add each new path to the set
            newPaths.forEach((path: string) => uniqueSelectedFiles.add(path));
            
            // Convert back to array
            selectedFiles = Array.from(uniqueSelectedFiles);
        } else {
            // Remove all current page files from selection
            const paginatedPaths = new Set(paginatedFiles.map((file: FileEntry) => file.filePath));
            selectedFiles = selectedFiles.filter((path: string) => !paginatedPaths.has(path));
        }
    }
    
    // Pagination functions
    function goToPage(page: number) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
        }
    }
    
    function goToNextPage() {
        if (currentPage < totalPages) {
            currentPage += 1;
        }
    }
    
    function goToPreviousPage() {
        if (currentPage > 1) {
            currentPage -= 1;
        }
    }
    
    // Generate page numbers to display
    function getPageNumbers() {
        const maxPagesToShow = 5;
        let pages: (number | string)[] = [];
        
        // Always show first page
        pages.push(1);
        
        // Calculate range around current page
        let startPage = Math.max(2, currentPage - Math.floor((maxPagesToShow - 3) / 2));
        let endPage = Math.min(totalPages - 1, startPage + (maxPagesToShow - 4));
        
        // Adjust if we're near the end
        if (endPage < totalPages - 1) {
            if (endPage - startPage < maxPagesToShow - 4) {
                startPage = Math.max(2, endPage - (maxPagesToShow - 4));
            }
        }
        
        // Add ellipsis after first page if needed
        if (startPage > 2) {
            pages.push('...');
        }
        
        // Add pages in range
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }
        
        // Add ellipsis before last page if needed
        if (endPage < totalPages - 1) {
            pages.push('...');
        }
        
        // Always show last page if there is more than one page
        if (totalPages > 1) {
            pages.push(totalPages);
        }
        
        return pages;
    }
    
    onMount(() => {
        loadFiles();
    });
</script>

<div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
    <!-- Table header with search and actions -->
    <div class="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
        <div class="flex-1">
            <input 
                type="text" 
                placeholder="Search for update packages..." 
                bind:value={searchTerm}
                class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-med border-gray-300 rounded-md"
            />
        </div>
        
        <div class="ml-4">
            <button 
                on:click={downloadSelected}
                disabled={selectedFiles.length === 0}
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
                Download Selected
            </button>
            
            <button 
                on:click={loadFiles}
                class="ml-2 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
                Refresh
            </button>
        </div>
    </div>
    
    {#if loading}
        <div class="px-4 py-16 text-center text-gray-500">
            Loading updates...
        </div>
    {:else if error}
        <div class="px-4 py-8 text-center text-red-500">
            {error}
        </div>
    {:else if filteredFiles.length === 0}
        <div class="px-4 py-8 text-center text-gray-500">
            {searchTerm ? 'No updates matching your search' : 'No updates available'}
        </div>
    {:else}
        <!-- Table -->
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input 
                                type="checkbox" 
                                on:change={selectAll}
                                checked={allSelected}
                                disabled={filteredFiles.length === 0}
                                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            File Name
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Created Date
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Version
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Size
                        </th>
                        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {#each paginatedFiles as file (file.filePath)}
                        <Entry 
                            fileName={file.fileName}
                            filePath={file.filePath}
                            fileSize={file.fileSize}
                            createdDate={file.createdDate}
                            version={file.version}
                            releaseType={file.releaseType}
                            parentDir={file.parentDir}
                            isSelected={selectedFiles.includes(file.filePath)}
                            on:select={handleSelect}
                            on:download={handleDownload}
                        />
                    {/each}
                </tbody>
            </table>
        </div>
        
        <!-- Pagination -->
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div class="flex-1 flex justify-between sm:hidden">
                <!-- Mobile pagination -->
                <button 
                    on:click={goToPreviousPage} 
                    disabled={currentPage === 1}
                    class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                    Previous
                </button>
                <div class="text-sm text-gray-700 py-2">
                    Page {currentPage} of {totalPages}
                </div>
                <button 
                    on:click={goToNextPage} 
                    disabled={currentPage === totalPages}
                    class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                    Next
                </button>
            </div>
            
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div class="flex items-center">
                    <p class="text-sm text-gray-700 mr-4">
                        Showing <span class="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to <span class="font-medium">{Math.min(currentPage * itemsPerPage, filteredFiles.length)}</span> of <span class="font-medium">{filteredFiles.length}</span> results
                    </p>
                    
                    <div>
                        <select 
                            bind:value={itemsPerPage} 
                            on:change={() => currentPage = 1}
                            class="mt-1 block w-full pl-3 pr-10 py-1 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                            <option value={5}>5 per page</option>
                            <option value={10}>10 per page</option>
                            <option value={25}>25 per page</option>
                            <option value={50}>50 per page</option>
                        </select>
                    </div>
                </div>
                
                <div>
                    <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                        <!-- Previous Page Button -->
                        <button 
                            on:click={goToPreviousPage} 
                            disabled={currentPage === 1}
                            class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                        >
                            <span class="sr-only">Previous</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                            </svg>
                        </button>
                        
                        <!-- Page Numbers -->
                        {#each getPageNumbers() as page, i (i)}
                            {#if typeof page === 'number'}
                                <button 
                                    on:click={() => goToPage(page)}
                                    class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${currentPage === page 
                                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600' 
                                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}`}
                                >
                                    {page}
                                </button>
                            {:else}
                                <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                                    ...
                                </span>
                            {/if}
                        {/each}
                        
                        <!-- Next Page Button -->
                        <button 
                            on:click={goToNextPage} 
                            disabled={currentPage === totalPages}
                            class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                        >
                            <span class="sr-only">Next</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </nav>
                </div>
            </div>
        </div>
    {/if}
</div>