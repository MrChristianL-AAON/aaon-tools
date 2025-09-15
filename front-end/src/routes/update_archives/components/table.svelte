<script lang="ts">
    import { onMount, afterUpdate } from 'svelte';
    import { page } from '$app/stores';
    import Entry from "./entry.svelte";
    import Filter from "../../../lib/assets/filter.svg"; 
    import { RangeCalendar } from "$lib/components/ui/range-calendar";
    import { parseDate, parseDateTime, type DateValue } from '@internationalized/date';
    import { format } from 'date-fns';
    
    // Define DateRange type to match what RangeCalendar expects
    interface DateRange {
        start: DateValue;
        end: DateValue;
    }
    
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
    
    // Sorting options
    type SortField = 'fileName' | 'createdDate' | 'version' | 'releaseType' | 'fileSize';
    type SortDirection = 'asc' | 'desc';
    
    let sortField: SortField = 'createdDate'; // Default sort by created date
    let sortDirection: SortDirection = 'desc'; // Default descending order (newest first)
    
    // Filter options
    type FilterState = {
        dateRange: { start: string; end: string };
        versions: string[];
        releaseTypes: string[];
        minSize: string;
        maxSize: string;
        parentDirs: string[];
    }
    
    // Filter state
    let filters: FilterState = {
        dateRange: { start: '', end: '' },
        versions: [],
        releaseTypes: [],
        minSize: '',
        maxSize: '',
        parentDirs: []
    };
    
    // Show/hide filters UI
    let showFilters: boolean = false;

    let files: FileEntry[] = [];
    let loading: boolean = true;
    let error: string | null = null;
    let selectedFiles: string[] = [];
    let searchTerm: string = '';
    let filteredFiles: FileEntry[] = [];
    let selectedDateRange: DateRange | undefined = undefined;
    
    // Pagination variables
    let currentPage = 1;
    let itemsPerPage = 10; // Show 10 items per page
    let paginatedFiles: FileEntry[] = [];
    
    // Function to sort files
    function sortFiles(a: FileEntry, b: FileEntry): number {
        // Helper to compare version strings (e.g., "1.2.3" > "1.2.0")
        function compareVersions(versionA: string, versionB: string): number {
            if (!versionA && !versionB) return 0;
            if (!versionA) return -1;
            if (!versionB) return 1;
            
            const partsA = versionA.split('.').map(part => parseInt(part) || 0);
            const partsB = versionB.split('.').map(part => parseInt(part) || 0);
            
            for (let i = 0; i < Math.max(partsA.length, partsB.length); i++) {
                const partA = partsA[i] || 0;
                const partB = partsB[i] || 0;
                if (partA !== partB) {
                    return partA - partB;
                }
            }
            return 0;
        }
        
        // Helper to compare file sizes (e.g., "1.2 MB" > "300 KB")
        function compareFileSizes(sizeA: string, sizeB: string): number {
            // Extract number and unit
            const parseSize = (size: string): [number, string] => {
                const match = size.match(/^([\d.]+)\s*([KMGT]B|B)?$/i);
                if (!match) return [0, 'B'];
                const num = parseFloat(match[1]) || 0;
                const unit = (match[2] || 'B').toUpperCase();
                return [num, unit];
            };
            
            const [numA, unitA] = parseSize(sizeA);
            const [numB, unitB] = parseSize(sizeB);
            
            // Unit conversion factors (relative to bytes)
            const units: {[key: string]: number} = {
                'B': 1,
                'KB': 1024,
                'MB': 1024 * 1024,
                'GB': 1024 * 1024 * 1024,
                'TB': 1024 * 1024 * 1024 * 1024
            };
            
            const bytesA = numA * (units[unitA] || 1);
            const bytesB = numB * (units[unitB] || 1);
            
            return bytesA - bytesB;
        }
        
        // Helper to compare dates
        function compareDates(dateA: string, dateB: string): number {
            if (!dateA && !dateB) return 0;
            if (!dateA) return -1;
            if (!dateB) return 1;
            
            // Try to parse the dates
            try {
                const timeA = new Date(dateA).getTime();
                const timeB = new Date(dateB).getTime();
                
                if (isNaN(timeA) && isNaN(timeB)) return 0;
                if (isNaN(timeA)) return -1;
                if (isNaN(timeB)) return 1;
                
                return timeA - timeB;
            } catch (e) {
                // If parsing fails, compare as strings
                return dateA.localeCompare(dateB);
            }
        }
        
        let result = 0;
        
        // Sort based on the selected field
        switch (sortField) {
            case 'fileName':
                result = a.fileName.localeCompare(b.fileName);
                break;
            case 'createdDate':
                result = compareDates(a.createdDate, b.createdDate);
                break;
            case 'version':
                result = compareVersions(a.version || '', b.version || '');
                break;
            case 'releaseType':
                result = (a.releaseType || '').localeCompare(b.releaseType || '');
                break;
            case 'fileSize':
                result = compareFileSizes(a.fileSize, b.fileSize);
                break;
            default:
                result = 0;
        }
        
        // Apply sort direction
        return sortDirection === 'asc' ? result : -result;
    }
    
    // Change sort field and direction
    function changeSort(field: SortField) {
        if (field === sortField) {
            // Toggle direction if clicking the same field
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            // Set new field and default to ascending
            sortField = field;
            sortDirection = 'asc';
        }
        
        // Reset to first page after changing sort
        currentPage = 1;
        
        // Automatically refresh the file list to get the latest data
        // This ensures we have the most up-to-date information when sorting
        loadFiles();
        
        // Force a re-render by creating a new array reference
        // This ensures the reactive statement for filteredFiles runs
        files = [...files];
    }
    
    // Get sort indicator symbol and classes
    function getSortIndicator(field: SortField): string {
        if (field !== sortField) return '';
        return sortDirection === 'asc' ? '▲' : '▼'; // ▲ for ascending (up), ▼ for descending (down)
    }
    
    function getSortHeaderClass(field: SortField): string {
        const baseClass = "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider cursor-pointer hover:bg-gray-100";
        if (field === sortField) {
            return `${baseClass} text-aaon-blue font-bold`;
        }
        return `${baseClass} text-gray-500`;
    }
    
    // Parse file size to bytes for comparison
    function parseFileSize(size: string): number {
        const match = size.match(/^([\d.]+)\s*([KMGT]B|B)?$/i);
        if (!match) return 0;
        
        const num = parseFloat(match[1]) || 0;
        const unit = (match[2] || 'B').toUpperCase();
        
        // Unit conversion factors (relative to bytes)
        const units: {[key: string]: number} = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
            'TB': 1024 * 1024 * 1024 * 1024
        };
        
        return num * (units[unit] || 1);
    }
    
    // Extract unique values from files for filter options
    function getUniqueValues(field: keyof FileEntry): string[] {
        const values = new Set<string>();
        
        files.forEach(file => {
            const value = file[field];
            if (value && typeof value === 'string') {
                values.add(value);
            }
        });
        
        return Array.from(values).sort();
    }
    
    $: availableVersions = getUniqueValues('version');
    // Static release types instead of dynamically generated ones
    const availableReleaseTypes = ['development', 'public'];
    $: availableParentDirs = getUniqueValues('parentDir');
    
    // React to changes in the selectedDateRange
    $: {
        if (selectedDateRange !== undefined) {
            handleDateRangeChange(selectedDateRange);
        }
    }
    
    // Handle date range change from the calendar
    function handleDateRangeChange(dateRange: DateRange | undefined) {
        selectedDateRange = dateRange;
        
        if (dateRange) {
            // Convert start date to ISO string if available
            if (dateRange.start) {
                const startDate = dateRange.start.toDate('UTC');
                filters.dateRange.start = startDate.toISOString().split('T')[0];
            } else {
                filters.dateRange.start = '';
            }
            
            // Convert end date to ISO string if available
            if (dateRange.end) {
                const endDate = dateRange.end.toDate('UTC');
                filters.dateRange.end = endDate.toISOString().split('T')[0];
            } else {
                filters.dateRange.end = '';
            }
        } else {
            // Reset date range when cleared
            filters.dateRange = { start: '', end: '' };
        }
    }
    
    // Convert current filter dates to DateRangeValue
    function initializeDateRangeFromFilters() {
        if (filters.dateRange.start || filters.dateRange.end) {
            const start = filters.dateRange.start ? parseDate(filters.dateRange.start) : undefined;
            const end = filters.dateRange.end ? parseDate(filters.dateRange.end) : undefined;
            
            if (start || end) {
                if (start && end) {
                    selectedDateRange = { start, end };
                } else if (start) {
                    selectedDateRange = { start, end: start };
                } else if (end) {
                    selectedDateRange = { start: end, end };
                }
            }
        } else {
            selectedDateRange = undefined;
        }
    }
    
    // Reset filters
    function resetFilters() {
        // Reset selected date range
        selectedDateRange = undefined;
        
        filters = {
            dateRange: { start: '', end: '' },
            versions: [],
            releaseTypes: [],
            minSize: '',
            maxSize: '',
            parentDirs: []
        };
        
        // Reset to first page
        currentPage = 1;
    }
    
    // Toggle filter value selection
    function toggleFilter(array: string[], value: string): string[] {
        const index = array.indexOf(value);
        if (index === -1) {
            return [...array, value];
        } else {
            return array.filter(v => v !== value);
        }
    }
    
    // Derived state for filtered files with all filters applied
    $: filteredFiles = files.filter((file: FileEntry) => {
        // Text search filter
        if (searchTerm && !file.fileName.toLowerCase().includes(searchTerm.toLowerCase())) {
            return false;
        }
        
        // Date range filter
        if (filters.dateRange.start || filters.dateRange.end) {
            try {
                const fileDate = new Date(file.createdDate).getTime();
                
                if (filters.dateRange.start) {
                    const startDate = new Date(filters.dateRange.start).getTime();
                    if (fileDate < startDate) return false;
                }
                
                if (filters.dateRange.end) {
                    const endDate = new Date(filters.dateRange.end).getTime();
                    if (fileDate > endDate) return false;
                }
            } catch (e) {
                // If date parsing fails, don't filter
            }
        }
        
        // Version filter
        if (filters.versions.length > 0 && file.version) {
            if (!filters.versions.includes(file.version)) return false;
        }
        
        // Release type filter
        if (filters.releaseTypes.length > 0 && file.releaseType) {
            if (!filters.releaseTypes.includes(file.releaseType)) return false;
        }
        
        // Parent directory filter
        if (filters.parentDirs.length > 0 && file.parentDir) {
            if (!filters.parentDirs.includes(file.parentDir)) return false;
        }
        
        return true;
    });
    
    // Create a reactive variable that changes when sort parameters change
    $: sortKey = `${sortField}-${sortDirection}`;
    
    // This ensures the UI updates when sort parameters change
    $: {
        // Force reactivity when sort parameters change
        const _ = sortKey;
    }
    
    // Reset to first page when filter changes
    $: {
        if (searchTerm) {
            currentPage = 1;
        }
    }
    
    // Reset to first page when any filter changes
    $: {
        const filterValues = JSON.stringify(filters);
        if (filterValues) {
            currentPage = 1;
        }
    }
    
    // Calculate total number of pages
    $: totalPages = Math.max(1, Math.ceil(filteredFiles.length / itemsPerPage));
    
    // Ensure current page is valid and recalculate when itemsPerPage changes
    $: {
        if (currentPage > totalPages) {
            currentPage = totalPages;
        }
    }
    
    // Update pagination when itemsPerPage changes
    $: {
        // This reactive statement ensures totalPages is recalculated when itemsPerPage changes
        const calculatedPages = Math.max(1, Math.ceil(filteredFiles.length / itemsPerPage));
        if (calculatedPages !== totalPages) {
            // Page count has changed due to itemsPerPage change
            currentPage = Math.min(currentPage, calculatedPages);
        }
    }
    
    // Recompute sorted and filtered files when sort parameters change
    $: sortedFilteredFiles = [...filteredFiles].sort(sortFiles);
    
    // Get current page's files
    $: paginatedFiles = sortedFilteredFiles.slice(
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
                            // Map release type to either development or public
                            releaseType: item.release_type === 'public' ? 'public' : 'development',
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
        // Create a container for the download iframes if it doesn't exist
        let downloadContainer = document.getElementById('download-container');
        if (!downloadContainer) {
            downloadContainer = document.createElement('div');
            downloadContainer.id = 'download-container';
            downloadContainer.style.display = 'none';
            document.body.appendChild(downloadContainer);
        } else {
            // Clear existing iframes
            downloadContainer.innerHTML = '';
        }
        
        // Create a hidden iframe for each file to download
        selectedFiles.forEach((filePath: string, index) => {
            // Create a delay to avoid overwhelming the browser
            setTimeout(() => {
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = `/api/archives/download/${encodeURIComponent(filePath)}`;
                iframe.onload = () => {
                    // Remove the iframe after a short delay to ensure the download starts
                    setTimeout(() => {
                        try {
                            iframe.remove();
                        } catch (e) {
                            console.error('Error removing iframe:', e);
                        }
                    }, 5000);
                };
                
                downloadContainer.appendChild(iframe);
            }, index * 500); // 500ms delay between each download to prevent overwhelming the browser
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
        
        // For small number of pages, just show all page numbers
        if (totalPages <= maxPagesToShow) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
            return pages;
        }
        
        // For larger sets, show first page
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
    
    // Variable to track if this is the initial load
    let initialLoad = true;
    
    // Reactive statement to track URL changes through the page store
    // This will reload files when navigating back to this page
    $: {
        if ($page && !initialLoad) {
            // The $page store changed - we're either navigating to this page
            // or it's being refreshed - reload the files
            loadFiles();
        }
    }
    
    onMount(() => {
        // Initial load when component is mounted
        loadFiles();
        initialLoad = false;
        
        // Initialize the date range from any existing filter values
        initializeDateRangeFromFilters();
    });
    
    // Define a function to handle manual refresh when needed
    function handleRefresh() {
        loadFiles();
    }
    
    // Add a keyboard shortcut for F5 to reload data without full page reload
    function handleKeyDown(event: KeyboardEvent) {
        // Check if F5 was pressed (keyCode 116)
        if (event.key === 'F5') {
            // Prevent the default browser refresh
            event.preventDefault();
            // Reload the data
            loadFiles();
        }
    }
</script>

<svelte:window on:keydown={handleKeyDown} />

<div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
    <!-- Table header with search and date range -->
    <div class="px-4 py-5 sm:px-6">
        <div class="flex justify-between items-center mb-4">
            <!-- Search box with magnifying glass icon -->
            <div class="relative w-full md:w-1/2 lg:w-1/3">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                    </svg>
                </div>
                <input 
                    type="text" 
                    placeholder="Search Package IDs " 
                    bind:value={searchTerm}
                    class="pl-10 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white py-2 focus:ring-blue-500 focus:border-blue-500 block w-full"
                />
            </div>
            
            <!-- Action buttons -->
            <div class="flex items-center">
                <!-- Date Filter Badge - Only shown when active -->
                {#if filters.dateRange.start || filters.dateRange.end}
                    <div class="mr-2">
                        <button 
                            on:click={() => showFilters = !showFilters}
                            class="inline-flex items-center px-4 py-2 border border-aaon-blue-light shadow-sm text-sm font-medium rounded-md text-aaon-blue bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            aria-label="Edit date filter"
                        >
                            <span>
                                {#if filters.dateRange.start && filters.dateRange.end}
                                    {format(new Date(filters.dateRange.start), 'MMM d, yyyy')} - {format(new Date(filters.dateRange.end), 'MMM d, yyyy')}
                                {:else if filters.dateRange.start}
                                    From {format(new Date(filters.dateRange.start), 'MMM d, yyyy')}
                                {:else}
                                    Until {format(new Date(filters.dateRange.end), 'MMM d, yyyy')}
                                {/if}
                            </span>
                            <svg class="ml-2 h-5 w-5 text-aaon-blue" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                {/if}
                
                <!-- Type Filter Badge - Only shown when active -->
                {#if filters.releaseTypes.length > 0}
                    <div class="mr-2">
                        <button 
                            on:click={() => showFilters = !showFilters}
                            class="inline-flex items-center px-4 py-2 border border-aaon-blue-light shadow-sm text-sm font-medium rounded-md text-aaon-blue bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            aria-label="Edit type filter"
                        >
                            <span>Release Types: {filters.releaseTypes} </span>
                            <svg class="ml-2 h-5 w-5 text-aaon-blue" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                {/if}
                
                <!-- Filters Toggle Button -->
                <div class="relative">
                    <button 
                        on:click={() => showFilters = !showFilters}
                        class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        aria-label="Toggle filters panel"
                    >
                        <span>Filters</span>
                        <img class="ml-2 h-5 w-5 text-aaon-blue"
                             src={Filter} alt="" />
                    </button>
                </div>
                
                <div class="ml-2">
                    <button 
                        on:click={downloadSelected}
                        disabled={selectedFiles.length === 0}
                        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-aaon-blue-light hover:bg-aaon-blue hover:cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Download selected files"
                    >
                        Download Selected
                    </button>
                </div>
                
                <!-- Refresh Button -->
                <div class="ml-2">
                    <button 
                        on:click={loadFiles}
                        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        aria-label="Refresh file list"
                    >
                        <svg class="mr-1.5 h-4 w-4 text-aaon-blue" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                        </svg>
                        Refresh
                    </button>
                </div>
            </div>
        </div>
        
        {#if showFilters}
            <div class="mt-4 p-4 bg-gray-50 rounded-md border border-gray-200">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Filter Options</h3>
                    <button 
                        on:click={resetFilters}
                        class="text-sm text-aaon-blue-light hover:text-aaon-blue"
                        aria-label="Reset all filters"
                    >
                        Reset All Filters
                    </button>
                </div>
                
                <div class="flex flex-wrap gap-4">
                    <div class="flex flex-wrap gap-4">
                        <!-- Date Range -->
                        <div class="space-y-2 min-w-[260px]">
                            <span class="block text-sm font-medium text-gray-700">Date Range</span>
                            <div class="bg-white border border-gray-200 rounded-md p-1 overflow-hidden max-w-[260px]">
                                <RangeCalendar 
                                    bind:value={selectedDateRange}
                                    class="w-full scale-90 origin-top-left -mb-6"
                                />
                            </div>
                            {#if filters.dateRange.start || filters.dateRange.end}
                                <div class="flex justify-left">
                                    <button 
                                        on:click={() => handleDateRangeChange(undefined)}
                                        class="text-xs text-aaon-blue-light hover:text-aaon-blue hover:underline hover:cursor-pointer"
                                    >
                                        Clear Date Range
                                    </button>
                                </div>
                            {/if}
                        </div>
                        
                        <!-- Release Types - Directly adjacent to Date Range -->
                        <div class="space-y-2 align-self-start">
                        <span class="block text-sm font-medium text-gray-700">Release Type</span>
                        <div class="max-h-32 overflow-y-auto border border-gray-200 rounded-md">
                            {#if availableReleaseTypes.length === 0}
                                <div class="p-2 text-sm text-gray-500">No types available</div>
                            {:else}
                                {#each availableReleaseTypes as type}
                                    <div class="flex items-center p-2 hover:bg-gray-100">
                                        <input 
                                            type="checkbox" 
                                            id={`type-${type}`}
                                            checked={filters.releaseTypes.includes(type)}
                                            on:change={() => filters.releaseTypes = toggleFilter(filters.releaseTypes, type)}
                                            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                        />
                                        <label for={`type-${type}`} class="ml-2 block text-sm">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                {type === 'development' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}">
                                                {type}
                                            </span>
                                        </label>
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    </div>
                    
                    </div>
                    
                    <!-- Parent Directories -->
                    {#if availableParentDirs.length > 0}
                        <div class="space-y-2 flex-grow">
                            <span class="block text-sm font-medium text-gray-700">Parent Directory</span>
                            <div class="max-h-32 overflow-y-auto border border-gray-200 rounded-md">
                                <div class="grid grid-cols-2 lg:grid-cols-3">
                                    {#each availableParentDirs as dir}
                                        <div class="flex items-center p-2 hover:bg-gray-100">
                                            <input 
                                                type="checkbox" 
                                                id={`dir-${dir}`}
                                                checked={filters.parentDirs.includes(dir)}
                                                on:change={() => filters.parentDirs = toggleFilter(filters.parentDirs, dir)}
                                                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                            />
                                            <label for={`dir-${dir}`} class="ml-2 block text-sm text-gray-900 truncate">{dir}</label>
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        </div>
                    {/if}
                </div>
                
                <!-- Filter summary -->
                <div class="mt-4 pt-3 border-t border-gray-200">
                    <div class="flex flex-wrap gap-2">
                        <span class="text-sm text-gray-500">
                            Showing {filteredFiles.length} of {files.length} updates
                        </span>
                        
                        {#if filters.dateRange.start || filters.dateRange.end}
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                Date: {filters.dateRange.start ? format(new Date(filters.dateRange.start), 'MMM d, yyyy') : 'Any'} - 
                                {filters.dateRange.end ? format(new Date(filters.dateRange.end), 'MMM d, yyyy') : 'Any'}
                            </span>
                        {/if}
                        
                        
                        {#if filters.releaseTypes.length > 0}
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                Release Types: {filters.releaseTypes.length} selected
                            </span>
                        {/if}
                        
                        {#if filters.parentDirs.length > 0}
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                Directories: {filters.parentDirs.length} selected
                            </span>
                        {/if}
                    </div>
                </div>
            </div>
        {/if}
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
                        <th scope="col" class="px-8 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input 
                                type="checkbox" 
                                on:change={selectAll}
                                checked={allSelected}
                                disabled={filteredFiles.length === 0}
                                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                        </th>
                        <th scope="col" 
                            class={getSortHeaderClass('fileName')}
                            on:click={() => changeSort('fileName')}
                        >
                            Package ID <span class="ml-1">{getSortIndicator('fileName')}</span>
                        </th>
                        <th scope="col" 
                            class={getSortHeaderClass('createdDate')}
                            on:click={() => changeSort('createdDate')}
                        >
                            Created On <span class="ml-1">{getSortIndicator('createdDate')}</span>
                        </th>
                        <th scope="col" 
                            class={getSortHeaderClass('version')}
                            on:click={() => changeSort('version')}
                        >
                            Version <span class="ml-1">{getSortIndicator('version')}</span>
                        </th>
                        <th scope="col" 
                            class={getSortHeaderClass('releaseType')}
                            on:click={() => changeSort('releaseType')}
                        >
                            Release Type <span class="ml-1">{getSortIndicator('releaseType')}</span>
                        </th>
                        <th scope="col" 
                            class={getSortHeaderClass('fileSize')}
                            on:click={() => changeSort('fileSize')}
                        >
                            File Size <span class="ml-1">{getSortIndicator('fileSize')}</span>
                        </th>
                        <th scope="col" class="px-7 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                            on:change={() => {
                                // Reset to first page and let the reactive statements handle recalculation
                                currentPage = 1;
                                // Force Svelte to update derived values
                                itemsPerPage = itemsPerPage;
                            }}
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