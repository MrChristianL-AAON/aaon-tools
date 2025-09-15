<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    // Props for the file entry
    export let fileName = '';
    export let filePath = '';
    export let fileSize = '';
    export let createdDate = '';
    
    // Optional props with defaults
    export let isSelected = false;
    export let version = '';
    export let releaseType = 'unknown';
    export let parentDir = '';
    
    // Fallback to parsing from filename if version not provided
    $: {
        if (!version) {
            version = fileName.match(/V(\d+\.\d+\.\d+[A-Z]?)_/)?.[1] || '';
        }
        if (releaseType === 'unknown') {
            releaseType = fileName.includes('_D_') ? 'development' : 'public';
        }
    }
    
    const dispatch = createEventDispatcher();
    
    function handleSelect(e: Event) {
        const target = e.target as HTMLInputElement;
        isSelected = target.checked;
        dispatch('select', { filePath, isSelected });
    }
    
    function handleDownload() {
        dispatch('download', { filePath });
    }
</script>

<tr class="hover:bg-gray-100">
    <!-- Checkbox column -->
    <td class="px-4 py-4 whitespace-nowrap">
        <input 
            type="checkbox" 
            checked={isSelected}
            on:change={handleSelect}
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
    </td>
    
    <!-- File name column -->
    <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm font-medium text-gray-900">{fileName}</div>
    </td>
    
    <!-- Created date column -->
    <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm text-gray-500">{createdDate}</div>
    </td>
    
    <!-- Version column -->
    <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm text-gray-500">{version}</div>
    </td>
    
    <!-- Release type column -->
    <td class="px-6 py-4 whitespace-nowrap">
        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
            {releaseType === 'development' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}">
            {releaseType}
        </span>
    </td>
    
    <!-- File size column -->
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {fileSize}
    </td>
    
    <!-- Actions column -->
    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button 
            on:click={handleDownload}
            class="text-blue-600 hover:text-blue-900"
        >
            Download
        </button>
    </td>
</tr>